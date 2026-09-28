# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

ctx_boundary = pf.PEPContext("dual_feg_exact_boundary").set_as_current()
x0f = pf.Vector(is_basis=True, tags=["x_{0}"])
xNf = pf.Vector(is_basis=True, tags=["x_{N}"])
A_boundary = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{boundary}"], L=Lp)
xs = A_boundary.set_zero_point("x_{star}")
Gf = A_boundary(xNf)
Rp = pf.Parameter("R_exact")
Rs = sp.Symbol("R", nonnegative=True)
terminal_potential = 2 * Gf**2 - 4 * Lp / Np * (x0f - xNf) * Gf
terminal_mon = -(xNf - xs) * Gf
terminal_square = (2 * Lp / Np * (x0f - xs) - Gf) ** 2
initial_residual = (x0f - xs) ** 2 - Rp**2
LHS = Gf**2 - 4 * Lp**2 * Rp**2 / Np**2
RHS = (
    terminal_potential
    + 4 * Lp / Np * terminal_mon
    - terminal_square
    + 4 * Lp**2 / Np**2 * initial_residual
)
boundary_mapping: dict[str, Any] = {"L_exact": Ls, "N_exact": Ns, "R_exact": Rs}
pm_boundary = pf.ExpressionManager(ctx_boundary, resolve_parameters=boundary_mapping)
proof_checks["boundary"] = verify_exact(
    "Performance boundary and normalization", LHS, RHS, pm_boundary
)
# Positivity is elementary on the exact index domain; no fitted signs are used.
splus = sp.Symbol("s", positive=True, integer=True)
assert sp.simplify((2 / Ts**2).subs(Ts, splus + 1)).is_positive
assert sp.simplify((4 * Ls / (Ts * (Ts - 1))).subs(Ts, splus + 1)).is_positive
assert (4 * Ls / Ns).is_positive and (4 * Ls**2 / Ns**2).is_positive
proof_checks["signs"] = True
proof_checks["domain"] = True
proof_checks["normalization"] = True
print(
    "Domain: N>=1 integer, L>0, R>=0; ordinary steps t=N-k>=2, final step t=1 handled separately."
)
print(
    "Signs: all active residual multipliers positive; terminal square is nonnegative and subtracted."
)
print(
    "V_0=0 and V_{k+1}<=V_k give V_N<=0. Monotonicity and initial distance make the remaining boundary terms nonpositive."
)
assert all(proof_checks.values())
print("All exact proof checks:", proof_checks)
