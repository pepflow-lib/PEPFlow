# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

a_now, b_now, a_next, b_next, u_lip, t_mon = sp.symbols(
    "a_k b_k a_next b_next u_lip t_mon", real=True
)
PA = pf.Parameter("a_now")
PB = pf.Parameter("b_now")
PAn = pf.Parameter("a_next")
PBn = pf.Parameter("b_next")
PU = pf.Parameter("u_lip")
PT = pf.Parameter("t_mon")
unknown_params: dict[str, Any] = {
    **params_symbolic,
    "a_now": a_now,
    "b_now": b_now,
    "a_next": a_next,
    "b_next": b_next,
    "u_lip": u_lip,
    "t_mon": t_mon,
}
unknown_V = PA * g_step**2 + PB * LL * g_step * (x_step - x0_step)
unknown_Vnext = PAn * gnext_step**2 + PBn * LL * gnext_step * (xnext_step - x0_step)
unknown_Lip = (gnext_step - h_step) ** 2 - LL**2 * (xnext_step - y_step) ** 2
unknown_Mon = -(gnext_step - g_step) * (xnext_step - x_step)
unknown_diff = unknown_Vnext - unknown_V - PU * unknown_Lip - PT * LL * unknown_Mon
pm_unknown = pf.ExpressionManager(ctx_step, resolve_parameters=unknown_params)
gram_unknown, func_unknown, offset_unknown = exact_components(unknown_diff, pm_unknown)
coefficient_equations = [
    term for term in [*gram_unknown, *func_unknown, offset_unknown] if term != 0
]
solutions = sp.solve(
    coefficient_equations, [a_now, a_next, b_next, u_lip, t_mon], dict=True
)
assert len(solutions) == 1
solution = solutions[0]
print("Coefficient equations solved exactly:", solution)
expected = {
    a_now: k_sp * b_now / 2,
    a_next: (k_sp + 1) ** 2 * b_now / (2 * k_sp),
    b_next: (k_sp + 1) * b_now / k_sp,
    u_lip: (k_sp + 1) ** 2 * b_now / (2 * k_sp),
    t_mon: (k_sp + 1) * b_now,
}
assert all(sp.simplify(solution[name] - value) == 0 for name, value in expected.items())
# b_(k+1)/(k+1)=b_k/k; therefore b_k=c*k and a_k=c*k^2/2.
# Terminal completion fixes c=4/N^2, yielding the target coefficient 1 on ||g_N||^2.
c_scale = 4 / N_sp**2
assert sp.simplify((c_scale * (k_sp + 1)) / (k_sp + 1) - (c_scale * k_sp) / k_sp) == 0
resolved_a = sp.simplify(k_sp * (c_scale * k_sp) / 2)
resolved_b = c_scale * k_sp
assert sp.simplify(resolved_a - 2 * k_sp**2 / N_sp**2) == 0
print("Resolved a_k=", resolved_a, "; b_k=", resolved_b)
print(
    "LaTeX V_k:",
    sp.latex(resolved_a)
    + r"\|g_{k}\|^2+"
    + sp.latex(resolved_b * L_sp)
    + r"\langle g_{k},x_{k}-x_{0}\rangle",
)
