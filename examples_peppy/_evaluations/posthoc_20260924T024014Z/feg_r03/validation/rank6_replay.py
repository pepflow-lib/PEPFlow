# Notebook cells and source fragments executed below supply these globals.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import contextlib
import json
import os
import sys
from pathlib import Path

root = Path(chr(92) * 2 + "?" + chr(92) + str(Path(__file__).resolve().parent))
notebook_dir = root
REPO_ROOT = root / "supplementary/approved"
os.chdir(root)
sys.path[:0] = [str(root / "supplementary/approved"), str(root)]
for key in [
    "TEMP",
    "TMP",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "JUPYTER_DATA_DIR",
    "XDG_CACHE_HOME",
]:
    p = root / "posthoc_runtime" / key
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
import numpy as np  # noqa: E402 -- Initialize paths and runtime environment before importing.
import sympy as sp  # noqa: E402 -- Initialize paths and runtime environment before importing.
from feg_setup import (  # ty: ignore[unresolved-import]  # Runtime bootstrap adds the archived helper directory to sys.path.  # noqa: E402 -- Initialize paths and runtime environment before importing.
    get_pep_setup,
)

certificate = json.loads((root / "supplementary/b2-N6.json").read_text())
N_int = certificate["N_verify"]
params_sp = {k: sp.S(v) for k, v in json.loads(certificate["params_json"]).items()}
ctx, pb, obj = get_pep_setup(sp.S(N_int), params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
ctx.set_as_current()
with (
    (root / "rank6-output.txt").open("w", encoding="utf-8") as log,
    contextlib.redirect_stdout(log),
):
    for f in ["b3_certificate_check.py", "b3_decomposition.py", "b3_grouping.py"]:
        src = (root / "supplementary" / f).read_text(encoding="utf-8-sig")
        assert "write_text" not in src and "write_bytes" not in src
        exec(compile(src, f, "exec"))
result = dict(
    N=N_int,
    ranks=ranks,
    singular_values=singular_values,
    certificate_checked=certificate_checked,
    grouping_checked=grouping_checked,
    tolerances=tol,
    min_eigenvalue=float(np.linalg.eigvalsh(S_array).min()),
    min_dual=min(
        float(x) for x in certificate["named_dual_values"].values() if x is not None
    ),
)
(root / "rank6-results.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
