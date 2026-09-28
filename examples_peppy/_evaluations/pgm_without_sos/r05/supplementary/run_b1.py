import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
    location = ROOT / "supplementary" / ".runtime" / key.lower()
    location.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(location)
sys.path[:0] = [
    str(ROOT / "supplementary" / "approved"),
    str(ROOT),
    str(ROOT / "supplementary" / "helpers"),
]
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from pgm_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)
from solve_runtime import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    solve_primal,
)

results = []
for n in range(1, 8):
    ctx, pb, _ = get_pep_setup(n, {})
    result, meta = solve_primal(ctx, pb, {"L": sp.Integer(1), "R": sp.Integer(1)})
    row = {"N": n, "opt_value": result.opt_value, **meta}
    results.append(row)
    (ROOT / "supplementary" / "_sweep_tmp.json").write_text(
        json.dumps(results, indent=2)
    )
    print(json.dumps(row), flush=True)
