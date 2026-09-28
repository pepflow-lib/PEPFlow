import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import NOTEBOOK_DIR, configure  # ty: ignore[unresolved-import]

configure()
from certificates import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    capture,
    save,
    verify,
)

ctx, pb, result, data = capture(4)
checks, _ = verify(ctx, pb, data, data["opt_value"])
data["checks"] = checks
save(NOTEBOOK_DIR / "state/pgm_dense.json", data)
print("Dense objective", data["opt_value"], "checks", checks)
for name, v in data["named_dual_values"].items():
    print(name, v)
