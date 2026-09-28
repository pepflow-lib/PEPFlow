"""Execute the exact proof cells and save observed symbolic residual evidence."""
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for key in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"]:
    os.environ[key] = "1"
sys.path[:0] = [str(ROOT / "supplementary/approved"),str(ROOT / "supplementary")]
import numpy as np  # noqa: E402
import pepflow as pf  # noqa: E402
import sympy as sp  # noqa: E402
from b5_notebook_cells import HELPERS,STEP,BASE,TERMINAL,BOUNDARY,SMALL,SIGNS  # noqa: E402

ns: dict[str,Any] = dict(np=np,pf=pf,sp=sp)
for source in (HELPERS,STEP,BASE,TERMINAL,BOUNDARY,SMALL,SIGNS):
    exec(source,ns)
(ROOT / "supplementary/b5-exact-evidence.json").write_text(json.dumps(ns["proof_results"],indent=2))
print(json.dumps(ns["proof_results"],indent=2))
