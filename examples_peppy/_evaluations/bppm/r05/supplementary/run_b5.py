# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Execute the exact symbolic constructions before final notebook assembly."""

import json
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
approved = root / "supplementary/approved"
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
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    path = root / "supplementary/.runtime" / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
sys.path[:0] = [str(approved), str(root / "supplementary/helpers")]
import numpy as np  # noqa: E402, F401 -- Required by exec of b5_symbolic_common.py. Paths initialized above.

import pepflow as pf  # noqa: E402, F401 -- Required by exec of b5_symbolic_common.py. Paths initialized above.

# Preserve the recorded import initialization order.
# isort: split
import sympy as sp  # noqa: E402, F401 -- Required by exec of b5_symbolic_common.py. Paths initialized above.

b4 = json.loads((root / "state/bppm_b4.json").read_text())
assert b4["numerical_reconstruction"]["passed"]
assert b4["numerical_reconstruction"]["certificate_id"] == b4["certificate_id"]
for name in ("symbolic_common", "step", "base", "boundary"):
    source = (root / f"supplementary/b5_{name}.py").read_text()
    exec(compile(source, f"b5_{name}.py", "exec"))
assert all(proof_checks.values()) and structure_verified
(root / "supplementary/b5-symbolic-results.json").write_text(
    json.dumps(
        {
            "exact_results": exact_results,
            "proof_checks": proof_checks,
            "structure_verified": bool(structure_verified),
            "domain": "alpha>0; R>=0; integer N>=1; integer 0<=k<N",
        },
        indent=2,
    )
)
