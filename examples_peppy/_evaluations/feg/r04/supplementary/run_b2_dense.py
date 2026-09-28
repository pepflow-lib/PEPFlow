import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
from certificate import acquire  # ty: ignore[unresolved-import]

data = acquire(6)
(runtime.ATTEMPT / "state/feg_dense.json").write_text(
    json.dumps(data, indent=2, allow_nan=False)
)
print("Dense objective", data["opt_value"], "checks", data["numerical_checks"])
print("Basis", data["basis_vectors"])
print("S eigenvalues", np.linalg.eigvalsh(data["S_matrix"]))
for key, val in data["named_dual_values"].items():
    if val is not None and abs(val) > 1e-6:
        print(key, round(val, 8))
