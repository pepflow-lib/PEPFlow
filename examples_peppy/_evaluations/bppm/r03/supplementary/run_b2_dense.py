import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import bppm_setup as setup

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
from certificate import capture  # ty: ignore[unresolved-import]

params = {"alpha": 1, "R": 1}
ctx, pb, obj = setup.get_pep_setup(4, params)
data = capture(ctx, pb, obj, params)
(runtime.ROOT / "state/bppm_dense.json").write_text(json.dumps(data, indent=2))
print("objective", data["opt_value"])
print("S max", max(abs(x) for row in data["S_matrix"] for x in row))
for name, value in data["named_dual_values"].items():
    if value is not None and abs(value) > 1e-6:
        print(name, round(value, 8))
print(data["basis_vectors"])
