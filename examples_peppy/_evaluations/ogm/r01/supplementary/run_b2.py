import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "supplementary/helpers"))
import json  # noqa: E402 - imports follow runtime or notebook setup

import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
from certificates import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    acquire,
)

state, ctx, pb, result, entries = acquire(4)
(root / "state/ogm_dense.json").write_text(json.dumps(state, indent=2))
print("Bound", state["opt_value"])
print("Basis", state["basis_vectors"])
print("Eigenvalues", np.linalg.eigvalsh(state["S_matrix"]))
for name, v in state["named_dual_values"].items():
    print(name, v)
