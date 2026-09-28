"""Attempt-owned environment and explicit solver selection using approved APIs."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPROVED = ROOT / "supplementary" / "approved"
RUNTIME = ROOT / "supplementary" / ".runtime"


def configure():
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    for key in ("TEMP", "TMP", "TMPDIR", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"):
        path = RUNTIME / key.lower()
        path.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(path)
    sys.path[:0] = [str(APPROVED), str(ROOT), str(ROOT / "supplementary" / "helpers")]


def solve_selected(ctx, pb, params):
    import cvxpy as cp
    import pepflow as pf
    constraints = list(pb.init_conditions)
    for func in ctx.func_to_triplets:
        constraints.extend(func.get_interpolation_constraints(ctx))
    constraints = [c for c in constraints if c.name not in pb.relaxed_constraints]
    solver = pf.CVXPrimalSolver(perf_metric=pb.performance_metric, constraints=constraints, context=ctx)
    problem = solver.build_problem(resolve_parameters=params)
    log = []
    try:
        value = problem.solve(solver="CLARABEL")
        log.append({"solver": "CLARABEL", "options": {}, "status": problem.status})
        if problem.status not in ("optimal", "optimal_inaccurate"):
            raise cp.error.SolverError(problem.status)
    except cp.error.SolverError as exc:
        log.append({"solver": "CLARABEL", "failure": str(exc)})
        value = problem.solve(solver="SCS", eps=1e-7, max_iters=200000)
        log.append({"solver": "SCS", "options": {"eps": 1e-7, "max_iters": 200000}, "status": problem.status})
    result = pf.PEPResult(opt_value=value, dual_var_manager=solver.dual_var_manager,
                          pep_type=pf.PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    return result, log

