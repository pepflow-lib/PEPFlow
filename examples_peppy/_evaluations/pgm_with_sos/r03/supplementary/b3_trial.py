import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import NOTEBOOK_DIR, configure  # ty: ignore[unresolved-import]

configure()
import json  # noqa: E402 - imports follow runtime or notebook setup

from grouping import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    construct,
)

state = json.loads((NOTEBOOK_DIR / "state/pgm_b2.json").read_text())
ctx, pb, lyap, sample = construct(state)
(NOTEBOOK_DIR / "supplementary/b3-N4-trial.json").write_text(
    json.dumps(sample, indent=2)
)
print("Coverage residual:", sample["coverage_residual"])
print("Singular values:", sample["singular_values"])
