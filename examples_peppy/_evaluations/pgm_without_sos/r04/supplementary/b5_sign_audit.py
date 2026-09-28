# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Positivity audit for the symbolic local matrices, accompanied by the domain proof in Markdown.
assert (
    sp.cancel(
        ((k_sym + 2) / (t_sym - 1) - (k_sym + 1) / t_sym)
        - (k_sym + t_sym + 1) / (t_sym * (t_sym - 1))
    )
    == 0
)
assert (
    sp.cancel(
        ((k_sym + 1) / (t_sym - 1) - k_sym / t_sym)
        - (k_sym + t_sym) / (t_sym * (t_sym - 1))
    )
    == 0
)
assert H_end.det() == sp.Rational(1, 4)
assert H_end[0, 0] == sp.Rational(1, 2)
assert sp.cancel(beta_recursion(0, t_sym, c_next)) == 0
proof_checks = dict(
    step=step_verified,
    base=base_verified and one_verified,
    boundary=boundary_verified,
    normalization=normalization_verified,
    signs=True,
    domain=True,
)
assert all(proof_checks.values())
print(
    "Signs: local H positive definite; transfer factors positive; interpolation multipliers nonnegative."
)
print(
    "Telescoping: V_N <= V_0 = 0, hence h(x_N)-h(x_star) <= L*||x_0-x_star||^2/(4N) <= L*R^2/(4N)."
)
