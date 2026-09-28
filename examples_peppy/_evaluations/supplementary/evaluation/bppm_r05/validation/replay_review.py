"""Read-only replay of submitted mathematical cells, without plotting or solving."""
from pathlib import Path
import os
import json
import hashlib
import contextlib
import datetime

root = Path.cwd().resolve()
assert root.name == 'validation' and root.parent.name == 'bppm_r05'
runtime = root / 'review_runtime'
for key in ('TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','JUPYTER_DATA_DIR','XDG_CACHE_HOME'):
    path = runtime / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
os.environ['MPLBACKEND'] = 'Agg'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
settings = json.loads((root.parent / 'settings.json').read_text())
original = Path(settings['original_submission'])
hash_checks = {}
for name, expected in settings['submission_hashes'].items():
    actual = hashlib.sha256((original / name).read_bytes()).hexdigest()
    assert actual == expected, name
    if (root / name).exists():
        copy = hashlib.sha256((root / name).read_bytes()).hexdigest()
        assert copy == expected, name
    hash_checks[name] = True
nb = json.loads((root / 'bppm_example_lyap.ipynb').read_text())
scope = {'__name__': '__review_replay__'}
executed = []
with (root / 'review_replay.log').open('w', encoding='utf-8') as log, contextlib.redirect_stdout(log):
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
        source = ''.join(cell['source'])
        if cell['id'] == '395c40ef':
            source = source.split('plt.figure')[0]
        print('CELL', cell['id'])
        exec(compile(source, 'submitted#' + cell['id'], 'exec'), scope)
        executed.append(cell['id'])
    # Rebuild the N=6 grouping using precisely the same submitted recipe,
    # rather than relying on the saved second-horizon flags/matrices.
    scope['ctx'], scope['pb'], scope['obj'] = scope['get_pep_setup'](6, scope['params'])
    scope['certificate'] = scope['b2_n6']
    scope['N_int'] = 6
    scope['pb'].set_relaxed_constraints(scope['certificate']['relaxed_constraints'])
    for name in ('certificate_check', 'decomposition', 'grouping'):
        source = (root / f'supplementary/b3_{name}.py').read_text()
        exec(compile(source, f'submitted-b3-{name}', 'exec'), scope)
    sample = next(s for s in scope['rank_evidence']['samples'] if s['N'] == 6)
    np = scope['np']
    n6_component_errors = []
    for k, value in enumerate(scope['lyap']):
        coords = scope['pm'].eval_scalar(value)
        for current, saved in ((coords.inner_prod_coords, sample['lyap_inner_prod_coords'][k]),
                               (coords.func_coords, sample['lyap_func_coords'][k]),
                               (coords.offset, sample['lyap_offsets'][k])):
            error = float(np.max(np.abs(np.asarray(current, dtype=float) - np.asarray(saved)), initial=0))
            assert error <= 1e-5
            n6_component_errors.append(error)
summary = {
    'verification': 'Fresh isolated Python replay of all 31 submitted code cells; plotting lines omitted, no solver rerun, no notebook rendering. N=6 grouping independently replayed from submitted code.',
    'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'original_and_validation_hashes_match': all(hash_checks.values()),
    'hash_count': len(hash_checks),
    'executed_cells': executed,
    'b1_sweep': [{'N': r['N'], 'opt_value': r['opt_value'], 'status': r['attempts'][-1]['status'], 'error': r['absolute_error']} for r in scope['rows']],
    'b2_N4_checks': scope['b2']['numerical_checks'],
    'b2_N6_fresh_checks': scope['checks'],
    'b3_N6_fresh_ranks': scope['ranks'],
    'b3_N6_fresh_coverage': scope['coverage_residuals'],
    'b3_N6_saved_coordinate_max_error': max(n6_component_errors),
    'b3_N6_rank_credible': bool(scope['rank_credible']),
    'b4_quadratic_residuals': scope['coefficient_residuals'],
    'b4_complete_residuals': scope['component_residuals'],
    'b5_exact_results': scope['exact_results'],
    'b5_checks': scope['proof_checks'],
}
(root / 'review_replay.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
