"""Attempt-owned B1 sweep with explicit frozen solver policy."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVED = ROOT / "supplementary" / "approved"
RUNTIME = ROOT / "supplementary" / ".runtime"
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
for variable in ("TEMP", "TMP", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR"):
    folder = RUNTIME / variable.lower()
    folder.mkdir(parents=True, exist_ok=True)
    os.environ[variable] = str(folder)
sys.path[:0] = [str(APPROVED), str(ROOT), str(ROOT / "supplementary")]

import cvxpy as cp
import pepflow as pf
import pgm_setup as setup

results = []
for horizon in range(1, 8):
    ctx, pb, _ = setup.get_pep_setup(horizon, {"L": 1, "R": 1})
    constraints = list(pb.init_conditions)
    for function in ctx.func_to_triplets:
        constraints.extend(function.get_interpolation_constraints(ctx))
    assert pb.performance_metric is not None
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    options = {"solver": "CLARABEL"}
    failure = None
    try:
        value = problem.solve(**options)
    except cp.error.SolverError as exc:
        failure = str(exc)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    if problem.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(f"N={horizon}: {problem.status}")
    record = {"N": horizon, "opt_value": value, "status": problem.status,
              "solver_options": options, "solver_failure": failure}
    results.append(record)
    print(json.dumps(record), flush=True)
(ROOT / "supplementary" / "b1_sweep.json").write_text(json.dumps(results, indent=2))
