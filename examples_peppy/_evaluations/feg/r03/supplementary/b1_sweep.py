from pathlib import Path
import os
import sys
ROOT = Path(__file__).resolve().parents[1]
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
for key in ("TEMP", "TMP", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR"):
    path = ROOT / "supplementary" / ".runtime" / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
sys.path[:0] = [str(ROOT / "supplementary" / "approved"), str(ROOT)]
import json
import cvxpy as cp
import pepflow as pf
from feg_setup import get_pep_setup

results = []
for n in range(1, 8):
    ctx, pb, op = get_pep_setup(n, {"L": 1, "R": 1})
    constraints = [*pb.init_conditions, *op.get_interpolation_constraints(ctx)]
    solver = pf.CVXPrimalSolver(perf_metric=pb.performance_metric, constraints=constraints, context=ctx)
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    attempts = []
    try:
        value = problem.solve(solver="CLARABEL")
        attempts.append({"solver": "CLARABEL", "options": {}, "status": problem.status})
        if problem.status not in ("optimal", "optimal_inaccurate"):
            raise cp.SolverError(problem.status)
    except cp.SolverError as exc:
        attempts.append({"solver": "CLARABEL", "error": str(exc)})
        value = problem.solve(solver="SCS", eps=1e-7, max_iters=200000)
        attempts.append({"solver": "SCS", "options": {"eps": 1e-7, "max_iters": 200000}, "status": problem.status})
    row = {"N": n, "opt_value": float(value), "status": problem.status, "attempts": attempts}
    results.append(row)
    print(json.dumps(row), flush=True)
    (ROOT / "supplementary" / "_sweep_tmp.json").write_text(json.dumps(results, indent=2))
print("origins", pf.__file__, cp.__file__)
