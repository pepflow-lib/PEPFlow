"""Attempt-local environment, solver policy, and notebook execution helpers."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
APPROVED = ROOT / "supplementary" / "approved"
RUNTIME = ROOT / "supplementary" / ".runtime"
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[name] = "1"
for name in ("TEMP", "TMP", "TMPDIR", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"):
    directory = RUNTIME / name.lower()
    directory.mkdir(parents=True, exist_ok=True)
    os.environ[name] = str(directory)
sys.path[:0] = [str(APPROVED), str(ROOT), str(ROOT / "supplementary")]


def solve_builder(ctx, pb, params):
    import cvxpy as cp
    from pepflow.solver import CVXPrimalSolver
    constraints = list(pb.init_conditions)
    for obj in ctx.func_to_triplets:
        constraints.extend(obj.get_interpolation_constraints(ctx))
    constraints = [c for c in constraints if c.name not in pb.relaxed_constraints]
    solver = CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=params)
    options = {"solver": "CLARABEL"}
    try:
        problem.solve(**options)
    except cp.error.SolverError:
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        problem.solve(**options)
    return problem, solver, options

