"""Fresh B1 sweep with explicit solver and private runtime configuration."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "MPLCONFIGDIR",
    "IPYTHONDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    private = ROOT / "supplementary" / ".runtime" / key.lower()
    private.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(private)
sys.path[:0] = [str(ROOT / "supplementary" / "approved"), str(ROOT)]

import cvxpy as cp  # noqa: E402 - imports follow runtime or notebook setup
from dual_feg_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

from pepflow.solver import (  # noqa: E402 - imports follow runtime or notebook setup
    CVXPrimalSolver,
)

results = []
for n in range(1, 8):
    ctx, pb, operator = get_pep_setup(n, {"L": 1, "R": 1})
    constraints = [*pb.init_conditions, *operator.get_interpolation_constraints(ctx)]
    solver = CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    options = {"solver": "CLARABEL"}
    failures = []
    try:
        val = problem.solve(**options)
    except cp.error.SolverError as exc:
        failures.append(str(exc))
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        val = problem.solve(**options)
    result = {
        "N": n,
        "opt_value": float(val),
        "solver_status": problem.status,
        "solver_options": options,
        "solver_failures": failures,
    }
    results.append(result)
    print(json.dumps(result), flush=True)
    (ROOT / "supplementary" / "_sweep_tmp.json").write_text(
        json.dumps(results, indent=2)
    )
