import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json
from fractions import Fraction

import numpy as np
import runtime

# local helper resolved by the notebook runtime path
from certificate import acquire, verify  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
n = 6
dense = json.loads((root / "state/dual_feg_dense.json").read_text())
keep = {f"A monotone:x_{n},x_star"}
keep.update(f"A monotone:x_{n},y_{k}" for k in range(n - 1))
keep.update(f"A Lipschitz:x_{k},y_{k}" for k in range(n - 1))
keep.add(f"A Lipschitz:x_{n - 1},x_{n}")
relaxed = [
    name
    for name, meta in dense["constraint_metadata"].items()
    if meta["origin"] == "interpolation" and name not in keep
]
state = acquire(n, relaxed, root)
checks, passed = verify(state, dense["opt_value"])
state["preliminary_checks"] = {"passed": passed, "residuals": checks}
(root / "supplementary/b2_sparse_candidate.json").write_text(
    json.dumps(state, indent=2)
)
print(
    "Sparse bound",
    state["opt_value"],
    state["certificate_provenance"]["solver_status"],
    checks,
    passed,
)
print("S eigenvalues", np.linalg.eigvalsh(state["S_matrix"]))
for name, v in state["named_dual_values"].items():
    if v is not None:
        print(name, v, str(Fraction(v).limit_denominator(10000)))
