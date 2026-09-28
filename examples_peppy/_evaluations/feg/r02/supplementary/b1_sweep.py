import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("runtime.py")))
import json
import sympy as sp
import pepflow as pf
from feg_setup import get_pep_setup

root = Path(__file__).resolve().parents[1]
results = []
for n in range(1, 8):
    ctx, pb, op = get_pep_setup(n, {})
    assert ctx["x_0"] is ctx["x_1/2"]
    constraints = list(pb.init_conditions) + op.get_interpolation_constraints(ctx)
    solver = pf.CVXPrimalSolver(perf_metric=pb.performance_metric, constraints=constraints, context=ctx)
    problem = solver.build_problem(resolve_parameters={"L": sp.Integer(1), "R": sp.Integer(1)})
    options = {"solver": "CLARABEL"}
    try:
        value = problem.solve(**options)
    except Exception as exc:
        print("CLARABEL failure", repr(exc), flush=True)
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        value = problem.solve(**options)
    row = {"N": n, "opt_value": value, "status": problem.status, "solver_options": options, "basis_dimension": len(ctx.basis_vectors())}
    results.append(row)
    print(row, flush=True)
(root / "supplementary" / "_sweep_tmp.json").write_text(json.dumps(results, indent=2))
