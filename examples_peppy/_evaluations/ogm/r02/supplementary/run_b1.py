"""B1 sweep using approved PEPFlow sources and explicit solver settings."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVED = ROOT / "supplementary" / "approved"
RUNTIME = ROOT / "supplementary" / ".runtime"
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
    "IPYTHONDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "MPLCONFIGDIR",
    "XDG_CACHE_HOME",
]:
    location = RUNTIME / key.lower()
    location.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(location)
sys.path[:0] = [str(APPROVED), str(ROOT), str(ROOT / "supplementary")]

import cvxpy as cp  # noqa: E402
import sympy as sp  # noqa: E402
from ogm_setup import get_pep_setup, theta_sequence  # noqa: E402

import pepflow as pf  # noqa: E402

results = []
for N in range(1, 8):
    ctx, pb, f = get_pep_setup(N, {"L": 1, "R": 1})
    constraints = list(pb.init_conditions)
    constraints.extend(f.get_interpolation_constraints(ctx))
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(
        resolve_parameters={"L": sp.Integer(1), "R": sp.Integer(1)}
    )
    options = {"solver": "CLARABEL"}
    failure = None
    try:
        value = problem.solve(**options)
        if problem.status not in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE):
            raise RuntimeError(f"CLARABEL status: {problem.status}")
    except (cp.SolverError, RuntimeError) as exc:
        failure = repr(exc)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    if value is None or problem.status not in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE):
        raise RuntimeError(f"Unusable solve at N={N}: {problem.status}")
    theta = theta_sequence(N)
    record = {
        "N": N,
        "opt_value": float(value),
        "theta_N": theta[-1],
        "status": problem.status,
        "solver": problem.solver_stats.solver_name,
        "options": options,
        "fallback_reason": failure,
        "theta_squared_times_opt": float(value) * theta[-1] ** 2,
    }
    results.append(record)
    (ROOT / "supplementary" / "_sweep_tmp.json").write_text(
        json.dumps(results, indent=2)
    )
    print(json.dumps(record), flush=True)

print(json.dumps({"framework_origin": pf.__file__, "completed": len(results)}))
