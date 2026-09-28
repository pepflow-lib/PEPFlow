# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Symbolic one-step recursion at arbitrary k, N and alpha.
ctx_step = pf.PEPContext("bppm_symbolic_step").set_as_current()
f_step = pf.ConvexFunction(is_basis=True, tags=["f_{step}"])
h_step = pf.ConvexFunction(is_basis=True, tags=["h_{step}"])
x_anchor = pf.Vector(is_basis=True, tags=["x_{0}"])
x_k = pf.Vector(is_basis=True, tags=["x_{k}"])
x_star_step = f_step.set_stationary_point("x_{star}")
x_next = prox_step(f_step, x_k, alpha_par, h_step, "x_{k+1}")
gap_k = f_step(x_k) - f_step(x_star_step)
gap_next = f_step(x_next) - f_step(x_star_step)
D_anchor = D_of(h_step, x_star_step, x_anchor)
V_step_k = k_par / N_par * gap_k + (D_of(h_step, x_star_step, x_k) - D_anchor) / (
    alpha_par * N_par
)
V_step_next = (k_par + 1) / N_par * gap_next + (
    D_of(h_step, x_star_step, x_next) - D_anchor
) / (alpha_par * N_par)
rf_star = gap_next + f_step.grad(x_next) * (x_star_step - x_next)
rf_forward = f_step(x_next) - f_step(x_k) + f_step.grad(x_next) * (x_k - x_next)
rh_backward = h_step(x_k) - h_step(x_next) + h_step.grad(x_k) * (x_next - x_k)
rh_forward = h_step(x_next) - h_step(x_k) + h_step.grad(x_next) * (x_k - x_next)
step_LHS = V_step_next - V_step_k
step_RHS = (
    rf_star / N_par
    + k_par / N_par * rf_forward
    + (k_par + 1) / (alpha_par * N_par) * rh_backward
    + k_par / (alpha_par * N_par) * rh_forward
)
diff_step = step_LHS - step_RHS
pm_step = symbolic_manager(ctx_step, symbolic_params)
step_verified = exact_check("Step", diff_step, pm_step, ctx_step)

# Verify that the exact geometric expression resolves the discovered coefficients.
a0 = x_star_step - x_anchor
ak = x_star_step - x_k
q0 = h_step.grad(x_anchor)
qk = h_step.grad(x_k)
V_basis = (
    (q0 * a0 - qk * ak) / (alpha_par * N_par)
    + k_par / N_par * gap_k
    + (h_step(x_anchor) - h_step(x_k)) / (alpha_par * N_par)
)
structure_verified = exact_check(
    "Closed-form coefficient structure", V_basis - V_step_k, pm_step, ctx_step
)
