import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import runtime
import json
import sympy as sp
from pgm_setup import get_pep_setup

results = []
for n in range(1, 8):
    ctx, pb, _ = get_pep_setup(n, {"L": 1, "R": 1})
    result, options = runtime.solve_setup(ctx, pb, {"L": sp.S.One, "R": sp.S.One})
    row = {"N": n, "opt_value": float(result.opt_value), "status": result.solver_status,
           "solver_options": options}
    results.append(row)
    print(json.dumps(row), flush=True)
(runtime.ROOT / "supplementary" / "_sweep_tmp.json").write_text(json.dumps(results, indent=2))

