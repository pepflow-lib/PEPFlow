from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
from runtime import ATTEMPT, solve_explicit
import json
import sympy as sp
from bppm_setup import get_pep_setup

results = []
for N in range(1, 8):
    ctx, pb, obj = get_pep_setup(N, {})
    result, attempts = solve_explicit(ctx, pb, {"alpha": sp.Integer(1), "R": sp.Integer(1)})
    row = {"N": N, "opt_value": float(result.opt_value), "conjecture": 1/N,
           "absolute_error": abs(float(result.opt_value)-1/N), "solver_attempts": attempts}
    results.append(row)
    print(json.dumps(row), flush=True)
(ATTEMPT / "supplementary" / "_sweep_tmp.json").write_text(json.dumps(results, indent=2))
assert max(row["absolute_error"] for row in results) <= 1e-5

