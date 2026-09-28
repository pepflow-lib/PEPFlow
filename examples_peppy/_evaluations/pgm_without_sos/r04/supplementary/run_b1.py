import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import cvxpy as cp
import runtime
from pgm_setup import get_pep_setup

import pepflow as pf

results = []
for N in range(1, 8):
    ctx, pb, _ = get_pep_setup(N, {"L": 1, "R": 1})
    constraints = list(pb.init_conditions)
    for obj in ctx.func_to_triplets:
        constraints.extend(obj.get_interpolation_constraints(ctx))
    assert pb.performance_metric is not None
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    options = {"solver": "CLARABEL"}
    failure = None
    try:
        value = problem.solve(**options)
    except cp.error.SolverError as exc:
        failure = str(exc)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    if problem.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(problem.status)
    row = {
        "N": N,
        "opt_value": float(value),
        "solver_status": problem.status,
        "solver_options": options,
        "fallback_reason": failure,
        "tau_sol": float(solver.dual_var_manager.dual_value("initial_condition")),
    }
    results.append(row)
    print(json.dumps(row), flush=True)
(runtime.ATTEMPT / "supplementary/_sweep_tmp.json").write_text(
    json.dumps(results, indent=2)
)
