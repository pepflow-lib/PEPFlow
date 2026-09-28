import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json  # noqa: E402

import cvxpy as cp  # noqa: E402
import runtime  # noqa: E402
from pgm_setup import get_pep_setup  # noqa: E402

import pepflow as pf  # noqa: E402

cache = runtime.ATTEMPT / "supplementary" / "_sweep_tmp.json"
results = json.loads(cache.read_text()) if cache.exists() else []
for n in range(len(results) + 1, 8):
    ctx, pb, obj = get_pep_setup(n, {"L": 1, "R": 1})
    constraints = list(pb.init_conditions)
    for func in ctx.func_to_triplets:
        constraints.extend(func.get_interpolation_constraints(ctx))
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    solver_name, options = "CLARABEL", {}
    try:
        value = problem.solve(solver=solver_name, **options)
    except cp.error.SolverError:
        solver_name, options = "SCS", {"eps": 1e-7, "max_iters": 200000}
        value = problem.solve(solver=solver_name, **options)
    row = {
        "N": n,
        "opt_value": float(value),
        "status": problem.status,
        "solver": solver_name,
        "options": options,
    }
    results.append(row)
    print(row, flush=True)
    (runtime.ATTEMPT / "supplementary" / "_sweep_tmp.json").write_text(
        json.dumps(results, indent=2)
    )
