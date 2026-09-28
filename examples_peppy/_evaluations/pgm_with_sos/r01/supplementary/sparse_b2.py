import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np
import runtime
import sympy as sp
from pgm_setup import f, g, get_pep_setup

import pepflow as pf

N = 4
ctx, pb, obj = get_pep_setup(N, {"L": 1, "R": 1})
constraints = list(pb.init_conditions)
for owner in ctx.func_to_triplets:
    constraints.extend(owner.get_interpolation_constraints(ctx))
keep = []
for c in constraints:
    if c.name == "initial_condition":
        keep.append(c)
        continue
    ri, ci = c.name.split(":")[1].split(",")
    if ri == "x_star" or (
        ri != "x_star" and ci != "x_star" and int(ci[2:]) == int(ri[2:]) + 1
    ):
        keep.append(c)
solver = pf.CVXPrimalSolver(pb.performance_metric, keep, ctx)
problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
v = problem.solve(solver="CLARABEL")
result = pf.PEPResult(
    opt_value=v,
    dual_var_manager=solver.dual_var_manager,
    pep_type=pf.PEPType.PRIMAL,
    solver_status=problem.status,
    context=ctx,
)
S = np.asarray(result.get_gram_dual_matrix().matrix, dtype=float)
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": 1, "R": 1})
a_star = f.grad(ctx["x_star"])
aid = pf.Scalar.zero()
for j in range(1, N + 1):
    i, n = sp.S(j), sp.S(N)
    xprev, x = ctx[f"x_{j - 1}"], ctx[f"x_{j}"]
    ap, a = f.grad(xprev), f.grad(x)
    s = g.grad(x)
    c1 = n / ((2 * n + 1 - i) * (2 * n - i))
    u1 = i / (2 * n) * a + (2 * n - i) / (2 * n) * ap - a_star
    c2 = (
        (i - 1) / (2 * n - i) * (2 * n + 2) / (2 * n + 1)
        + 2 * n / ((2 * n - i) ** 2 * (2 * n + 1))
    ) / 2
    u2 = ap + s - (xprev - ctx["x_star"]) / (2 * n + 1 - i)
    c3 = i / (2 * n + 1 - i) * (2 * n) / (2 * n + 1) / 2
    u3 = (
        (2 * n + 1) / (2 * n) * (a + s)
        - (ap + s) / (2 * n)
        - (x - ctx["x_star"]) / (2 * n - i)
    )
    aid += c1 * u1**2 + c2 * u2**2 + c3 * u3**2
A = np.asarray(pm.eval_scalar(aid).inner_prod_coords, dtype=float)
scale = float(np.sum(S * A) / np.sum(A * A))
print("value/status", v, problem.status)
for c in keep:
    print(c.name, result.get_dual_value(c.name))
print("aid normalized fit", scale, "max residual", np.max(abs(S - scale * A)))
data = dict(
    N=N,
    opt_value=float(v),
    status=problem.status,
    duals={c.name: float(result.get_dual_value(c.name)) for c in keep},
    dropped=[c.name for c in constraints if c not in keep],
    S_matrix=S.tolist(),
    aid_scale=scale,
    aid_residual=float(np.max(abs(S - scale * A))),
)
(runtime.ATTEMPT / "supplementary/b2-sparse-explore.json").write_text(
    json.dumps(data, indent=2)
)
