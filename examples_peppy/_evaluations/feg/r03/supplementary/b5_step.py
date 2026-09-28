# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from typing import Any

k_sp, N_sp = sp.symbols("k N", integer=True, positive=True)
L_sp = sp.Symbol("L", positive=True)
R_sp = sp.Symbol("R", nonnegative=True)
K = pf.Parameter("k_symbolic")
NN = pf.Parameter("N_symbolic")
LL = pf.Parameter("L_symbolic")
RR = pf.Parameter("R_symbolic")
params_symbolic: dict[str, Any] = {
    "k_symbolic": k_sp,
    "N_symbolic": N_sp,
    "L_symbolic": L_sp,
    "R_symbolic": R_sp,
}
ctx_step = pf.PEPContext("feg_symbolic_step").set_as_current()
A_step = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{step}"], L=LL)
x0_step = pf.Vector(is_basis=True, tags=["x_{0}"])
x_step = pf.Vector(is_basis=True, tags=["x_{k}"])
g_step = A_step(x_step)
y_step = x_step + (x0_step - x_step) / (K + 1) - K / (K + 1) / LL * g_step
y_step.add_tag("x_{k+1/2}")
h_step = A_step(y_step)
xnext_step = x_step + (x0_step - x_step) / (K + 1) - h_step / LL
xnext_step.add_tag("x_{k+1}")
gnext_step = A_step(xnext_step)
V_step = 2 * K**2 / NN**2 * g_step**2 + 4 * K * LL / NN**2 * g_step * (x_step - x0_step)
Vnext_step = 2 * (K + 1) ** 2 / NN**2 * gnext_step**2 + 4 * (
    K + 1
) * LL / NN**2 * gnext_step * (xnext_step - x0_step)
Lip_step = (gnext_step - h_step) ** 2 - LL**2 * (xnext_step - y_step) ** 2
Mon_step = -(gnext_step - g_step) * (xnext_step - x_step)
LHS_step = Vnext_step - V_step
RHS_step = 2 * (K + 1) ** 2 / NN**2 * Lip_step + 4 * LL * K * (K + 1) / NN**2 * Mon_step
diff_step = LHS_step - RHS_step
pm_step = pf.ExpressionManager(ctx_step, resolve_parameters=params_symbolic)
step_verified = verify_exact("Step", diff_step, pm_step, ctx_step)
