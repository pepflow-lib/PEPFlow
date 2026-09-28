"""Attempt-local Block 1 sweep using the approved framework API."""

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
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
]:
    dest = RUNTIME / key.lower()
    dest.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(dest)
sys.path[:0] = [str(APPROVED), str(ROOT), str(ROOT / "supplementary")]

import cvxpy as cp  # noqa: E402 - imports follow runtime or notebook setup
from dual_feg_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup


def sweep():
    results = []
    for n in range(1, 8):
        ctx, pb, operator = get_pep_setup(n, {"L": 1, "R": 1})
        constraints = list(pb.init_conditions) + operator.get_interpolation_constraints(
            ctx
        )
        solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
        problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
        solver_name, options, failure = "CLARABEL", {}, None
        try:
            value = problem.solve(solver=solver_name, **options)
            if problem.status not in ["optimal", "optimal_inaccurate"]:
                raise RuntimeError(problem.status)
        except (cp.error.SolverError, RuntimeError) as exc:
            failure = str(exc)
            solver_name, options = "SCS", {"eps": 1e-7, "max_iters": 200000}
            value = problem.solve(solver=solver_name, **options)
        result = {
            "N": n,
            "opt_value": value,
            "solver": solver_name,
            "options": options,
            "solver_status": problem.status,
            "fallback_reason": failure,
        }
        results.append(result)
        print(json.dumps(result), flush=True)
        (ROOT / "supplementary" / "b1_sweep.json").write_text(
            json.dumps(results, indent=2)
        )
    return results


if __name__ == "__main__":
    sweep()
