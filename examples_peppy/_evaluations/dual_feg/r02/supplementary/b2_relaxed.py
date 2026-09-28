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
import dual_feg_setup as setup  # noqa: E402 - imports follow runtime or notebook setup
from certificate import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    capture,
)

dense = json.loads((root / "state/dual_feg_dense.json").read_text())
ctx, pb, obj = setup.get_pep_setup(6, {"L": 1, "R": 1})
dropped = [
    name
    for name, val in dense["named_dual_values"].items()
    if val is not None and val < 1e-6 and name != "initial_condition"
]
pb.set_relaxed_constraints(dropped)
data = capture(ctx, pb, obj, {"L": 1, "R": 1})
data["N"] = 6
data["sparsity_selection"] = {
    "method": "drop dense multipliers below 1e-6",
    "threshold": 1e-6,
    "dense_gap": abs(data["opt_value"] - dense["opt_value"]),
}
(root / "state/dual_feg_relaxed.json").write_text(json.dumps(data, indent=2))
print("Objective and gap", data["opt_value"], data["sparsity_selection"]["dense_gap"])
for name, val in data["named_dual_values"].items():
    if val is not None:
        print(name, val)
