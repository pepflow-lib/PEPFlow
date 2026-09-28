import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json
from fractions import Fraction

import numpy as np
import runtime

# local helper resolved by the notebook runtime path
from certificate import solve_capture  # ty: ignore[unresolved-import]

N = 4
dense = json.loads((runtime.ROOT / "state/bppm_dense.json").read_text())
keep = {"initial_condition"}
keep.update(f"f:x_star,x_{k}" for k in range(1, N + 1))
keep.update(f"f:x_{k - 1},x_{k}" for k in range(2, N + 1))
keep.update(f"h:x_{k},x_{k - 1}" for k in range(1, N + 1))
keep.update(f"h:x_{k - 1},x_{k}" for k in range(2, N + 1))
keep.add(f"h:x_star,x_{N}")
relaxed = [name for name in dense["named_dual_values"] if name not in keep]
ctx, pb, result, entries, data = solve_capture(N, relaxed)
(runtime.ROOT / "state/bppm_relaxed.json").write_text(json.dumps(data, indent=2))
print(
    "Dense, relaxed, difference:",
    dense["opt_value"],
    data["opt_value"],
    abs(dense["opt_value"] - data["opt_value"]),
)
print("Dropped:", len(relaxed), "kept:", len(keep))
for name, v in data["named_dual_values"].items():
    if v is not None:
        print(name, v, Fraction(v).limit_denominator(1000))
print("S eigenvalues:", np.linalg.eigvalsh(data["S_matrix"]))
