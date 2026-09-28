"""Acquire a separate N=8 certificate for cross-horizon rank confirmation."""

import json
import os
import sys
from pathlib import Path

notebook_dir = Path(__file__).resolve().parents[1]
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
    str(notebook_dir / "supplementary/approved"),
    str(notebook_dir / "supplementary/helpers"),
    str(notebook_dir),
]
import sympy as sp  # noqa: E402, F401 -- Required by exec of b2_verification_core.py. Paths initialized above.
from certificate_tools import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    acquire,
    source_hashes,
)
from dual_feg_setup import (  # noqa: E402, F401 -- Required by exec of b2_verification_core.py. Paths initialized above.
    get_pep_setup,
)

directory = notebook_dir / "supplementary/n8"
directory.mkdir(exist_ok=True)
n = 8
hashes = source_hashes(notebook_dir)
ctx, pb, result, entries, dense = acquire(n)
dense["certificate_provenance"]["source_hashes"] = hashes
(directory / "dense.json").write_text(json.dumps(dense, indent=2))
print(
    "N=8 dense",
    dense["opt_value"],
    dense["certificate_provenance"]["solver_status"],
    flush=True,
)
keep = {"initial_condition", f"A monotone:x_{n},x_star"}
for k in range(n - 1):
    keep.add(f"A monotone:x_{k}_half,x_{n}")
    keep.add(f"A Lipschitz:x_{k},x_{k}_half")
keep.add(f"A Lipschitz:x_{n - 1},x_{n}")
dropped = [name for name in dense["named_dual_values"] if name not in keep]
ctx, pb, result, entries, selected = acquire(n, dropped)
selected["certificate_provenance"]["source_hashes"] = hashes
(directory / "selected-raw.json").write_text(json.dumps(selected, indent=2))
print(
    "N=8 sparse",
    selected["opt_value"],
    selected["certificate_provenance"]["solver_status"],
    flush=True,
)
source = (notebook_dir / "supplementary/b2_verification_core.py").read_text()
source = source.replace(
    "notebook_dir / 'state' / 'dual_feg_dense.json'",
    "notebook_dir / 'supplementary/n8/dense.json'",
)
source = source.replace(
    "notebook_dir / 'supplementary' / 'b2-selected-structural.json'",
    "notebook_dir / 'supplementary/n8/selected-raw.json'",
)
source = source.replace(
    "notebook_dir / 'state' / filename", "notebook_dir / 'supplementary/n8' / filename"
)
source = source.replace(
    "Preserved bound with 12 interpolation constraints",
    "Preserved bound with 16 interpolation constraints",
)
source = source.replace("checked only at N=6", "checked at N=6 and N=8 independently")
(directory / "verification.py").write_text(source)
exec(compile(source, "n8/verification.py", "exec"))
print("Separate N=8 complete certificate verified and saved.", flush=True)
