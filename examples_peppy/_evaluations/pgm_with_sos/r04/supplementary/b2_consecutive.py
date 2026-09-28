import json
from fractions import Fraction

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
from b2_explore import acquire

dense = json.loads((runtime.ROOT / "state/pgm_dense.json").read_text())
drop = []
for name in dense["named_dual_values"]:
    if ":" not in name:
        continue
    owner, pair = name.split(":")
    left, right = pair.split(",")
    keep = left == "x_star" or (
        left != "x_star" and right != "x_star" and int(right[2:]) == int(left[2:]) + 1
    )
    if not keep:
        drop.append(name)
ctx, pb, result, data = acquire(4, drop)
(runtime.ROOT / "supplementary/b2-consecutive.json").write_text(
    json.dumps(data, indent=2)
)
print(data["status"], data["opt_value"])
for name, value in data["named_dual_values"].items():
    print(name, value, str(Fraction(value).limit_denominator(1000)))
