# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_one = pf.PEPContext("symbolic_N1").set_as_current()
A_one = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{N=1}"], L=l_p)
x0_one = pf.Vector(is_basis=True, tags=["x_{0,N=1}"])
g0_one = A_one(x0_one)
X_one = (x0_one - g0_one / l_p).add_tag("x_{1,N=1}")
G_one = A_one(X_one)
one_LHS = terminal_potential(X_one, x0_one, G_one, l_p, 1)
one_RHS = 2 * ((g0_one - G_one) ** 2 - l_p**2 * (x0_one - X_one) ** 2)
pm_one = pf.ExpressionManager(
    ctx_one, resolve_parameters=cast(dict[str, pf.NUMERICAL_TYPE], {"L_symbolic": l_s})
)
one_diff = one_LHS - one_RHS
small_horizon_passed = verify_exact("N=1 direct terminal potential", one_diff, pm_one)
proof_checks["base"] = proof_checks["base"] and small_horizon_passed
# Domain reasoning: 1<=N, 0<=k<=N-2 imply t=N-k>=2.
# Thus 2/t^2>0 and 4L/[t(t-1)]>0; final weight 2>0.
# Boundary weights 4L/N and 4L^2/N^2 are positive, and the subtracted
# squared norm is nonnegative. No sign condition is needed on V itself.
assert sp.ask(sp.Q.positive(2 / t_s**2)) is True
m_s = sp.Symbol("m", integer=True, nonnegative=True)
assert sp.ask(sp.Q.positive(4 * l_s / ((m_s + 2) * (m_s + 1)))) is True
assert sp.ask(sp.Q.positive(4 * l_s / n_s)) is True
assert sp.ask(sp.Q.positive(4 * l_s**2 / n_s**2)) is True
proof_checks["signs"] = True
proof_checks["domain"] = (
    small_horizon_passed
    and proof_checks["step"]
    and proof_checks["base"]
    and proof_checks["boundary"]
)
assert all(proof_checks.values())
print("Exact proof obligations:", proof_checks)
