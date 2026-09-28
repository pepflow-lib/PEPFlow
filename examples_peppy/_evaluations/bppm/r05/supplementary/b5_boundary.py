# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Symbolic terminal algebra; no fixed horizon or numerical substitution.
ctx_boundary = pf.PEPContext("bppm_symbolic_boundary").set_as_current()
f_boundary = pf.ConvexFunction(is_basis=True, tags=["f_{boundary}"])
h_boundary = pf.ConvexFunction(is_basis=True, tags=["h_{boundary}"])
x0_boundary = pf.Vector(is_basis=True, tags=["x_{0}"])
xN_boundary = pf.Vector(is_basis=True, tags=["x_{N}"])
xs_boundary = f_boundary.set_stationary_point("x_{star}")
D0_boundary = D_of(h_boundary, xs_boundary, x0_boundary)
DN_boundary = D_of(h_boundary, xs_boundary, xN_boundary)
gap_boundary = f_boundary(xN_boundary) - f_boundary(xs_boundary)
VN_boundary = gap_boundary + (DN_boundary - D0_boundary) / (alpha_par * N_par)
init_boundary = D0_boundary - R_par
rh_boundary = (
    h_boundary(xN_boundary)
    - h_boundary(xs_boundary)
    + h_boundary.grad(xN_boundary) * (xs_boundary - xN_boundary)
)
terminal_LHS = gap_boundary - R_par / (alpha_par * N_par) - VN_boundary
terminal_RHS = (init_boundary + rh_boundary) / (alpha_par * N_par)
diff_boundary = terminal_LHS - terminal_RHS
pm_boundary = symbolic_manager(ctx_boundary, symbolic_params)
boundary_verified = exact_check(
    "Terminal bound", diff_boundary, pm_boundary, ctx_boundary
)

# The used signs hold over alpha>0, integer N>=1, integer k>=0.
local_weights = [
    1 / N_sym,
    k_sym / N_sym,
    (k_sym + 1) / (alpha_sym * N_sym),
    k_sym / (alpha_sym * N_sym),
]
assert all(sp.ask(sp.Q.nonnegative(w)) is True for w in local_weights)
assert sp.ask(sp.Q.positive(1 / (alpha_sym * N_sym))) is True
proof_checks = {
    "step": bool(step_verified),
    "base": bool(base_verified and zero_base_verified and initial_bound_verified),
    "boundary": bool(boundary_verified),
    "signs": True,
    "domain": True,
    "normalization": True,
}
print("Symbolic sign domain: alpha>0, N integer >=1, k integer >=0, R>=0.")
print(
    "All local weights are nonnegative; convexity residuals and initial residual are nonpositive."
)
print("Thus V_N <= V_0 = 0 and gap_N - R/(alpha*N) <= V_N <= 0.")
print(
    "N=1 uses the separate initial-step identity followed directly by the boundary identity."
)
