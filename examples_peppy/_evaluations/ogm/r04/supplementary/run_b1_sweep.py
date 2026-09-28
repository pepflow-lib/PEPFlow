import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import configure  # ty: ignore[unresolved-import]

attempt, approved = configure()
import json  # noqa: E402 - imports follow runtime or notebook setup

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
    constraints = list(pb.init_conditions) + f.get_interpolation_constraints(ctx)
    solver = CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    options = {"solver": "CLARABEL"}
    failure = None
    try:
        value = problem.solve(**options)
    except cp.error.SolverError as exc:
        failure = str(exc)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    row = {
        "N": N,
        "opt_value": float(value),
        "status": problem.status,
        "solver_options": options,
        "solver_failure": failure,
        "theta_N": theta_sequence(N)[-1],
    }
    results.append(row)
    print(json.dumps(row), flush=True)
(attempt / "supplementary" / "_sweep_tmp.json").write_text(
    json.dumps(results, indent=2)
)
