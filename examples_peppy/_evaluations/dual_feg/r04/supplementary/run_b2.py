"""Block 2 dense solve and sparsity investigation."""

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
    p = ROOT / "supplementary" / ".runtime" / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
sys.path[:0] = [
    str(ROOT / "supplementary" / "approved"),
    str(ROOT / "supplementary" / "helpers"),
    str(ROOT),
]

import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
from certificate_tools import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    acquire,
    source_hashes,
)

hashes = source_hashes(ROOT)
ctx, pb, result, entries, dense = acquire(6)
dense["certificate_provenance"]["source_hashes"] = hashes
(ROOT / "state" / "dual_feg_dense.json").write_text(json.dumps(dense, indent=2))
print(
    "Dense",
    dense["opt_value"],
    dense["certificate_provenance"]["solver_status"],
    flush=True,
)
for name, val in dense["named_dual_values"].items():
    if val > 1e-6:
        print(name, val, flush=True)
print("S eigenvalues", np.linalg.eigvalsh(dense["S_matrix"]), flush=True)
dropped = [
    name
    for name, val in dense["named_dual_values"].items()
    if name != "initial_condition" and abs(val) < 1e-6
]
print("Dropping", len(dropped), "of", len(dense["named_dual_values"]), flush=True)
ctx, pb, result, entries, selected = acquire(6, dropped)
selected["certificate_provenance"]["source_hashes"] = hashes
(ROOT / "supplementary" / "b2-selected-raw.json").write_text(
    json.dumps(selected, indent=2)
)
print(
    "Relaxed",
    selected["opt_value"],
    selected["certificate_provenance"]["solver_status"],
    flush=True,
)
for name, val in selected["named_dual_values"].items():
    if val is not None and val > 1e-6:
        print(name, val, flush=True)
print("S eigenvalues", np.linalg.eigvalsh(selected["S_matrix"]), flush=True)
