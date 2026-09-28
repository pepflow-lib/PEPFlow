"""Initial dense certificate and structural summary."""

import json
from pathlib import Path

import numpy as np

# local helper resolved by the notebook runtime path
from certificate_tools import capture, source_hashes  # ty: ignore[unresolved-import]
from feg_setup import get_pep_setup

root = Path.cwd()
hashes = source_hashes(root)
ctx, pb, obj = get_pep_setup(6, {"L": 1, "R": 1})
state, result, sm = capture(ctx, pb, obj, {"L": 1, "R": 1})
state["N"] = 6
state["certificate_provenance"]["source_hashes"] = hashes
assert hashes == source_hashes(root)
(root / "state/feg_dense.json").write_text(json.dumps(state, indent=2))
print("objective", state["opt_value"])
print("basis", state["basis_vectors"])
print("S eigenvalues", np.linalg.eigvalsh(sm.matrix))
for name, value in state["named_dual_values"].items():
    if value is not None and abs(value) > 1e-6:
        print(name, value)
