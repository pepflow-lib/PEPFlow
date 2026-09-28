# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Base uses no g(x_0), so x_0 need not belong to dom(g).
f_base = pf.SmoothConvexFunction(is_basis=True, tags=["f_{base}"], L=Lpar)
g_base = pf.ConvexFunction(is_basis=True, tags=["g_{base}"])
ctx_base = pf.PEPContext("symbolic_base").set_as_current()
star = (f_base + g_base).set_stationary_point("x_{star}")
x = pf.Vector(is_basis=True, tags=["x_{0}"])
y = g_base.prox(x - f_base.grad(x) / Lpar, 1 / Lpar, tag="x_{1}")
f_base(y)
d = x - star
p = (f_base.grad(x) - f_base.grad(star)) / Lpar
z = (f_base.grad(y) - f_base.grad(star)) / Lpar
q = (g_base.grad(y) + f_base.grad(star)) / Lpar
w = q - P("inv_m") * d
If0 = (
    f_base(x)
    - f_base(star)
    - f_base.grad(x) * d
    + (f_base.grad(x) - f_base.grad(star)) ** 2 / (2 * Lpar)
)
If1 = (
    f_base(y)
    - f_base(star)
    - f_base.grad(y) * (y - star)
    + (f_base.grad(y) - f_base.grad(star)) ** 2 / (2 * Lpar)
)
If01 = (
    f_base(y)
    - f_base(x)
    + f_base.grad(y) * (x - y)
    + (f_base.grad(x) - f_base.grad(y)) ** 2 / (2 * Lpar)
)
Ig1 = g_base(y) - g_base(star) - g_base.grad(y) * (y - star)
LHS = (
    -P("tau") * d**2
    + P("alpha_next") * (y - star) ** 2
    - P("inv_m_next") * (y - star) * f_base.grad(y)
    - P("t_next") * (f_base.grad(y) - f_base.grad(star)) ** 2
    + P("a_next") * (f_base(y) - f_base(star))
    + P("b_next") * (g_base(y) - g_base(star))
)
Qbase = Lpar * (
    P("A") * (z + P("r") * (w + P("inv_m") * p)) ** 2 + P("B") * (w + P("c") * p) ** 2
)
RHS = (
    P("a_current") * If0
    - P("tau") * p**2
    + (P("a_next") - P("a_current")) * If1
    + P("a_current") * If01
    + P("b_next") * Ig1
    - Qbase
)
params_base: dict[str, Any] = {
    name: sp.sympify(value).subs(k_symbol, 0) for name, value in params_step.items()
}
params_base["tau"] = L_symbol / (4 * N_symbol)
pm_base = pf.ExpressionManager(ctx_base, resolve_parameters=params_base)
diff = LHS - RHS
base_verified = exact_check("Base V_1<=V_0=0, N>=2", diff, pm_base, ctx_base)
