import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import NOTEBOOK_DIR, configure  # ty: ignore[unresolved-import]

configure()
import json  # noqa: E402 - imports follow runtime or notebook setup

from derive_coefficients import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    derive,
)

e, unknowns, equations, solved, free, substitution = derive()
print(
    "Equations",
    len(equations),
    "Unknowns",
    len(unknowns),
    "free",
    sorted(map(str, free)),
)
for u, v in zip(unknowns, solved):
    print(u, "=", v)
record = {
    "equations": [str(v) for v in equations],
    "solution": {str(u): str(v) for u, v in zip(unknowns, solved)},
    "free_symbols": sorted(map(str, free)),
    "chosen_solution": {str(u): str(v) for u, v in substitution.items()},
}
(NOTEBOOK_DIR / "supplementary/b5-coefficient-derivation.json").write_text(
    json.dumps(record, indent=2)
)
