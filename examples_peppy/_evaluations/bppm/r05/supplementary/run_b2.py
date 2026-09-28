"""B2 numerical discovery, with all source and certificate provenance retained."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
APPROVED = ROOT / 'supplementary' / 'approved'
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
for key in ('TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME'):
    path = ROOT / 'supplementary' / '.runtime' / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
sys.path[:0] = [str(APPROVED), str(ROOT / 'supplementary' / 'helpers')]
import numpy as np
import sympy as sp
from certificate_tools import solve_capture

spec = importlib.util.spec_from_file_location('bppm_setup', ROOT / 'bppm_setup.py')
assert spec is not None and spec.loader is not None
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
b1 = json.loads((ROOT / 'state' / 'bppm_b1.json').read_text())
params = {k: sp.S(v) for k,v in json.loads(b1['params_json']).items()}
source_files = [ROOT/'bppm_setup.py', ROOT/'supplementary/helpers/certificate_tools.py']
allowlist = json.loads((APPROVED/'allowlist.json').read_text())
source_files.extend(Path(p) for p in allowlist['exact_read_files'] if Path(p).parent == APPROVED/'pepflow')
hashes = {str(p.relative_to(ROOT)).replace('\\','/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
ctx, pb, obj = setup.get_pep_setup(b1['N_verify'], params)
dense = solve_capture(ctx, pb, params, hashes)
dense['N'] = b1['N_verify']
(ROOT/'state/bppm_dense.json').write_text(json.dumps(dense, indent=2))
print('DENSE', dense['opt_value'])
print('BASIS', dense['basis_vectors'])
print('S eig', np.linalg.eigvalsh(np.array(dense['S_matrix'])))
for name,v in dense['named_dual_values'].items():
    if v is not None and abs(v)>1e-6:
        print(name, v)
