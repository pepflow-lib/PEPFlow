import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supplementary"))
from certificate_capture import (  # noqa: E402 - imports follow runtime or notebook setup
    capture,
)

dense = json.loads((ROOT / "state" / "dual_feg_dense.json").read_text())
N = dense["N"]
keep = {"initial_condition", f"A monotone:x_{N},x_star"}
keep |= {f"A monotone:x_{N},y_{k}" for k in range(N - 1)}
keep |= {f"A Lipschitz:x_{k},y_{k}" for k in range(N - 1)}
keep |= {f"A Lipschitz:x_{N - 1},x_{N}", f"A Lipschitz:x_{N},y_{N - 1}"}
dropped = [name for name in dense["named_dual_values"] if name not in keep]
data = capture(N, dropped)
(ROOT / "supplementary" / "sparse_candidate.json").write_text(
    json.dumps(data, indent=2)
)
print("Relaxed", data["opt_value"], data["solver_status"], "dropped", len(dropped))
for name, v in data["named_dual_values"].items():
    if v is not None:
        print(name, v)
