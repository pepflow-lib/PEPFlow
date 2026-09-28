"""Run the one-time B1 sweep through the frozen framework's solver API."""
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
APPROVED = ROOT / "supplementary" / "approved"
RUNTIME = ROOT / "supplementary" / ".runtime"
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
for key in ("TEMP", "TMP", "TMPDIR", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"):
    path = RUNTIME / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
sys.path[:0] = [str(APPROVED), str(ROOT / "supplementary")]
import cvxpy as cp
import pepflow as pf
import sympy as sp

spec = importlib.util.spec_from_file_location("bppm_setup", ROOT / "bppm_setup.py")
assert spec is not None and spec.loader is not None
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
rows = []
for N in range(1, 8):
    ctx, pb, _ = setup.get_pep_setup(N, {})
    constraints = list(pb.init_conditions)
    for obj in ctx.func_to_triplets:
        constraints.extend(obj.get_interpolation_constraints(ctx))
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters={"alpha": sp.Integer(1), "R": sp.Integer(1)})
    attempts = []
    try:
        value = problem.solve(solver="CLARABEL")
        attempts.append({"solver": "CLARABEL", "options": {}, "status": problem.status})
    except cp.error.SolverError as exc:
        attempts.append({"solver": "CLARABEL", "options": {}, "error": str(exc)})
        value = problem.solve(solver="SCS", eps=1e-7, max_iters=200000)
        attempts.append({"solver": "SCS", "options": {"eps": 1e-7, "max_iters": 200000}, "status": problem.status})
    if problem.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(f"N={N}: {problem.status}")
    row = {"N": N, "opt_value": float(value), "conjectured": 1 / N,
           "absolute_error": abs(float(value) - 1 / N), "attempts": attempts,
           "solver": problem.solver_stats.solver_name}
    rows.append(row)
    print(json.dumps(row), flush=True)
(ROOT / "supplementary" / "_sweep_tmp.json").write_text(json.dumps(rows, indent=2))
(ROOT / "state").mkdir(exist_ok=True)
state = {"algo_name": "bppm", "problem_type": "convex_bregman", "obj_tag": "f",
         "params_json": '{"alpha": 1, "R": 1}', "performance_metric": "f(x_N)-f(x_star)",
         "initial_condition": "D_h(x_star,x_0) <= R", "conjectured_rate": "R/(alpha*N)",
         "setup_file": "bppm_setup.py", "sweep_results": rows, "N_verify": 4,
         "rate_match_atol": 1e-5, "rate_match": all(r["absolute_error"] < 1e-5 for r in rows),
         "framework_origin": pf.__file__, "presentation_policy": "evaluation-ancillary-v1"}
(ROOT / "state" / "bppm_b1.json").write_text(json.dumps(state, indent=2))
