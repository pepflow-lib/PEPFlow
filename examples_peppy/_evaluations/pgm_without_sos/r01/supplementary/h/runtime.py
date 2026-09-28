"""Attempt-local runtime and explicit solver settings."""

import os
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
        path = NOTEBOOK_DIR / "supplementary" / ".runtime" / key.lower()
        path.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(path)


def solve_setup(ctx, pb, params):
    import cvxpy as cp

    import pepflow as pf

    constraints = list(pb.init_conditions)
    for func in ctx.func_to_triplets:
        constraints.extend(func.get_interpolation_constraints(ctx))
    constraints = [c for c in constraints if c.name not in pb.relaxed_constraints]
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=params)
    options = {"solver": "CLARABEL"}
    failures = []
    try:
        problem.solve(**options)
        if problem.status not in ("optimal", "optimal_inaccurate"):
            raise RuntimeError(problem.status)
    except (cp.error.SolverError, RuntimeError) as exc:
        failures.append(str(exc))
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        problem.solve(**options)
    result = pf.PEPResult(
        opt_value=problem.value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=pf.PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    return result, {"options": options, "status": problem.status, "failures": failures}
