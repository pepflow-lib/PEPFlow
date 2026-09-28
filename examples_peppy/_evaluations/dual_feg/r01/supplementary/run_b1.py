import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime
import json
import pepflow as pf
from dual_feg_setup import get_pep_setup

results = []
for n in range(1, 8):
    ctx, pb, op = get_pep_setup(n, {"L": 1, "R": 1})
    constraints = [*pb.init_conditions, *op.get_interpolation_constraints(ctx)]
    solver = pf.CVXPrimalSolver(perf_metric=pb.performance_metric, constraints=constraints, context=ctx)
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    options = {"solver": "CLARABEL"}
    try:
        value = problem.solve(**options)
    except Exception as error:
        print(f"CLARABEL failure: {error}", flush=True)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    record = {"N": n, "opt_value": value, "status": problem.status, "solver_options": options}
    results.append(record)
    print(record, flush=True)
    (runtime.ATTEMPT / "supplementary" / "b1_sweep.json").write_text(json.dumps(results, indent=2))
