"""Attempt-owned runtime and explicit solver policy for the approved framework."""
import os
from pathlib import Path
import sys

ATTEMPT = Path(__file__).resolve().parents[2]
APPROVED = ATTEMPT / "supplementary" / "approved"
RUNTIME = ATTEMPT / "supplementary" / ".runtime"
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
for key in ("TEMP", "TMP", "TMPDIR", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"):
    location = RUNTIME / key.lower()
    location.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(location)
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path[:0] = [str(APPROVED), str(ATTEMPT), str(ATTEMPT / "supplementary" / "helpers")]


def solve_explicit(ctx, pb, params):
    import cvxpy as cp
    import pepflow as pf
    from pepflow.utils import PEPType

    constraints = list(pb.init_conditions)
    for obj in ctx.func_to_triplets:
        constraints.extend(obj.get_interpolation_constraints(ctx))
    constraints = [c for c in constraints if c.name not in pb.relaxed_constraints]
    solver = pf.CVXPrimalSolver(perf_metric=pb.performance_metric, constraints=constraints, context=ctx)
    problem = solver.build_problem(resolve_parameters=params)
    attempts = []
    try:
        value = problem.solve(solver="CLARABEL")
        attempts.append({"solver": "CLARABEL", "options": {}, "status": problem.status})
    except cp.error.SolverError as error:
        attempts.append({"solver": "CLARABEL", "options": {}, "error": str(error)})
        value = problem.solve(solver="SCS", eps=1e-7, max_iters=200000)
        attempts.append({"solver": "SCS", "options": {"eps": 1e-7, "max_iters": 200000}, "status": problem.status})
    if problem.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(f"Unsuccessful solve: {attempts}")
    result = pf.PEPResult(opt_value=value, dual_var_manager=solver.dual_var_manager,
                          pep_type=PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    return result, attempts

