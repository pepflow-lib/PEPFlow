import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import runtime
import sympy as sp
from bppm_setup import get_pep_setup

import pepflow as pf

results = []
for N in range(1, 8):
    ctx, pb, f = get_pep_setup(N, {})
    constraints = list(pb.init_conditions)
    for func in ctx.func_to_triplets:
        constraints.extend(func.get_interpolation_constraints(ctx))
    solver = pf.CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters={"alpha": sp.S(1), "R": sp.S(1)})
    value = problem.solve(solver="CLARABEL")
    row = {
        "N": N,
        "opt_value": value,
        "solver": problem.solver_stats.solver_name,
        "solver_options": {},
        "status": problem.status,
        "candidate": 1 / N,
        "error": value - 1 / N,
    }
    results.append(row)
    print(row, flush=True)
(runtime.ROOT / "supplementary" / "b1-sweep.json").write_text(
    json.dumps(results, indent=2)
)
assert all(r["status"] == "optimal" and abs(r["error"]) <= 1e-5 for r in results)
