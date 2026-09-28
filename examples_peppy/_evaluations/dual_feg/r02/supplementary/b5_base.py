# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_base = pf.PEPContext("symbolic_base").set_as_current()
A_base = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{base}"], L=l_p)
x0_base = pf.Vector(is_basis=True, tags=["x_{0,base}"])
X_base = pf.Vector(is_basis=True, tags=["x_{N,base}"])
G_base = A_base(X_base)
g0_base = A_base(x0_base)
z0_base = pf.Vector.zero()
y0_base = (x0_base - g0_base / l_p).add_tag("y_{0,base}")
h0_base = A_base(y0_base)
x1_base = y0_base - ((n_p - 1) / n_p) * (h0_base - g0_base) / l_p
z1_base = -h0_base / n_p
base_LHS = potential(n_p - 1, x1_base, z1_base, X_base, x0_base, G_base, l_p, n_p)
base_RHS = (2 / n_p**2) * (
    (g0_base - h0_base) ** 2 - l_p**2 * (x0_base - y0_base) ** 2
) + (4 * l_p / (n_p * (n_p - 1))) * (-(G_base - h0_base) * (X_base - y0_base))
pm_base = pf.ExpressionManager(
    ctx_base,
    resolve_parameters=cast(
        dict[str, pf.NUMERICAL_TYPE], {"N_symbolic": n_s, "L_symbolic": l_s}
    ),
)
base_initial = verify_exact(
    "Initial V0=0",
    potential(n_p, x0_base, z0_base, X_base, x0_base, G_base, l_p, n_p),
    pm_base,
)
base_diff = base_LHS - base_RHS
proof_checks["base"] = (
    verify_exact("Base first step (N>=2)", base_diff, pm_base) and base_initial
)
