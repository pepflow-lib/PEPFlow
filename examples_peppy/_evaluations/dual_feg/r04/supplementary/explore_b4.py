# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Explore basis candidates and direct interpretable pattern."""

import json  # noqa: F401 -- Required by exec of b4_rebuild.py.
import os
import sys
from pathlib import Path

notebook_dir = Path(__file__).resolve().parents[1]
repo_root = notebook_dir / "supplementary/approved"
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "MPLCONFIGDIR",
    "IPYTHONDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    p = notebook_dir / "supplementary/.runtime" / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
sys.path[:0] = [
    str(repo_root),
    str(notebook_dir / "supplementary/helpers"),
    str(notebook_dir),
]
import numpy as np  # noqa: E402, F401 -- Required by exec of b4_rebuild.py. Paths initialized above.
import sympy as sp  # noqa: E402, F401 -- Required by exec of b4_rebuild.py. Paths initialized above.
from dual_feg_setup import (  # noqa: E402, F401 -- Required by exec of b4_rebuild.py. Paths initialized above.
    get_pep_setup,
)

for name in ("b4_rebuild.py", "b4_scan.py", "b4_basis.py"):
    exec(
        compile((notebook_dir / "supplementary" / name).read_text(), name, "exec"),
        globals(),
    )
for k in range(N_int + 1):
    C = find_symmetric_coefficient_matrix(
        lyap[k],
        V_k_basis(k),
        pep_context=ctx,
        resolve_parameters=params_sp,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    print("Adopted", k, V_k_basis_labels(k), C, flush=True)
