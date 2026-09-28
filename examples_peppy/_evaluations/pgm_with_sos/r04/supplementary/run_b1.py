import json
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import runtime
import pgm_setup

results = []
for n in range(1, 8):
    ctx, pb, _ = pgm_setup.get_pep_setup(n, {"L": 1, "R": 1})
    problem, solver, options = runtime.solve_builder(ctx, pb, {"L": 1, "R": 1})
    result = {"N": n, "opt_value": float(problem.value), "status": problem.status,
              "solver_options": options, "solver_name": problem.solver_stats.solver_name}
    results.append(result)
    print(result, flush=True)
    (runtime.ROOT / "supplementary" / "_sweep_tmp.json").write_text(json.dumps(results, indent=2))
    if problem.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(problem.status)
print("fractions", [str(Fraction(r["opt_value"]).limit_denominator(1000)) for r in results])
print("inverse", [1/r["opt_value"] for r in results])

