import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("runtime.py")))
import json
import cvxpy as cp
import pepflow as pf
from pgm_setup import get_pep_setup

root = Path(__file__).resolve().parents[1]
results = json.loads((root / "supplementary" / "sweep.json").read_text())
for n in range(7, 8):
    ctx, pb, _ = get_pep_setup(n, {"L": 1, "R": 1})
    constraints = list(pb.init_conditions)
    for func in ctx.func_to_triplets:
        constraints.extend(func.get_interpolation_constraints(ctx))
    solver = pf.CVXPrimalSolver(perf_metric=pb.performance_metric, constraints=constraints, context=ctx)
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    options = {"solver": "CLARABEL"}
    try:
        value = problem.solve(**options)
    except cp.error.SolverError:
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    row = {"N": n, "opt_value": float(value), "status": problem.status, "solver_options": options}
    results.append(row)
    print(row, flush=True)
    (root / "supplementary" / "sweep.json").write_text(json.dumps(results, indent=2))
    assert problem.status in ("optimal", "optimal_inaccurate"), row

