# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Initial auxiliary potential Phi_0, with theta_0=1 and z_0=x_0.
base_ctx = pf.PEPContext("ogm_symbolic_base").set_as_current()
base_f = pf.SmoothConvexFunction(is_basis=True, tags=["f_{base}"], L=L_proof)
base_x = pf.Vector(is_basis=True, tags=["x_{0}"])
base_f.set_stationary_point("x_{star}")
base_star = base_ctx["x_{star}"]
base_g = base_f.grad(base_x)
base_z1 = base_x - 2 / L_proof * base_g
base_initial = L_proof / 2 * (base_x - base_star) ** 2
base_Phi0 = (
    2 * (base_f(base_x) - base_f(base_star))
    - base_g**2 / L_proof
    + L_proof / 2 * (base_z1 - base_star) ** 2
)
base_LHS = base_Phi0 - base_initial
base_RHS = 2 * interpolation_residual(base_f, base_star, base_x)
base_diff = base_LHS - base_RHS
base_pm = pf.ExpressionManager(base_ctx, resolve_parameters={"L_proof": ell_sym})
symbolic_results["base"] = assert_exact(
    "Initial identity", base_diff, base_pm, base_ctx
)
