import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import runtime
from b2_core import solve_capture

ctx, pb, result, data = solve_capture(4, {"alpha": 1, "R": 1}, [], runtime.ATTEMPT)
(runtime.ATTEMPT / "state/bppm_dense.json").write_text(json.dumps(data, indent=2))
