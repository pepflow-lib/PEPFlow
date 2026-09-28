import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "attempt_runtime", root / "supplementary/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)

import cvxpy as cp  # noqa: E402 - imports follow runtime or notebook setup
from ogm_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
    theta_sequence,
)

from pepflow.solver import (  # noqa: E402 - imports follow runtime or notebook setup
    CVXPrimalSolver,
)

results = []
for N in range(1, 8):
    ctx, pb, f = get_pep_setup(N, {"L": 1, "R": 1})
    constraints = list(pb.init_conditions)
    constraints.extend(f.get_interpolation_constraints(ctx))
    solver = CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    options = {"solver": "CLARABEL"}
    try:
        value = problem.solve(**options)
    except cp.SolverError:
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    row = {
        "N": N,
        "opt_value": float(value),
        "theta_N": theta_sequence(N)[-1],
        "status": problem.status,
        "solver": problem.solver_stats.solver_name,
        "options": options,
    }
    results.append(row)
    print(json.dumps(row), flush=True)
    (root / "supplementary/_sweep_tmp.json").write_text(json.dumps(results, indent=2))
