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
sys.path[:0] = [
    str(ROOT / "supplementary" / "approved"),
    str(ROOT),
    str(ROOT / "supplementary" / "helpers"),
]
import numpy as np  # noqa: E402

# local helper resolved by the notebook runtime path
from certificates import (  # noqa: E402  # ty: ignore[unresolved-import]
    revalidate,
    solve_certificate,
)

dense = solve_certificate(4)
revalidate(dense)
(ROOT / "state" / "ogm_dense.json").write_text(json.dumps(dense, indent=2))
print(
    "DENSE", dense["opt_value"], "S eigenvalues", np.linalg.eigvalsh(dense["S_matrix"])
)
print("BASIS", dense["basis_vectors"])
for name, val in dense["named_dual_values"].items():
    if val is not None and val > 1e-6:
        print(name, val)
relaxed = [
    name
    for name, val in dense["named_dual_values"].items()
    if val is not None and val < 1e-6 and name != "initial_condition"
]
relaxed.append("f:x_4,x_3")
selected = solve_certificate(4, relaxed)
revalidate(selected)
(ROOT / "supplementary" / "b2_candidate.json").write_text(
    json.dumps(selected, indent=2)
)
print("SELECTED", selected["opt_value"], "DROP", relaxed)
print("S", np.asarray(selected["S_matrix"]))
for name, val in selected["named_dual_values"].items():
    if val is not None and val > 1e-6:
        print(name, val)
