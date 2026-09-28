# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Derivation: eliminate the two future-gradient directions from the local quadratic remainder.
beta_unknown = sp.symbols("beta_unknown", real=True)
e_alg, p_alg, q_alg, r_alg = sp.symbols("e p q r", real=True)
t_alg = t_sym
k_alg = k_sym
next_e = e_alg - p_alg - q_alg
old_quad = (
    (t_alg - k_alg) * e_alg**2 / (2 * t_alg**2)
    - e_alg * p_alg / t_alg
    - beta_unknown * p_alg**2
)
new_quad = (
    (t_alg - k_alg - 2) * next_e**2 / (2 * (t_alg - 1) ** 2)
    - next_e * r_alg / (t_alg - 1)
    - c_next * r_alg**2
)
a_alg = (k_alg + 1) / t_alg
b_alg = k_alg / t_alg
an_alg = (k_alg + 2) / (t_alg - 1)
bn_alg = (k_alg + 1) / (t_alg - 1)
weighted_quad = (
    (an_alg - a_alg) * (-r_alg * next_e + r_alg**2 / 2)
    + a_alg * (r_alg * (e_alg - next_e) + (p_alg - r_alg) ** 2 / 2)
    + (bn_alg - b_alg) * (-q_alg * next_e)
    + b_alg * q_alg * (e_alg - next_e)
)
remainder_matrix = (
    sp.hessian(weighted_quad - new_quad + old_quad, [r_alg, q_alg, e_alg, p_alg]) / 2
).applyfunc(sp.cancel)
assert all(sp.cancel(v) == 0 for v in remainder_matrix[:2, :2] - H_symbolic)
assert all(sp.cancel(v) == 0 for v in remainder_matrix[:2, 2:] - K_symbolic)
schur_residual = (
    remainder_matrix[2:, 2:] - K_symbolic.T * H_symbolic.inv() * K_symbolic
).applyfunc(sp.cancel)
assert schur_residual[0, 0] == schur_residual[0, 1] == schur_residual[1, 0] == 0
beta_solution = sp.solve(schur_residual[1, 1], beta_unknown)[0]
assert sp.cancel(beta_solution - beta_recursion(k_sym, t_sym, c_next)) == 0
print(
    "Solved coefficient equation:",
    sp.Eq(beta_unknown, beta_recursion(k_sym, t_sym, c_next)),
)
print(
    "The finite product above solves this recurrence with beta_(N-1)=(N-1)/(2(N+1)^2)."
)
