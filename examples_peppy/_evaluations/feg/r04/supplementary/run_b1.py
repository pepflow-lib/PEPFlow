import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import cvxpy as cp

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
import sympy as sp
from feg_setup import get_pep_setup

import pepflow as pf

results = []
for n in range(1, 8):
    ctx, pb, op = get_pep_setup(n, {})
    constraints = pb.init_conditions + op.get_interpolation_constraints(ctx)
    solver = pf.CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters={"L": sp.S.One, "R": sp.S.One})
    options = {}
    solver_name = "CLARABEL"
    try:
        value = problem.solve(solver=solver_name)
        if problem.status not in ("optimal", "optimal_inaccurate"):
            raise RuntimeError(problem.status)
    except (cp.error.SolverError, RuntimeError):
        solver_name = "SCS"
        options = {"eps": 1e-7, "max_iters": 200000}
        value = problem.solve(solver=solver_name, **options)
    row = {
        "N": n,
        "opt_value": float(value),
        "status": problem.status,
        "solver": solver_name,
        "options": options,
        "initial_half_is_x0": ctx["x_0"].uid == ctx["x_1/2"].uid,
    }
    results.append(row)
    print(json.dumps(row), flush=True)
    (runtime.ATTEMPT / "supplementary" / "_sweep_tmp.json").write_text(
        json.dumps(results, indent=2)
    )
