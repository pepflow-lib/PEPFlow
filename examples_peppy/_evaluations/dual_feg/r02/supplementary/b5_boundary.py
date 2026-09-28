# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_bound = pf.PEPContext("symbolic_bound").set_as_current()
A_bound = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{boundary}"], L=l_p)
x0_bound = pf.Vector(is_basis=True, tags=["x_{0,boundary}"])
X_bound = pf.Vector(is_basis=True, tags=["x_{N,boundary}"])
star_bound = A_bound.set_zero_point("x_{star,boundary}")
G_bound = A_bound(X_bound)
r_p = pf.Parameter("R_symbolic")
r_s = sp.Symbol("R", nonnegative=True)
V_bound = terminal_potential(X_bound, x0_bound, G_bound, l_p, n_p)
mon_bound = -(G_bound * (X_bound - star_bound))
initial_bound = (x0_bound - star_bound) ** 2 - r_p**2
square_bound = ((2 * l_p / n_p) * (x0_bound - star_bound) - G_bound) ** 2
bound_LHS = G_bound**2 - (4 * l_p**2 / n_p**2) * r_p**2
bound_RHS = (
    V_bound
    + (4 * l_p / n_p) * mon_bound
    - square_bound
    + (4 * l_p**2 / n_p**2) * initial_bound
)
pm_bound = pf.ExpressionManager(
    ctx_bound,
    resolve_parameters=cast(
        dict[str, pf.NUMERICAL_TYPE],
        {"N_symbolic": n_s, "L_symbolic": l_s, "R_symbolic": r_s},
    ),
)
bound_diff = bound_LHS - bound_RHS
boundary_passed = verify_exact(
    "Rate and initial-radius normalization", bound_diff, pm_bound
)
proof_checks["boundary"] = last_step_passed and boundary_passed
proof_checks["normalization"] = boundary_passed
