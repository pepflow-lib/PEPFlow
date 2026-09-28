"""Explicit solver selection using approved PEPFlow APIs."""
import cvxpy as cp
import pepflow as pf


def solve_primal(ctx, pb, params):
    constraints = list(pb.init_conditions)
    for obj in ctx.func_to_triplets:
        constraints.extend(obj.get_interpolation_constraints(ctx))
    constraints = [c for c in constraints if c.name not in pb.relaxed_constraints]
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=params)
    options = {"solver": "CLARABEL"}
    failure = None
    try:
        problem.solve(**options)
        if problem.status not in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE):
            raise RuntimeError(str(problem.status))
    except (cp.error.SolverError, RuntimeError) as exc:
        failure = str(exc)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        problem.solve(**options)
    result = pf.PEPResult(float(problem.value), solver.dual_var_manager,
                          pf.PEPType.PRIMAL, problem.status, ctx)
    metadata = {"solver": problem.solver_stats.solver_name, "options": options,
                "status": problem.status, "fallback_reason": failure}
    return result, metadata
