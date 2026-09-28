"""Attempt-local environment and explicit solver policy."""
import os
import sys
from pathlib import Path

NOTEBOOK_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = NOTEBOOK_DIR / "supplementary" / "approved"


def configure():
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = "1"
    for name in ("TEMP", "TMP", "TMPDIR", "IPYTHONDIR", "MPLCONFIGDIR",
                 "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"):
        folder = NOTEBOOK_DIR / "supplementary" / ".runtime" / name.lower()
        folder.mkdir(parents=True, exist_ok=True)
        os.environ[name] = str(folder)
    sys.path[:0] = [str(REPO_ROOT), str(NOTEBOOK_DIR),
                    str(NOTEBOOK_DIR / "supplementary" / "helpers")]


def solve_explicit(ctx, pb, params):
    from pepflow.solver import CVXPrimalSolver
    from pepflow.pep_result import PEPResult
    from pepflow.utils import PEPType
    import cvxpy as cp
    constraints = list(pb.init_conditions)
    for func in ctx.func_to_triplets:
        constraints.extend(func.get_interpolation_constraints(ctx))
    constraints = [c for c in constraints if c.name not in pb.relaxed_constraints]
    solver = CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=params)
    options = {"solver": "CLARABEL"}
    failures = []
    try:
        value = problem.solve(**options)
    except cp.error.SolverError as exc:
        failures.append(str(exc))
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    result = PEPResult(value, solver.dual_var_manager, PEPType.PRIMAL,
                       problem.status, ctx)
    return result, {"status": problem.status, "options": options,
                    "failures": failures, "solver": problem.solver_stats.solver_name}

