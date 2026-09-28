"""Attempt-local execution environment and explicitly configured solver."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPROVED = ROOT / "supplementary" / "approved"
for name in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[name] = "1"
for name in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    directory = ROOT / "supplementary" / ".runtime" / name.lower()
    directory.mkdir(parents=True, exist_ok=True)
    os.environ[name] = str(directory)
sys.path[:0] = [str(APPROVED), str(ROOT), str(ROOT / "supplementary" / "helpers")]


def solve_builder(ctx, pb, params):
    import cvxpy as cp

    import pepflow as pf

    constraints = list(pb.init_conditions)
    for obj in ctx.func_to_triplets:
        constraints.extend(obj.get_interpolation_constraints(ctx))
    constraints = [c for c in constraints if c.name not in pb.relaxed_constraints]
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=params)
    options = {"solver": "CLARABEL"}
    failure = None
    try:
        value = problem.solve(**options)
        if problem.status not in ("optimal", "optimal_inaccurate"):
            raise RuntimeError(problem.status)
    except (cp.error.SolverError, RuntimeError) as exc:
        failure = str(exc)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    result = pf.PEPResult(
        opt_value=value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=pf.PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    return result, {
        "status": problem.status,
        "solver_options": options,
        "fallback_reason": failure,
        "solver_name": problem.solver_stats.solver_name,
    }
