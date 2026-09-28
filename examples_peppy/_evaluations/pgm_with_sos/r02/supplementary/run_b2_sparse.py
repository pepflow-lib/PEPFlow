import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime", root / "supplementary/helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
from certificate import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    acquire,
    summarize,
    verify,
)

dense = json.loads((root / "state/pgm_dense.json").read_text())
relaxed = []
for name in dense["named_dual_values"]:
    if name == "initial_condition":
        continue
    owner, pair = name.split(":")
    left, right = pair.split(",")
    keep = left == "x_star" or (
        left != "x_star" and right != "x_star" and int(right[2:]) == int(left[2:]) + 1
    )
    if not keep:
        relaxed.append(name)
data, ctx, pb, result = acquire(4, relaxed)
(root / "supplementary/b2-sparse-hypothesis1.json").write_text(
    json.dumps(data, indent=2)
)
summarize(data)
print("check", verify(data, dense["opt_value"])[0])
