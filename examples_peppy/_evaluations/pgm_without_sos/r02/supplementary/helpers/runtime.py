"""Attempt-local pinned runtime and explicit solver route."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPROVED = ROOT / "supplementary" / "approved"
RUNTIME = ROOT / "supplementary" / ".runtime"
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
for key in ("TEMP", "TMP", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR"):
    folder = RUNTIME / key.lower()
    folder.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(folder)
sys.path[:0] = [str(APPROVED), str(ROOT), str(ROOT / "supplementary")]


def solve_setup(ctx, pb, params):
    import cvxpy as cp
    import pepflow as pf
    constraints = list(pb.init_conditions)
    for fun in ctx.func_to_triplets:
        constraints.extend(fun.get_interpolation_constraints(ctx))
    constraints = [c for c in constraints if c.name not in pb.relaxed_constraints]
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=params)
    options = {"solver": "CLARABEL"}
    try:
        value = problem.solve(**options)
    except cp.error.SolverError:
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    result = pf.PEPResult(opt_value=value, dual_var_manager=solver.dual_var_manager,
                          pep_type=pf.PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    return result, options

