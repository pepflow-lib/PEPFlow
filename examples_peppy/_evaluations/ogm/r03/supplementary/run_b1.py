"""Run the initial numerical sweep using the approved PEPFlow solver API."""

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
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_CONFIG_DIR",
    "JUPYTER_RUNTIME_DIR",
):
    directory = ROOT / "supplementary" / ".runtime" / key.lower()
    directory.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(directory)
sys.path[:0] = [str(ROOT / "supplementary" / "approved"), str(ROOT)]

import cvxpy as cp  # noqa: E402
import sympy as sp  # noqa: E402
from ogm_setup import get_pep_setup, theta_sequence  # noqa: E402

import pepflow as pf  # noqa: E402

results = []
for n in range(1, 8):
    ctx, pb, f = get_pep_setup(n, {"L": 1, "R": 1})
    constraints = [*pb.init_conditions, *f.get_interpolation_constraints(ctx)]
    assert pb.performance_metric is not None
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(
        resolve_parameters={"L": sp.Integer(1), "R": sp.Integer(1)}
    )
    attempts = []
    try:
        value = problem.solve(solver="CLARABEL")
        attempts.append({"solver": "CLARABEL", "options": {}, "status": problem.status})
    except cp.SolverError as error:
        attempts.append({"solver": "CLARABEL", "options": {}, "error": str(error)})
        value = None
    if problem.status != "optimal":
        value = problem.solve(solver="SCS", eps=1e-7, max_iters=200000)
        attempts.append(
            {
                "solver": "SCS",
                "options": {"eps": 1e-7, "max_iters": 200000},
                "status": problem.status,
            }
        )
    if problem.status != "optimal":
        raise RuntimeError(f"Unsuccessful solve at N={n}: {problem.status}")
    assert value is not None
    result = {
        "N": n,
        "opt_value": float(value),
        "theta_N": theta_sequence(n)[-1],
        "solve_attempts": attempts,
    }
    results.append(result)
    print(json.dumps(result), flush=True)
(ROOT / "supplementary" / "b1_sweep.json").write_text(json.dumps(results, indent=2))
