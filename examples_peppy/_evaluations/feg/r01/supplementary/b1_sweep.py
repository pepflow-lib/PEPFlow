"""Required B1 rate sweep, retaining all actually observed results."""

import json
import time
from pathlib import Path

from feg_setup import get_pep_setup

# local helper resolved by the notebook runtime path
from solve_tools import solve_setup  # ty: ignore[unresolved-import]

results = []
for n in range(1, 8):
    started = time.monotonic()
    ctx, pb, obj = get_pep_setup(n, {"L": 1, "R": 1})
    assert ctx["x_0"].uid == ctx["x_1/2"].uid
    result, options = solve_setup(ctx, pb, {"L": 1, "R": 1})
    item = {
        "N": n,
        "opt_value": float(result.opt_value),
        "status": result.solver_status,
        "solver_options": options,
        "seconds": time.monotonic() - started,
    }
    results.append(item)
    Path("supplementary/_sweep_tmp.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(item), flush=True)
