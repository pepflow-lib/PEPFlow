import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np
import runtime

# local helper resolved by the notebook runtime path
from certificates import acquire  # ty: ignore[unresolved-import]

ctx, pb, result, dense = acquire(4)
(runtime.ATTEMPT / "state/pgm_dense.json").write_text(json.dumps(dense, indent=2))
print("DENSE", dense["opt_value"], dense["solver_status"])
print("BASIS", dense["basis_vectors"])
print("S eigenvalues", np.linalg.eigvalsh(np.array(dense["S_matrix"])))
for name, value in dense["named_dual_values"].items():
    if value is not None and abs(value) > 1e-6:
        print(name, round(value, 8))
# First sparsity hypothesis: retain star-to-iterate and forward consecutive pairs.
dropped = []
for name, meta in dense["constraint_metadata"].items():
    if meta["origin"] != "interpolation":
        continue
    _, pair = name.split(":")
    ri, ci = pair.split(",")
    adjacent = ri != "x_star" and ci != "x_star" and int(ci[2:]) == int(ri[2:]) + 1
    if not (ri == "x_star" or adjacent):
        dropped.append(name)
ctx, pb, result, selected = acquire(4, dropped)
(runtime.ATTEMPT / "supplementary/b2-sparse-first.json").write_text(
    json.dumps(selected, indent=2)
)
print(
    "SPARSE",
    selected["opt_value"],
    selected["solver_status"],
    "gap",
    selected["opt_value"] - dense["opt_value"],
)
for name, value in selected["named_dual_values"].items():
    if value is not None and abs(value) > 1e-6:
        print(name, round(value, 8))
