"""Run Block 1 once with explicit solver policy."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for key in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]:
    os.environ[key] = "1"
for key in [
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
]:
    path = ROOT / "supplementary" / ".runtime" / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
sys.path[:0] = [str(ROOT / "supplementary" / "approved"), str(ROOT)]
import cvxpy as cp  # noqa: E402 - imports follow runtime or notebook setup
from dual_feg_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

from pepflow.solver import (  # noqa: E402 - imports follow runtime or notebook setup
    CVXPrimalSolver,
)

results = []
for N in range(1, 8):
    ctx, pb, A = get_pep_setup(N, {"L": 1, "R": 1})
    cons = [*pb.init_conditions, *A.get_interpolation_constraints(ctx)]
    solver = CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=cons, context=ctx
    )
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    options = {"solver": "CLARABEL"}
    try:
        value = problem.solve(**options)
    except cp.error.SolverError:
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    row = {
        "N": N,
        "opt_value": float(value),
        "status": problem.status,
        "options": options,
    }
    results.append(row)
    print(json.dumps(row), flush=True)
    (ROOT / "supplementary" / "_sweep_tmp.json").write_text(
        json.dumps(results, indent=2)
    )
