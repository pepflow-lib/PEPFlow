import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import json

from b2_acquire import acquire, attempt

dense = json.loads((attempt / "state/ogm_dense.json").read_text())
points = ["z_0"] + [f"x_{k}" for k in range(1, dense["N"] + 1)]
keep = (
    {f"f:x_star,{p}" for p in points}
    | {f"f:{a},{b}" for a, b in zip(points[:-1], points[1:])}
    | {"initial_condition"}
)
relaxed = [name for name in dense["named_dual_values"] if name not in keep]
acquire(relaxed, "supplementary/b2-chain-certificate.json")
