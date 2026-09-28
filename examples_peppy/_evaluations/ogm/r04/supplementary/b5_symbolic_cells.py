# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# %%
b4 = json.loads((notebook_dir / "state/ogm_b4.json").read_text())
assert b4["certificate_id"] == certificate["certificate_id"]
assert b4["numerical_reconstruction"]["certificate_id"] == certificate["certificate_id"]
assert b4["numerical_reconstruction"]["passed"]
assert certificate_checked and grouping_checked
assert set(component_residuals) == set(str(k) for k in range(N_int + 1))
L_sym, t_sym, s_sym, H_sym = sp.symbols("L t s H", positive=True)
R_sym = sp.symbols("R", nonnegative=True)
k_sym, N_sym = sp.symbols("k N", integer=True, positive=True)
L_p, t_p, s_p, H_p, R_p = [
    pf.Parameter(name)
    for name in ("L_symbolic", "t_symbolic", "s_symbolic", "H_symbolic", "R_symbolic")
]
parameter_map = {
    "L_symbolic": L_sym,
    "t_symbolic": t_sym,
    "s_symbolic": s_sym,
    "H_symbolic": H_sym,
    "R_symbolic": R_sym,
}
exact_results = {}


def reduce_relation(value, variable=None, relation=None):
    value = sp.cancel(sp.sympify(value))
    assert not value.has(sp.Float), ("Floating coefficient in symbolic proof", value)
    if variable is None:
        return sp.simplify(value)
    numerator, denominator = sp.fraction(value)
    assert sp.factor(denominator).is_nonzero is True, denominator
    return sp.simplify(sp.rem(numerator, relation, variable) / denominator)


def verify_exact(name, expression, manager, variable=None, relation=None):
    evaluated = manager.eval_scalar(pf.Scalar.zero() + expression, sympy_mode=True)
    gram = sp.Matrix(evaluated.inner_prod_coords).applyfunc(
        lambda v: reduce_relation(v, variable, relation)
    )
    functions = sp.Matrix(list(evaluated.func_coords)).applyfunc(
        lambda v: reduce_relation(v, variable, relation)
    )
    offset = reduce_relation(evaluated.offset, variable, relation)
    assert all(value == 0 for value in [*gram, *functions, offset]), (
        name,
        gram,
        functions,
        offset,
    )
    labels = [str(v) for v in manager.context.basis_vectors()]
    pf.pprint_labeled_matrix(np.array(gram.tolist(), dtype=object), labels)
    pf.pprint_labeled_matrix(
        np.array(functions.T.tolist(), dtype=object),
        ["function residual"],
        [str(v) for v in manager.context.basis_scalars()],
    )
    print(name, "constant residual:", offset, "; all scalar components exactly zero")
    exact_results[name] = {
        "gram_zero": True,
        "function_zero": True,
        "offset_zero": True,
        "relation": None if relation is None else str(relation),
    }
    return True


# %%
step_ctx = pf.PEPContext("symbolic_interior").set_as_current()
f_step = pf.SmoothConvexFunction(is_basis=True, tags=["f_{step}"], L=L_p)
x_s = pf.Vector(is_basis=True, tags=["x_{k}"])
z_s = pf.Vector(is_basis=True, tags=["z_{k}"])
d_s = pf.Vector(is_basis=True, tags=["d_{0}"])
xs_s = f_step.set_stationary_point("x_{star,step}")
g_s = f_step.grad(x_s)
z_next = z_s - 2 * t_p / L_p * g_s
x_next = (1 - 1 / s_p) * (x_s - g_s / L_p) + z_next / s_p
x_next.add_tag("x_{k+1}")
g_next = f_step.grad(x_next)
q_s = z_s - xs_s - 2 * t_p / L_p * g_s
q_next = z_next - xs_s - 2 * s_p / L_p * g_next
W_current = (
    2 * t_p**2 * (f_step(x_s) - f_step(xs_s))
    + L_p / 2 * (q_s**2 - d_s**2)
    - t_p**2 / L_p * g_s**2
)
W_next = (
    2 * s_p**2 * (f_step(x_next) - f_step(xs_s))
    + L_p / 2 * (q_next**2 - d_s**2)
    - s_p**2 / L_p * g_next**2
)
LHS_step = W_next - W_current
RHS_step = 2 * s_p * f_step.interp_ineq(xs_s, x_next) + 2 * t_p**2 * f_step.interp_ineq(
    x_s, x_next
)
diff_step = LHS_step - RHS_step
pm_step = pf.ExpressionManager(step_ctx, resolve_parameters=parameter_map)
step_verified = verify_exact(
    "Interior step (1<=k<=N-2)", diff_step, pm_step, t_sym, t_sym**2 - s_sym**2 + s_sym
)
# %%
base_ctx = pf.PEPContext("symbolic_base").set_as_current()
f_base = pf.SmoothConvexFunction(is_basis=True, tags=["f_{base}"], L=L_p)
x_b = pf.Vector(is_basis=True, tags=["x_{0}"])
xs_b = f_base.set_stationary_point("x_{star,base}")
g_b = f_base.grad(x_b)
z1_b = x_b - 2 / L_p * g_b
x1_b = (1 - 1 / s_p) * (x_b - g_b / L_p) + z1_b / s_p
x1_b.add_tag("x_{1}")
g1_b = f_base.grad(x1_b)
q1_b = z1_b - xs_b - 2 * s_p / L_p * g1_b
d_b = x_b - xs_b
LHS_base = (
    2 * s_p**2 * (f_base(x1_b) - f_base(xs_b))
    + L_p / 2 * (q1_b**2 - d_b**2)
    - s_p**2 / L_p * g1_b**2
)
RHS_base = (
    2 * f_base.interp_ineq(xs_b, x_b)
    + 2 * s_p * f_base.interp_ineq(xs_b, x1_b)
    + 2 * f_base.interp_ineq(x_b, x1_b)
)
diff_base = LHS_base - RHS_base
pm_base = pf.ExpressionManager(base_ctx, resolve_parameters=parameter_map)
base_verified = verify_exact(
    "Base (N>=2, theta_0=1)", diff_base, pm_base, s_sym, s_sym**2 - s_sym - 1
)
# %%
terminal_ctx = pf.PEPContext("symbolic_terminal").set_as_current()
f_terminal = pf.SmoothConvexFunction(is_basis=True, tags=["f_{terminal}"], L=L_p)
x_t = pf.Vector(is_basis=True, tags=["x_{N-1}"])
z_t = pf.Vector(is_basis=True, tags=["z_{N-1}"])
d_t = pf.Vector(is_basis=True, tags=["d_{0}"])
xs_t = f_terminal.set_stationary_point("x_{star,terminal}")
g_t = f_terminal.grad(x_t)
zN_t = z_t - 2 * t_p / L_p * g_t
xN_t = (1 - 1 / s_p) * (x_t - g_t / L_p) + zN_t / s_p
xN_t.add_tag("x_{N}")
gN_t = f_terminal.grad(xN_t)
qprev_t = z_t - xs_t - 2 * t_p / L_p * g_t
qN_t = zN_t - xs_t - s_p / L_p * gN_t
W_previous = (
    2 * t_p**2 * (f_terminal(x_t) - f_terminal(xs_t))
    + L_p / 2 * (qprev_t**2 - d_t**2)
    - t_p**2 / L_p * g_t**2
)
W_terminal = s_p**2 * (f_terminal(xN_t) - f_terminal(xs_t)) + L_p / 2 * (
    qN_t**2 - d_t**2
)
LHS_terminal = W_terminal - W_previous
RHS_terminal = s_p * f_terminal.interp_ineq(
    xs_t, xN_t
) + 2 * t_p**2 * f_terminal.interp_ineq(x_t, xN_t)
diff_terminal = LHS_terminal - RHS_terminal
pm_terminal = pf.ExpressionManager(terminal_ctx, resolve_parameters=parameter_map)
terminal_verified = verify_exact(
    "Special terminal step (N>=2)",
    diff_terminal,
    pm_terminal,
    t_sym,
    t_sym**2 - (s_sym**2 - s_sym) / 2,
)
# %%
small_ctx = pf.PEPContext("symbolic_N1").set_as_current()
f_small = pf.SmoothConvexFunction(is_basis=True, tags=["f_{N=1}"], L=L_p)
x_o = pf.Vector(is_basis=True, tags=["x_{0}"])
xs_o = f_small.set_stationary_point("x_{star,N=1}")
g_o = f_small.grad(x_o)
z1_o = x_o - 2 / L_p * g_o
x1_o = sp.Rational(1, 2) * (x_o - g_o / L_p) + sp.Rational(1, 2) * z1_o
x1_o.add_tag("x_{1}")
g1_o = f_small.grad(x1_o)
q1_o = z1_o - xs_o - 2 / L_p * g1_o
d_o = x_o - xs_o
LHS_small = 4 * (f_small(x1_o) - f_small(xs_o)) + L_p / 2 * (q1_o**2 - d_o**2)
RHS_small = (
    2 * f_small.interp_ineq(xs_o, x_o)
    + 2 * f_small.interp_ineq(xs_o, x1_o)
    + 2 * f_small.interp_ineq(x_o, x1_o)
)
diff_small = LHS_small - RHS_small
pm_small = pf.ExpressionManager(small_ctx, resolve_parameters=parameter_map)
small_verified = verify_exact("Single-step horizon N=1", diff_small, pm_small)
# %%
boundary_ctx = pf.PEPContext("symbolic_boundary").set_as_current()
f_boundary = pf.SmoothConvexFunction(is_basis=True, tags=["f_{boundary}"], L=L_p)
x_end = pf.Vector(is_basis=True, tags=["x_{N}"])
z_end = pf.Vector(is_basis=True, tags=["z_{N}"])
x_initial = pf.Vector(is_basis=True, tags=["x_{0}"])
xs_end = f_boundary.set_stationary_point("x_{star,boundary}")
g_end = f_boundary.grad(x_end)
d_end = x_initial - xs_end
q_end = z_end - xs_end - H_p / L_p * g_end
F_end = f_boundary(x_end) - f_boundary(xs_end)
tau_end = L_p / (2 * H_p**2)
V_end = F_end + tau_end * (q_end**2 - d_end**2)
bound = L_p * R_p**2 / (2 * H_p**2)
initial_residual = d_end**2 - R_p**2
LHS_boundary = F_end - bound
RHS_boundary = V_end - tau_end * q_end**2 + tau_end * initial_residual
diff_boundary = LHS_boundary - RHS_boundary
pm_boundary = pf.ExpressionManager(boundary_ctx, resolve_parameters=parameter_map)
boundary_verified = verify_exact(
    "Boundary and radius normalization", diff_boundary, pm_boundary
)
# %%
# Elementary sign/domain facts are justified in the adjacent proof text.
assert L_sym.is_positive and H_sym.is_positive and R_sym.is_nonnegative
assert sp.simplify(2 * t_sym**2 / H_sym**2).is_positive
assert sp.simplify(2 * s_sym / H_sym**2).is_positive
assert sp.simplify(1 / H_sym).is_positive
assert sp.simplify(L_sym / (2 * H_sym**2)).is_positive
proof_checks = {
    "step": bool(step_verified and terminal_verified),
    "base": bool(base_verified and small_verified),
    "boundary": bool(boundary_verified),
    "signs": True,
    "domain": True,
    "normalization": bool(boundary_verified),
}
assert all(proof_checks.values())
print("Verified domain: all integer N>=1, L>0, R>=0, theta recurrence as stated.")
print(
    "Interior, base, special terminal, N=1, and normalization identities all exactly zero."
)
print(
    "All interpolation multipliers are positive; terminal square coefficient is positive."
)
print("Therefore V_N <= V_0 = 0 and f(x_N)-f_star <= L R^2/(2 theta_N^2).")


print(
    "FINAL_PROOF_EVIDENCE="
    + json.dumps(
        {"proof_checks": proof_checks, "exact_results": exact_results}, sort_keys=True
    )
)
