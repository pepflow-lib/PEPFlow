import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "runtime", Path(__file__).parent / "helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)

import cvxpy as cp  # noqa: E402 - imports follow runtime or notebook setup
from feg_setup import (  # noqa: E402 - imports follow runtime or notebook setup
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
    failure = None
    try:
        value = problem.solve(**options)
    except cp.error.SolverError as error:
        failure = str(error)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    row = {
        "N": n,
        "opt_value": float(value),
        "status": problem.status,
        "solver": problem.solver_stats.solver_name,
        "options": options,
        "failure": failure,
        "first_half_same_point": ctx["x_0"] is ctx["x_1/2"],
    }
    results.append(row)
    print(row, flush=True)
    (runtime.ROOT / "supplementary" / "_sweep_tmp.json").write_text(
        json.dumps(results, indent=2)
    )
