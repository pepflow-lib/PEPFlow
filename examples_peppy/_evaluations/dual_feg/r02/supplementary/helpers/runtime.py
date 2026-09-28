"""Attempt-owned runtime configuration and explicit solver selection."""
import os
import sys
from pathlib import Path

NOTEBOOK_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = NOTEBOOK_DIR / "supplementary" / "approved"
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
for key in ("TEMP", "TMP", "TMPDIR", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"):
    folder = NOTEBOOK_DIR / "supplementary" / ".runtime" / key.lower()
    folder.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(folder)
sys.path[:0] = [str(REPO_ROOT), str(NOTEBOOK_DIR), str(NOTEBOOK_DIR / "supplementary" / "helpers")]


def solve_setup(ctx, pb, obj, params):
    import cvxpy as cp
    import pepflow as pf
    assert pb.performance_metric is not None
    constraints = list(pb.init_conditions) + obj.get_interpolation_constraints(ctx)
    constraints = [c for c in constraints if c.name not in pb.relaxed_constraints]
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=params)
    options = {"solver": "CLARABEL"}
    failures = []
    try:
        value = problem.solve(**options)
    except cp.error.SolverError as exc:
        failures.append(str(exc))
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    result = pf.PEPResult(opt_value=value, dual_var_manager=solver.dual_var_manager,
                          pep_type=pf.PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    return result, {"solver": problem.solver_stats.solver_name, "options": options, "status": problem.status, "failures": failures}

