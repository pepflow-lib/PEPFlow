"""Test terminal-star sparsity and simple horizon-dependent coefficients."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
for key in ('TEMP', 'TMP', 'TMPDIR', 'MPLCONFIGDIR', 'IPYTHONDIR', 'JUPYTER_RUNTIME_DIR', 'JUPYTER_CONFIG_DIR', 'XDG_CACHE_HOME'):
    p = ROOT / 'supplementary' / '.runtime' / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
sys.path[:0] = [str(ROOT / 'supplementary' / 'approved'), str(ROOT / 'supplementary' / 'helpers'), str(ROOT)]

import numpy as np
import pepflow as pf
from certificate_tools import acquire, source_hashes

dense = json.loads((ROOT / 'state' / 'dual_feg_dense.json').read_text())
n = dense['N']
keep = {'initial_condition', f'A monotone:x_{n},x_star'}
for k in range(n - 1):
    keep.add(f'A monotone:x_{k}_half,x_{n}')
    keep.add(f'A Lipschitz:x_{k},x_{k}_half')
keep.add(f'A Lipschitz:x_{n - 1},x_{n}')
dropped = [name for name in dense['named_dual_values'] if name not in keep]
ctx, pb, result, entries, selected = acquire(n, dropped)
selected['certificate_provenance']['source_hashes'] = source_hashes(ROOT)
(ROOT / 'supplementary' / 'b2-selected-structural.json').write_text(json.dumps(selected, indent=2))
print('Structural', selected['opt_value'], selected['certificate_provenance']['solver_status'], flush=True)
candidate = {'initial_condition': 4 / n**2, f'A monotone:x_{n},x_star': 4 / n}
for k in range(n - 1):
    t = n - k
    candidate[f'A monotone:x_{k}_half,x_{n}'] = 4 / (t * (t - 1))
    candidate[f'A Lipschitz:x_{k},x_{k}_half'] = 2 / t**2
candidate[f'A Lipschitz:x_{n - 1},x_{n}'] = 2
for name in keep:
    print(name, selected['named_dual_values'][name], 'guess', candidate[name], flush=True)
pm = pf.ExpressionManager(ctx, resolve_parameters={'L': 1, 'R': 1})
Sguess = pf.Scalar.zero() + 4 / n**2 - pb.performance_metric
for c, *_ in entries:
    if c.name in candidate:
        Sguess += candidate[c.name] * (c.lhs - c.rhs)
M = np.asarray(pm.eval_scalar(Sguess).inner_prod_coords, dtype=float)
print('candidate S eigenvalues', np.linalg.eigvalsh(M), flush=True)
print('candidate S difference', np.max(np.abs(M - np.array(selected['S_matrix']))), flush=True)
print('basis', selected['basis_vectors'], flush=True)
w, v = np.linalg.eigh(M)
for j in np.flatnonzero(w > 1e-6):
    print('square', w[j], v[:, j], flush=True)
(ROOT / 'supplementary' / 'b2-formula-exploration.json').write_text(json.dumps({'lambda_candidate': candidate, 'S_candidate': M.tolist(), 'S_eigenvalues': w.tolist(), 'S_match_max_abs': float(np.max(np.abs(M - selected['S_matrix'])))}, indent=2))
