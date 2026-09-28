# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_small = pf.PEPContext("symbolic_small").set_as_current()
L_small = pf.Parameter("L_symbolic")
f_small = pf.SmoothConvexFunction(is_basis=True, tags=["f_{small}"], L=L_small)
g_small = pf.ConvexFunction(is_basis=True, tags=["g_{small}"])
xs_small = (f_small + g_small).set_stationary_point("x_{star}")
x0_small = pf.Vector(is_basis=True, tags=["x_{0}"])
x1_small = g_small.prox(
    x0_small - f_small.grad(x0_small) / L_small, 1 / L_small, tag="x_{1}"
)
LHS_small = (
    f_small(x1_small)
    - f_small(xs_small)
    + g_small(x1_small)
    - g_small(xs_small)
    - L_small / 4 * (x0_small - xs_small) ** 2
)
RHS_small = smooth_residual(f_small, xs_small, x0_small, L_small) / 2
RHS_small += local_contribution(
    f_small,
    g_small,
    x0_small,
    x1_small,
    xs_small,
    sp.S.One,
    sp.S.One,
    L_small,
    terminal=True,
    include_previous_g=False,
)
diff_small = LHS_small - RHS_small
pm_small = pf.ExpressionManager(
    ctx_small, resolve_parameters={"L_symbolic": ell_symbol}
)
small_verified = verify_identity("Exceptional horizon N=1", diff_small, pm_small)
