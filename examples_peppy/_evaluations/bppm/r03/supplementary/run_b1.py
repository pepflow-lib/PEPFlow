import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import bppm_setup as setup

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

params = {"alpha": 1, "R": 1}
results = []
for n in range(1, 8):
    ctx, pb, _ = setup.get_pep_setup(n, params)
    result, info = runtime.solve_builder(ctx, pb, params)
    row = {"N": n, "opt_value": float(result.opt_value), **info}
    results.append(row)
    print(row, flush=True)
(runtime.ROOT / "supplementary" / "_sweep_tmp.json").write_text(
    json.dumps(results, indent=2)
)
