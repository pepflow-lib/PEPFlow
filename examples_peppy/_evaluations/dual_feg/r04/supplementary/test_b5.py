"""Preliminary execution of exact symbolic proof cells."""
import json
import os
from pathlib import Path
import sys

notebook_dir = Path(__file__).resolve().parents[1]
repo_root = notebook_dir / 'supplementary/approved'
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
for key in ('TEMP', 'TMP', 'TMPDIR', 'MPLCONFIGDIR', 'IPYTHONDIR', 'JUPYTER_RUNTIME_DIR', 'JUPYTER_CONFIG_DIR', 'XDG_CACHE_HOME'):
    p = notebook_dir / 'supplementary/.runtime' / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
sys.path[:0] = [str(repo_root), str(notebook_dir / 'supplementary/helpers'), str(notebook_dir)]

import numpy as np
import pepflow as pf
import sympy as sp

b3 = json.loads((notebook_dir / 'state/dual_feg_b3.json').read_text())
for filename in ('b5_symbolic_definitions.py', 'b5_analytic_coefficients.py', 'b5_step.py', 'b5_base.py', 'b5_last_step.py', 'b5_boundary.py', 'b5_signs.py'):
    exec(compile((notebook_dir / 'supplementary' / filename).read_text(), filename, 'exec'), globals())
print(json.dumps(exact_identity_results, indent=2))
(notebook_dir / 'supplementary/b5-symbolic-preliminary.json').write_text(json.dumps(exact_identity_results, indent=2))
if '--save' in sys.argv:
    exec(compile((notebook_dir / 'supplementary/b5_save.py').read_text(), 'b5_save.py', 'exec'), globals())
