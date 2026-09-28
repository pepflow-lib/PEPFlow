import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supplementary"))
from certificate_capture import capture
prior = json.loads((ROOT / "supplementary" / "sparse_candidate.json").read_text())
dropped = prior["relaxed_constraints"] + ["A Lipschitz:x_6,y_5"]
data = capture(6, dropped)
(ROOT / "supplementary" / "sparse_candidate_2.json").write_text(json.dumps(data, indent=2))
print(data["opt_value"], data["solver_status"])
for name, v in data["named_dual_values"].items():
    if v is not None:
        print(name, v)

