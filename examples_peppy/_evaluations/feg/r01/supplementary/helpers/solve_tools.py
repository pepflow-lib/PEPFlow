"""Explicit solver selection using the approved generic framework API."""

import cvxpy as cp

import pepflow as pf


def solve_setup(ctx, pb, params):
    constraints = list(pb.init_conditions)
    for obj in list(ctx.func_to_triplets) + list(ctx.oper_to_duplets):
        constraints.extend(obj.get_interpolation_constraints(ctx))
    constraints = [c for c in constraints if c.name not in pb.relaxed_constraints]
    solver = pf.CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters=params)
    actual_options = {"solver": "CLARABEL"}
    try:
        value = problem.solve(**actual_options)
    except cp.error.SolverError:
        actual_options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**actual_options)
    result = pf.PEPResult(
        opt_value=value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=pf.PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    return result, actual_options
