"""Attempt-local environment and explicit solver route."""

import os
import sys
from pathlib import Path

NOTEBOOK_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = NOTEBOOK_DIR / "supplementary" / "approved"


def configure():
    for key in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        os.environ[key] = "1"
    root = NOTEBOOK_DIR / "supplementary" / ".runtime"
    for key in (
        "TEMP",
        "TMP",
        "TMPDIR",
        "IPYTHONDIR",
        "MPLCONFIGDIR",
        "JUPYTER_RUNTIME_DIR",
        "JUPYTER_CONFIG_DIR",
        "XDG_CACHE_HOME",
    ):
        target = root / key.lower()
        target.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(target)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    for path in (NOTEBOOK_DIR, NOTEBOOK_DIR / "supplementary" / "helpers", REPO_ROOT):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def solve_pep(ctx, pb, obj, params):
    """Use framework model construction with the frozen solver settings."""
    import cvxpy as cp

    import pepflow as pf

    constraints = list(pb.init_conditions) + obj.get_interpolation_constraints(ctx)
    constraints = [c for c in constraints if c.name not in pb.relaxed_constraints]
    solver = pf.CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters=params)
    calls = []
    try:
        value = problem.solve(solver="CLARABEL")
        calls.append({"solver": "CLARABEL", "options": {}, "status": problem.status})
    except cp.error.SolverError as exc:
        calls.append({"solver": "CLARABEL", "options": {}, "error": str(exc)})
        value = problem.solve(solver="SCS", eps=1e-7, max_iters=200000)
        calls.append(
            {
                "solver": "SCS",
                "options": {"eps": 1e-7, "max_iters": 200000},
                "status": problem.status,
            }
        )
    if problem.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(f"Solver did not produce an optimum: {calls}")
    result = pf.PEPResult(
        opt_value=value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=pf.PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    return result, calls
