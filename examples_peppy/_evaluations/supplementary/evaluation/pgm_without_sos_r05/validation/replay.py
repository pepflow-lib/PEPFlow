import os
import sys
from pathlib import Path
import json
import hashlib

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parents[3] / 'pgm_without_sos' / 'r05'
assert ORIGINAL.is_dir(), ORIGINAL
for key in ('TEMP','TMP','TMPDIR','MPLCONFIGDIR','IPYTHONDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME'):
    loc = HERE / 'runtime' / key.lower()
    loc.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(loc)
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
sys.path.insert(0, str(ORIGINAL / 'supplementary' / 'approved'))
import numpy as np
import sympy as sp
import pepflow as pf
notebook_dir = ORIGINAL
repo_root = ORIGINAL / 'supplementary' / 'approved'
nb = json.loads((ORIGINAL / 'pgm_example_lyap.ipynb').read_text(encoding='utf-8'))
def cell(i):
    print('REPLAY CELL', i, nb['cells'][i]['id'], flush=True)
    exec(compile(''.join(nb['cells'][i]['source']), f'cell-{i}', 'exec'), globals())
results = {}
for i in (6,7,18,19,20,21,24,26,27,29,31,33,34):
    cell(i)
results['N4'] = {'certificate_id':certificate['certificate_id'], 'ranks':ranks, 'singular_values':singular_values, 'coverage':coverage_residuals, 'minimum_piece_eigenvalue':minimum_piece_eigenvalue, 'quadratic_reconstruction':coefficient_residuals, 'component_residuals':component_residuals}
proof_checks = dict.fromkeys(('step','base','boundary','signs','domain','normalization'), False)
for i in (38,39,43,46,49,52,54):
    cell(i)
results['exact'] = {'proof_checks':proof_checks, 'N1':one_verified, 'closed_comparison':closed_comparison}
certificate = json.loads((ORIGINAL / 'supplementary/b2-n06-certificate.json').read_text())
N_int = certificate['N_verify']
ctx,pb,obj = get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
ctx.set_as_current()
for i in (19,20,21):
    cell(i)
results['N6'] = {'certificate_id':certificate['certificate_id'], 'ranks':ranks, 'singular_values':singular_values, 'coverage':coverage_residuals, 'minimum_piece_eigenvalue':minimum_piece_eigenvalue}
(HERE / 'replay-results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
print('ALL SELECTED CHECKS PASSED', flush=True)
