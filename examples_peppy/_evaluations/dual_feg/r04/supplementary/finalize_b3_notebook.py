"""Finalize B3 with visible same-recipe replay at N=6 and N=8."""
import hashlib
import os
from pathlib import Path
import textwrap

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / 'supplementary/.runtime'
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
for key in ('TEMP', 'TMP', 'TMPDIR', 'MPLCONFIGDIR', 'IPYTHONDIR', 'JUPYTER_RUNTIME_DIR', 'JUPYTER_CONFIG_DIR', 'XDG_CACHE_HOME'):
    p = runtime / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
os.environ['JUPYTER_PATH'] = str(runtime / 'jupyter')
source_names = ('b3_certificate_check.py', 'b3_decomposition.py', 'b3_grouping.py')
sources = [(ROOT / 'supplementary' / name).read_text() for name in source_names]
intro = '''N_int = certificate['N_verify']
params_sp = {name: sp.S(value) for name, value in json.loads(certificate['params_json']).items()}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
'''
# Move function-local imports before the first executable statement.
imports = '\n'.join(line for line in sources[0].splitlines() if line.startswith(('import ', 'from ')))
check_without_imports = '\n'.join(line for line in sources[0].splitlines() if not line.startswith(('import ', 'from ')))
tail = '''
observation = {'N': N_int, 'certificate_id': certificate['certificate_id'],
    'recipe_id': 'terminal-star-step-pairs-S-boundary', 'rank_profile': ranks,
    'singular_values': singular_values,
    'rank_convention': {'absolute_tolerance': 1e-4, 'scaling': 'none; L=R=1', 'coordinate_order': 'setup basis order'},
    'certificate_checked': certificate_checked, 'grouping_checked': grouping_checked,
    'rank_credible': all(not any(0.5e-4 < s < 2e-4 for s in row) for row in singular_values),
    'coverage_max_abs': max(coverage_residuals)}
evaluated_lyap = [pm.eval_scalar(Vk) for Vk in lyap]
data = {'lyap_inner_prod_coords': [np.asarray(v.inner_prod_coords, dtype=float).tolist() for v in evaluated_lyap],
        'lyap_func_coords': [np.asarray(v.func_coords, dtype=float).tolist() for v in evaluated_lyap],
        'lyap_offsets': [float(v.offset) for v in evaluated_lyap],
        'grouping_coverage': {'constraint_assignment': term_assignment, 'S_assignment': S_assignment,
            'normalization_constraint': tau_name, 'boundary_constraints': boundary_names,
            'boundary_S': boundary_S, 'omitted_constraints': [], 'checked': grouping_checked},
        'extra_duals': extra_duals}
return observation, data
'''
function_source = 'def evaluate_rank_sample(certificate):\n' + textwrap.indent(imports + '\n' + intro + '\n' + check_without_imports + '\n' + sources[1] + '\n' + sources[2] + tail, '    ')
(ROOT / 'supplementary/b3_rank_function.py').write_text(function_source)
comparison = '''REPO_ROOT = repo_root
main_certificate = json.loads((notebook_dir / 'state/dual_feg_b2.json').read_text())
extra_certificate = json.loads((notebook_dir / 'supplementary/n8/dual_feg_b2.json').read_text())
rank_samples = []
print('Selected N=6 sample:')
main_observation, main_partial_sums = evaluate_rank_sample(main_certificate)
rank_samples.append(main_observation)
print('Confirming N=8 sample:')
extra_observation, extra_partial_sums = evaluate_rank_sample(extra_certificate)
rank_samples.append(extra_observation)
assert len({sample['N'] for sample in rank_samples}) == 2
assert all(sample['certificate_checked'] and sample['grouping_checked'] and sample['rank_credible'] for sample in rank_samples)
assert all(sample['rank_convention'] == rank_samples[0]['rank_convention'] for sample in rank_samples)
assert all(sample['recipe_id'] == rank_samples[0]['recipe_id'] for sample in rank_samples)
retained = [sample['rank_profile'][1:sample['N']] for sample in rank_samples]
assert all(len(profile) >= 3 and set(profile) == {4} for profile in retained)
rank_search = {'status': 'confirmed', 'boundary_exclusions': {'left': 1, 'right': 1}, 'rank': 4,
    'confirmed_horizons': [6, 8], 'selected_certificate_id': main_certificate['certificate_id'],
    'recipe_id': main_observation['recipe_id'], 'rank_convention': main_observation['rank_convention'],
    'unresolved_samples': [], 'evidence_path': 'supplementary/rank_search.json'}
print('Confirmed interior rank:', 4, 'at horizons:', [6, 8], 'fixed exclusions:', (1, 1), 'absolute tolerance:', 1e-4)
print('Every N=6 and N=8 retained singular value is outside the ambiguity band [0.5e-4,2e-4].')
source_names = ['b3_certificate_check.py', 'b3_decomposition.py', 'b3_grouping.py']
source_text = [(notebook_dir / 'supplementary' / name).read_text() for name in source_names]
b3_state = {**main_certificate, **main_partial_sums, 'rank_profile': main_observation['rank_profile'],
    'rank_search': rank_search, 'certificate_check_code': source_text[0], 'decomposition_code': source_text[1],
    'grouping_code': source_text[2], 'rank_tolerance': 1e-4, 'reconstruction_tolerance': 1e-4,
    'reconstruction_rtol': 1e-5, 'numerical_certificate_verified': True,
    'analytic_full_pep_verified': False, 'lyapunov_proof_verified': False}
(notebook_dir / 'supplementary/rank_search.json').write_text(json.dumps({'summary': rank_search, 'samples': rank_samples}, indent=2, allow_nan=False))
(notebook_dir / 'state/dual_feg_b3.json').write_text(json.dumps(b3_state, indent=2, allow_nan=False))
'''
(ROOT / 'supplementary/b3_comparison.py').write_text(comparison)
path = ROOT / 'dual_feg_example_lyap.ipynb'
nb = nbformat.read(path, as_version=4)
old_md = next(c.source for c in nb.cells if c.id == 'b3-00')
old_md = old_md.replace('A second horizon remains required before B3 can be complete.', 'The same construction independently gives rank four at $N=8$. Both samples pass full-coordinate coverage; this is finite-sample structural evidence, not an arbitrary-horizon proof.')
cells = [nbformat.v4.new_markdown_cell(old_md), nbformat.v4.new_code_cell(function_source), nbformat.v4.new_code_cell(comparison)]
for i, cell in enumerate(cells):
    cell.id = f'b3-{i:02d}'
nb.cells = [c for c in nb.cells if not c.id.startswith('b3-')]
index = next(i for i, c in enumerate(nb.cells) if c.id == 'b1-14')
nb.cells[index:index] = cells
nbformat.write(nb, path)
NotebookClient(nb, timeout=120, kernel_name='dual-feg-owned', resources={'metadata': {'path': str(ROOT)}}).execute()
nbformat.write(nb, path)
for cell in cells:
    for out in cell.get('outputs', []):
        if out.output_type == 'stream':
            print(out.text)
checkpath = ROOT / 'supplementary/dual_feg_example_lyap_checklist.md'
lines = checkpath.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith('Last reviewed block:'):
        lines[i] = 'Last reviewed block: B3'
    elif line.startswith('SHA-256:'):
        lines[i] = 'SHA-256: ' + hashlib.sha256(path.read_bytes()).hexdigest()
    elif line.startswith('| 9.'):
        lines[i] = '| 9. partial-sum Lyapunov construction and rank profile | verified | b3-00,b3-01,b3-02 | Both complete certificates replayed; same-recipe rank four confirmed at N=6,8 with fixed exclusions; all components and boundary coverage checked. |'
checkpath.write_text('\n'.join(lines), encoding='utf-8')
print('B3 complete; selected sample remains N=6.')
