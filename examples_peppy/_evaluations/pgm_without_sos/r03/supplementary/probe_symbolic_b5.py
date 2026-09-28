import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("runtime.py")))
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup

exec(
    compile(
        Path("supplementary/b5_coeff_formula.py").read_text(encoding="utf-8-sig"),
        "formula",
        "exec",
    )
)
# Auxiliary symbolic one-step PEPFlow context, distinct from numerical objects.
k, N, Lsym = sp.symbols("k N L", positive=True)
U = sp.symbols("U", nonnegative=True)
m = 2 * N - k
H = U + (k + 2) * (m - 1)
D = ((2 * k + 1) * m - k) * U + (m - 1) * (k * (k + 3) * m + m + 1)
T = k * (k + 1) * (m - 1) * (m * U + (m - 1) * (k + m + 1)) / D
r = (k + 1) * (m - 1) / H
c = (m * H * (k * m + 1) - (k + 1) ** 2 * (m - 1) ** 2) / (m * D)
A = H / (2 * (m - 1) ** 2)
B = D / (2 * (m - 1) ** 2 * H)
Lpar = pf.Parameter("L_symbolic")
f_step = pf.SmoothConvexFunction(is_basis=True, tags=["f_{step}"], L=Lpar)
g_step = pf.ConvexFunction(is_basis=True, tags=["g_{step}"])
h_step = f_step + g_step
ctx_step = pf.PEPContext("symbolic_step").set_as_current()
star = h_step.set_stationary_point("x_{star}")
x = pf.Vector(is_basis=True, tags=["x_{k}"])
y = g_step.prox(x - f_step.grad(x) / Lpar, 1 / Lpar, tag="x_{k+1}")
g_step(x)
f_step(y)
d = x - star
p = (f_step.grad(x) - f_step.grad(star)) / Lpar
z = (f_step.grad(y) - f_step.grad(star)) / Lpar
q = (g_step.grad(y) + f_step.grad(star)) / Lpar
w = q - pf.Parameter("inv_m") * d
P = lambda name: pf.Parameter(name)  # noqa: E731 - retain the archived notebook helper
Vcur = (
    P("alpha") * d**2
    - P("inv_m") * d * f_step.grad(x)
    - P("t_current") * (f_step.grad(x) - f_step.grad(star)) ** 2
    + P("a_current") * (f_step(x) - f_step(star))
    + P("b_current") * (g_step(x) - g_step(star))
)
Vnext = (
    P("alpha_next") * (y - star) ** 2
    - P("inv_m_next") * (y - star) * f_step.grad(y)
    - P("t_next") * (f_step.grad(y) - f_step.grad(star)) ** 2
    + P("a_next") * (f_step(y) - f_step(star))
    + P("b_next") * (g_step(y) - g_step(star))
)
Ifstar = (
    f_step(y)
    - f_step(star)
    + f_step.grad(y) * (star - y)
    + (f_step.grad(star) - f_step.grad(y)) ** 2 / (2 * Lpar)
)
Ifpair = (
    f_step(y)
    - f_step(x)
    + f_step.grad(y) * (x - y)
    + (f_step.grad(x) - f_step.grad(y)) ** 2 / (2 * Lpar)
)
Igstar = g_step(y) - g_step(star) + g_step.grad(y) * (star - y)
Igpair = g_step(y) - g_step(x) + g_step.grad(y) * (x - y)
Q = Lpar * (
    P("A") * (z + P("r") * (w + P("inv_m") * p)) ** 2 + P("B") * (w + P("c") * p) ** 2
)
LHS = Vnext - Vcur
RHS = (
    (P("a_next") - P("a_current")) * Ifstar
    + P("a_current") * Ifpair
    + (P("b_next") - P("b_current")) * Igstar
    + P("b_current") * Igpair
    - Q
)
params = {
    "L_symbolic": Lsym,
    "alpha": Lsym * (N - k) / m**2,
    "alpha_next": Lsym * (N - k - 1) / (m - 1) ** 2,
    "inv_m": 1 / m,
    "inv_m_next": 1 / (m - 1),
    "t_current": T / (2 * Lsym * m**2),
    "t_next": U / (2 * Lsym * (m - 1) ** 2),
    "a_current": (k + 1) / m,
    "b_current": k / m,
    "a_next": (k + 2) / (m - 1),
    "b_next": (k + 1) / (m - 1),
    "A": A,
    "B": B,
    "r": r,
    "c": c,
}
pm_step = pf.ExpressionManager(ctx_step, resolve_parameters=params)
diff = LHS - RHS
value = pm_step.eval_scalar(diff, sympy_mode=True)
parts = [
    sp.Matrix(value.inner_prod_coords).applyfunc(sp.factor),
    sp.Matrix(value.func_coords).applyfunc(sp.factor),
    sp.factor(value.offset),
]
print("Symbolic step residual:", parts)
assert all(v == 0 for matrix in parts[:2] for v in matrix) and parts[2] == 0
