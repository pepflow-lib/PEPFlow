import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import fractions
import json

import numpy as np

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
from certificate import acquire  # ty: ignore[unresolved-import]

dense = json.loads((runtime.ATTEMPT / "state/feg_dense.json").read_text())
relaxed = [
    k
    for k, v in dense["named_dual_values"].items()
    if k != "initial_condition" and abs(v) < 1e-6
]
data = acquire(6, relaxed, dense["opt_value"])
(runtime.ATTEMPT / "supplementary/b2-sparse-002.json").write_text(
    json.dumps(data, indent=2, allow_nan=False)
)
print("Sparse objective/checks", data["opt_value"], data["numerical_checks"])
for name, value in data["named_dual_values"].items():
    if value is not None:
        print(name, value, str(fractions.Fraction(value).limit_denominator(1000)))
print("S", np.array(data["S_matrix"]))
print("D diagonal", np.diag(data["numerical_decomposition"]["D"]))
