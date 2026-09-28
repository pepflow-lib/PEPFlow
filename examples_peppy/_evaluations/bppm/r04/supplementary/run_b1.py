import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import cvxpy as cp
import runtime
from bppm_setup import get_pep_setup

import pepflow as pf

results = []
for N in range(1, 8):
    ctx, pb, f = get_pep_setup(N, {"alpha": 1, "R": 1})
    constraints = list(pb.init_conditions)
    for fun in ctx.func_to_triplets:
        constraints.extend(fun.get_interpolation_constraints(ctx))
    solver = pf.CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters={"alpha": 1, "R": 1})
    options = {"solver": "CLARABEL"}
    try:
        value = problem.solve(**options)
    except cp.error.SolverError:
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    row = {
        "N": N,
        "opt_value": value,
        "status": problem.status,
        "solver_options": options,
        "solver_name": problem.solver_stats.solver_name,
        "conjecture": 1 / N,
        "absolute_error": abs(value - 1 / N),
    }
    results.append(row)
    print(json.dumps(row), flush=True)
    (runtime.ATTEMPT / "supplementary" / "b1_sweep.json").write_text(
        json.dumps(results, indent=2)
    )
    assert problem.status == "optimal"
    assert row["absolute_error"] < 1e-5
