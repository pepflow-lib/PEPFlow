"""Insert B2 evidence and execute the evolving notebook."""
import hashlib
import json
import os
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / 'supplementary' / '.runtime'
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
for key in ('TEMP', 'TMP', 'TMPDIR', 'MPLCONFIGDIR', 'IPYTHONDIR', 'JUPYTER_RUNTIME_DIR', 'JUPYTER_CONFIG_DIR', 'XDG_CACHE_HOME'):
    p = runtime / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
os.environ['JUPYTER_PATH'] = str(runtime / 'jupyter')
kernel = runtime / 'jupyter' / 'kernels' / 'dual-feg-owned'
kernel.mkdir(parents=True, exist_ok=True)
(kernel / 'kernel.json').write_text(json.dumps({'argv': [sys.executable, '-I', '-B', '-m', 'ipykernel_launcher', '-f', '{connection_file}'], 'display_name': 'Dual FEG private kernel', 'language': 'python'}))
path = ROOT / 'dual_feg_example_lyap.ipynb'
nb = nbformat.read(path, as_version=4)
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
new_cells = [md(r'''## Dense and relaxed proof solves
At $N=6$, the dense solve and both sparsity tests use CLARABEL defaults. The first test drops multipliers below $10^{-6}$. Because $x_{N-1/2}=x_N$, redundant final evaluation constraints yield nonunique coefficients. The selected pattern retains monotonicity between $x_{k+1/2}$ and $x_N$ for $k<N-1$, terminal-root monotonicity, and Lipschitz inequalities between $x_k$ and $x_{k+1/2}$ (using the terminal point at the last step). Each saved certificate contains all retained multipliers and its own $S$ from the same solve.
'''), code('''dense_summary = json.loads((notebook_dir / 'state' / 'dual_feg_dense.json').read_text())
threshold_summary = json.loads((notebook_dir / 'supplementary' / 'b2-selected-raw.json').read_text())
sparse_summary = json.loads((notebook_dir / 'supplementary' / 'b2-selected-structural.json').read_text())
for name, sample in [('dense', dense_summary), ('threshold', threshold_summary), ('structural', sparse_summary)]:
    print(name, 'bound:', sample['opt_value'], 'solver:', sample['certificate_provenance']['solver'])
    for group in sample['lambda_groups']:
        active = [(key, val) for key, val in sample['named_dual_values'].items()
                  if val is not None and abs(val)>1e-6 and sample['constraint_metadata'][key]['group']==group]
        print(group, 'active count:', len(active))
        print(active)
    print('S rank at absolute tolerance 1e-4:', np.linalg.matrix_rank(np.array(sample['S_matrix']), tol=1e-4))
print('Basis:', sparse_summary['basis_vectors'])
print('Dense-to-selected bound difference:', abs(dense_summary['opt_value']-sparse_summary['opt_value']))
'''), md(r'''## Lambda and S verification
For normalized $L=R=1$, the initial search suggests $\tau=4/N^2$, terminal-root multiplier $4/N$, half-step-to-terminal monotonicity multipliers $4/[(N-k)(N-k-1)]$ for $k<N-1$, and within-step Lipschitz multipliers $2/(N-k)^2$. The candidate remainder is
$$S_{\mathrm{guess}}=\left\|\frac{2}{N}(x_0-x_\star)-A(x_N)\right\|^2.$$
These formulas are **fixed-sample candidates**, not an all-horizon analytic proof. The authoritative handoff retains the original numerical multipliers and remainder. Reverse LDL retains every factor and off-diagonal block, with a reconstruction check. The complete identity checked below is
$$\|A(x_N)\|^2-\mathrm{bound}-\sum_i\lambda_i R_i+S=0,$$
where every scalar residual is normalized as $R_i\leq0$. Nonnegative multipliers and $S\succeq0$ establish the numerical certificate direction. No PSD constraint families or function-value terms occur for this setup; their absence is checked explicitly. Analytic full-PEP and Lyapunov proof statuses remain false.
'''), code((ROOT / 'supplementary' / 'b2_verification_core.py').read_text())]
for i, cell in enumerate(new_cells):
    cell.id = f'b2-{i:02d}'
    if cell.cell_type == 'markdown':
        assert not any(c in cell.source for c in ('\x0c', '\r', '\x08'))
        assert '\\(' not in cell.source and '\\[' not in cell.source
nb.cells = [c for c in nb.cells if c.id not in {'b1-11', 'b1-12'} and not c.id.startswith('b2-')]
nb.cells[11:11] = new_cells
nbformat.write(nb, path)
NotebookClient(nb, timeout=120, kernel_name='dual-feg-owned', resources={'metadata': {'path': str(ROOT)}}).execute()
nbformat.write(nb, path)
for cell in new_cells:
    for out in cell.get('outputs', []):
        if out.output_type == 'stream':
            print(out.text)
checkpath = ROOT / 'supplementary' / 'dual_feg_example_lyap_checklist.md'
lines = checkpath.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith('Last reviewed block:'):
        lines[i] = 'Last reviewed block: B2'
    elif line.startswith('SHA-256:'):
        lines[i] = 'SHA-256: ' + hashlib.sha256(path.read_bytes()).hexdigest()
    elif line.startswith('| 7.'):
        lines[i] = '| 7. dense and relaxed proof solves | verified | b2-00,b2-01 | Saved distinct solve evidence, all groups summarized, relaxation and preserved bound checked. |'
    elif line.startswith('| 8.'):
        lines[i] = '| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | b2-02,b2-03 | Full numerical identity, signs, S reconstruction, labeled matrices, candidate checks, and explicit unresolved arbitrary-horizon status. |'
checkpath.write_text('\n'.join(lines), encoding='utf-8')
print('B2 notebook execution passed.')
