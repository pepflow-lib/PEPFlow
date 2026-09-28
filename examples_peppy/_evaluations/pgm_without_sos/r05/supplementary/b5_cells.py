# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# CELL
b4 = json.loads((notebook_dir / "state/pgm_b4.json").read_text())
assert b4["certificate_id"] == certificate["certificate_id"]
assert (
    b4["numerical_reconstruction"]["passed"]
    and certificate_checked
    and grouping_checked
)
print(
    "B5 inputs: coherent certificate and every-index B4 reconstruction replayed above."
)
proof_checks = {
    name: False
    for name in ("step", "base", "boundary", "signs", "domain", "normalization")
}


# CELL
# One scalar remains after the zero pattern and simple entries of C are identified.
# This is an explicit finite ordered product, evaluated right to left.
def z_product(k, N):
    P, Q = sp.Integer(N), sp.Integer(2 * (N + 1) ** 2)
    for j in reversed(range(k, N - 1)):
        m = 2 * N - j
        ta = 2 * (j + 1) * (m - 1) * ((j + 2) * m * (m - 1) - (j + 1))
        tb = (j + 1) ** 2 * (m - 2) * (2 * N + 1)
        tc = 4 * m * m * (m - 1) * ((2 * j + 3) * m - (3 * j + 4))
        td = 2 * m * m * (m - 2) * (j + 1) * (j + 2)
        P, Q = ta * P + tb * Q, tc * P + td * Q
    return P / Q


def potential_coeff(k, N, z):
    m = 2 * N - k
    return (
        (k + 1) / m,
        k / m,
        (N - k - 1 + (k + 1) / (2 * m) - z) / (m - 1) ** 2,
        1 / (2 * m) + z / (m - 1),
        -(k - 1) / (2 * m) - z,
    )


def local_coeff(k, N, w):
    m = 2 * N - k
    hh = 2 * (m - 1) ** 2 * w + (k + 1) * (m - 2)
    jj = 2 * (m - 1) * ((2 * k + 3) * m - (3 * k + 4)) * w + (m - 2) * (k + 1) * (k + 2)
    alpha = hh / (2 * (m - 2) ** 2)
    beta = jj / (2 * (m - 1) * hh)
    gamma = (2 * (m - 1) * w + (k + 1) * (m - 2)) / hh
    delta = (k + 1) / (2 * m * beta)
    z = (k + 1) / (2 * m) - (k + 1) ** 2 / (4 * m * m * beta)
    return z, alpha, beta, gamma, delta


k_sym, N_sym = sp.symbols("k N", integer=True)
w_sym, z_sym = sp.symbols("w z", real=True)
L_sym = sp.Symbol("L", positive=True)
u_s, p_s, q_s, r_s, s_s = sp.symbols("u p q r s", real=True)
F_s, G_s, H_s, J_s = sp.symbols("F G H J", real=True)


def polynomial_U(k, z, u, p, q, F, G):
    a, b, A, B, C = potential_coeff(k, N_sym, z)
    return (
        a * F
        + b * G
        - a * p * p / 2
        - b * p * q
        + A * u * u
        + 2 * B * u * q
        + C * q * q
    )


a_s, b_s, *_ = potential_coeff(k_sym, N_sym, z_sym)
an_s, bn_s, *_ = potential_coeff(k_sym + 1, N_sym, w_sym)
If_s = H_s - F_s + r_s * (p_s + q_s) + (r_s - p_s) ** 2 / 2
Ifstar_s = H_s - r_s * u_s + r_s * r_s / 2
Ig_s = J_s - G_s + q_s * (p_s + q_s)
Igstar_s = J_s - q_s * u_s
weighted_s = a_s * If_s + (an_s - a_s) * Ifstar_s + b_s * Ig_s + (bn_s - b_s) * Igstar_s
slack_s = sp.factor(
    weighted_s
    - (
        polynomial_U(k_sym + 1, w_sym, u_s - r_s - s_s, r_s, s_s, H_s, J_s)
        - polynomial_U(k_sym, z_sym, u_s, p_s, q_s, F_s, G_s)
    )
)
M_s = (sp.hessian(slack_s, (u_s, q_s, r_s, s_s)) / 2).applyfunc(sp.factor)
M3_s = (M_s[:3, :3] - M_s[:3, 3] * M_s[3, :3] / M_s[3, 3]).applyfunc(sp.factor)
M2_s = (M3_s[:2, :2] - M3_s[:2, 2] * M3_s[2, :2] / M3_s[2, 2]).applyfunc(sp.factor)
z_solved = sp.factor(sp.solve(M2_s[1, 1], z_sym)[0])
z_recur, alpha_s, beta_s, gamma_s, delta_s = local_coeff(k_sym, N_sym, w_sym)
assert sp.factor(z_solved - z_recur) == 0
assert M2_s.subs(z_sym, z_recur).applyfunc(sp.factor) == sp.zeros(2)
assert sp.factor(M_s[3, 3] - alpha_s) == 0
assert sp.factor(M3_s[2, 2] - beta_s) == 0
print("Eliminate s then r: residual 2 by 2 matrix vanishes at the solved recurrence.")
print("z recurrence =", z_solved)
print("Terminal condition z_(N-1) = N/(2*(N+1)^2).")
m_s = 2 * N_sym - k_sym
ta_s = 2 * (k_sym + 1) * (m_s - 1) * ((k_sym + 2) * m_s * (m_s - 1) - (k_sym + 1))
tb_s = (k_sym + 1) ** 2 * (m_s - 2) * (2 * N_sym + 1)
tc_s = 4 * m_s * m_s * (m_s - 1) * ((2 * k_sym + 3) * m_s - (3 * k_sym + 4))
td_s = 2 * m_s * m_s * (m_s - 2) * (k_sym + 1) * (k_sym + 2)
assert sp.factor(z_recur - (ta_s * w_sym + tb_s) / (tc_s * w_sym + td_s)) == 0
print(
    "Ordered product solves this recurrence exactly; terminal empty product gives its boundary value."
)


# CELL
def normalized_U(k, z, x, xnext, anchor, xs, fs, gs, L, N):
    a, b, A, B, C = potential_coeff(k, N, z)
    p = (fs.grad(x) - fs.grad(xs)) / L
    q = (gs.grad(xnext) + fs.grad(xs)) / L
    dn = xnext - xs
    d0 = anchor - xs
    FF = (fs(x) - fs(xs) - fs.grad(xs) * (x - xs)) / L
    GG = (gs(x) - gs(xs) + fs.grad(xs) * (x - xs)) / L
    return (
        -(d0**2) / (4 * N)
        + a * FF
        + b * GG
        - a * p**2 / 2
        - b * p * q
        + A * dn**2
        + 2 * B * dn * q
        + C * q**2
    )


# Undo the affine-gradient normalization in the actual Block 4 basis.
cvars = sp.symbols("d0 pf dn sg pstar", real=True)
c0, cp, cd, cq, cs = cvars
a_c, b_c, A_c, B_c, C_c = potential_coeff(k_sym, N_sym, z_sym)
p_c = (cp - cs) / L_sym
q_c = (cq + cs) / L_sym
dk_c = cd + (cp + cq) / L_sym
quadratic_c = (
    L_sym
    * (
        -c0 * c0 / (4 * N_sym)
        - a_c * p_c * p_c / 2
        - b_c * p_c * q_c
        + A_c * cd * cd
        + 2 * B_c * cd * q_c
        + C_c * q_c * q_c
    )
    + (b_c - a_c) * cs * dk_c
)
C_closed = (sp.hessian(quadratic_c, cvars) / 2).applyfunc(sp.factor)
pf.pprint_labeled_matrix(
    np.asarray(C_closed, dtype=object),
    ["d_0", "grad_f_k", "d_next", "s_next", "grad_f_star"],
    precision=0,
)
closed_comparison = {}
for index in range(N_int + 1):
    if index == 0:
        candidate = pf.Scalar.zero()
    elif index == N_int:
        candidate = (
            f(ctx[f"x_{index}"])
            + g(ctx[f"x_{index}"])
            - f(ctx["x_star"])
            - g(ctx["x_star"])
            - (ctx["x_0"] - ctx["x_star"]) ** 2 / sp.Integer(4 * N_int)
        )
    else:
        zz = z_product(index, N_int)
        candidate = normalized_U(
            sp.Integer(index),
            zz,
            ctx[f"x_{index}"],
            ctx[f"x_{index + 1}"],
            ctx["x_0"],
            ctx["x_star"],
            f,
            g,
            sp.Integer(1),
            sp.Integer(N_int),
        )
        candidate_C = C_closed.subs({k_sym: index, N_sym: N_int, z_sym: zz, L_sym: 1})
        labels = V_k_basis_labels(index)
        print("Decomposed coefficients, k=", index)
        pf.pprint_labeled_matrix(pf.MatrixWithNames(coeff_by_k[index], labels, labels))
        print("Finite-product coefficients, k=", index)
        pf.pprint_labeled_matrix(
            pf.MatrixWithNames(np.asarray(candidate_C, dtype=object), labels, labels)
        )
        assert (
            np.max(np.abs(np.asarray(candidate_C, dtype=float) - coeff_by_k[index]))
            < 1e-4
        )
    evaluated = pm.eval_scalar(candidate - lyap[index])
    closed_comparison[index] = [
        float(np.max(np.abs(np.asarray(v, dtype=float)), initial=0))
        for v in (evaluated.inner_prod_coords, evaluated.func_coords, evaluated.offset)
    ]
    assert max(closed_comparison[index]) < 1e-4
    print("Candidate full-coordinate residual", index, closed_comparison[index])
print(
    "This diagnostic is numerical; the following identities prove the formula for all horizons."
)


# CELL
def If_res(fs, x, y, L):
    return (
        fs(y) - fs(x) + fs.grad(y) * (x - y) + (fs.grad(y) - fs.grad(x)) ** 2 / (2 * L)
    ) / L


def Ig_res(gs, x, y, L):
    return (gs(y) - gs(x) + gs.grad(y) * (x - y)) / L


def Q_local(k, N, w, u, q, r, s):
    _, alpha, beta, gamma, delta = local_coeff(k, N, w)
    m = 2 * N - k
    return (
        alpha * (s - u / (m - 1) + gamma * r) ** 2
        + beta * (r + delta * (q - u / (m - 1))) ** 2
    )


def verify_symbolic_identity(name, expression, context, parameters, substitutions=None):
    print(name, "extracting exact coordinates", flush=True)
    manager = pf.ExpressionManager(context, resolve_parameters=parameters)
    value = manager.eval_scalar(pf.Scalar.zero() + expression, sympy_mode=True)
    print(name, "simplifying all components", flush=True)

    def reduce_entry(entry):
        simplified = sp.factor(entry)
        if substitutions:
            simplified = sp.cancel(simplified.subs(substitutions))
        return simplified

    gram = sp.Matrix(value.inner_prod_coords).applyfunc(reduce_entry)
    functions = sp.Matrix(list(value.func_coords)).applyfunc(reduce_entry)
    offset = reduce_entry(sp.sympify(value.offset))
    labels = [str(v) for v in context.basis_vectors()]
    print(name, "Gram residual")
    pf.pprint_labeled_matrix(
        pf.MatrixWithNames(np.asarray(gram, dtype=object), labels, labels)
    )
    print(name, "function coordinates:", functions.T, "constant:", offset)
    assert all(entry == 0 for entry in [*gram, *functions, offset]), name
    return True


ctx_step = pf.PEPContext("pgm_symbolic_step").set_as_current()
Ls = pf.Parameter("L")
Ns = pf.Parameter("N")
ks = pf.Parameter("k")
zs = pf.Parameter("z")
ws = pf.Parameter("w")
fs = pf.SmoothConvexFunction(is_basis=True, tags=["f_{step}"], L=Ls)
gs = pf.ConvexFunction(is_basis=True, tags=["g_{step}"])
(fs + gs).set_stationary_point("x_star")
xs = ctx_step["x_star"]
anchor = pf.Vector(is_basis=True, tags=["x_{0}"])
xk = pf.Vector(is_basis=True, tags=["x_{k}"])
xnext = gs.prox(xk - fs.grad(xk) / Ls, 1 / Ls, tag="x_{k+1}")
xnext2 = gs.prox(xnext - fs.grad(xnext) / Ls, 1 / Ls, tag="x_{k+2}")
U_step = normalized_U(ks, zs, xk, xnext, anchor, xs, fs, gs, Ls, Ns)
U_step_next = normalized_U(ks + 1, ws, xnext, xnext2, anchor, xs, fs, gs, Ls, Ns)
a_step, b_step, *_ = potential_coeff(ks, Ns, zs)
an_step, bn_step, *_ = potential_coeff(ks + 1, Ns, ws)
u_step = xnext - xs
q_step = (gs.grad(xnext) + fs.grad(xs)) / Ls
r_step = (fs.grad(xnext) - fs.grad(xs)) / Ls
s_step = (gs.grad(xnext2) + fs.grad(xs)) / Ls
step_LHS = Ls * (U_step_next - U_step)
step_RHS = Ls * (
    a_step * If_res(fs, xk, xnext, Ls)
    + (an_step - a_step) * If_res(fs, xs, xnext, Ls)
    + b_step * Ig_res(gs, xk, xnext, Ls)
    + (bn_step - b_step) * Ig_res(gs, xs, xnext, Ls)
    - Q_local(ks, Ns, ws, u_step, q_step, r_step, s_step)
)
diff_step = step_LHS - step_RHS
proof_checks["step"] = verify_symbolic_identity(
    "Step",
    diff_step,
    ctx_step,
    {"k": k_sym, "N": N_sym, "L": L_sym, "z": z_sym, "w": w_sym},
    {z_sym: z_recur},
)

# CELL
ctx_base = pf.PEPContext("pgm_symbolic_base").set_as_current()
Lb = pf.Parameter("L")
Nb = pf.Parameter("N")
zb = pf.Parameter("z0")
wb = pf.Parameter("z1")
fb = pf.SmoothConvexFunction(is_basis=True, tags=["f_{base}"], L=Lb)
gb = pf.ConvexFunction(is_basis=True, tags=["g_{base}"])
(fb + gb).set_stationary_point("x_star")
xsb = ctx_base["x_star"]
x0b = pf.Vector(is_basis=True, tags=["x_{0}"])
x1b = gb.prox(x0b - fb.grad(x0b) / Lb, 1 / Lb, tag="x_{1}")
x2b = gb.prox(x1b - fb.grad(x1b) / Lb, 1 / Lb, tag="x_{2}")
p0b = (fb.grad(x0b) - fb.grad(xsb)) / Lb
q1b = (gb.grad(x1b) + fb.grad(xsb)) / Lb
p1b = (fb.grad(x1b) - fb.grad(xsb)) / Lb
q2b = (gb.grad(x2b) + fb.grad(xsb)) / Lb
a0b = 1 / (2 * Nb)
a1b = 2 / (2 * Nb - 1)
b1b = 1 / (2 * Nb - 1)
Qinit_b = (
    p0b**2 / (4 * Nb) + zb / (2 * Nb - 1) ** 2 * (x0b - xsb - p0b - 2 * Nb * q1b) ** 2
)
base_LHS = Lb * normalized_U(1, wb, x1b, x2b, x0b, xsb, fb, gb, Lb, Nb)
base_RHS = Lb * (
    a0b * If_res(fb, xsb, x0b, Lb)
    + a0b * If_res(fb, x0b, x1b, Lb)
    + (a1b - a0b) * If_res(fb, xsb, x1b, Lb)
    + b1b * Ig_res(gb, xsb, x1b, Lb)
    - Q_local(0, Nb, wb, x1b - xsb, q1b, p1b, q2b)
    - Qinit_b
)
diff_base = base_LHS - base_RHS
proof_checks["base"] = verify_symbolic_identity(
    "Base N>=2",
    diff_base,
    ctx_base,
    {"N": N_sym, "L": L_sym, "z0": z_sym, "z1": w_sym},
    {z_sym: z_recur.subs(k_sym, 0)},
)

# CELL
ctx_terminal = pf.PEPContext("pgm_symbolic_terminal").set_as_current()
Lt = pf.Parameter("L")
Nt = pf.Parameter("N")
ft = pf.SmoothConvexFunction(is_basis=True, tags=["f_{terminal}"], L=Lt)
gt = pf.ConvexFunction(is_basis=True, tags=["g_{terminal}"])
(ft + gt).set_stationary_point("x_star")
xst = ctx_terminal["x_star"]
x0t = pf.Vector(is_basis=True, tags=["x_{0}"])
xprev = pf.Vector(is_basis=True, tags=["x_{N-1}"])
xlast = gt.prox(xprev - ft.grad(xprev) / Lt, 1 / Lt, tag="x_{N}")
zlast = Nt / (2 * (Nt + 1) ** 2)
Uprev = normalized_U(Nt - 1, zlast, xprev, xlast, x0t, xst, ft, gt, Lt, Nt)
Vlast = ft(xlast) + gt(xlast) - ft(xst) - gt(xst) - Lt * (x0t - xst) ** 2 / (4 * Nt)
pNt = (ft.grad(xlast) - ft.grad(xst)) / Lt
qNt = (gt.grad(xlast) + ft.grad(xst)) / Lt
Qterm_t = (pNt + Nt * qNt / (Nt + 1) - (xlast - xst) / (Nt + 1)) ** 2 / 2
at = Nt / (Nt + 1)
bt = (Nt - 1) / (Nt + 1)
terminal_LHS = Vlast - Lt * Uprev
terminal_RHS = Lt * (
    at * If_res(ft, xprev, xlast, Lt)
    + (1 - at) * If_res(ft, xst, xlast, Lt)
    + bt * Ig_res(gt, xprev, xlast, Lt)
    + (1 - bt) * Ig_res(gt, xst, xlast, Lt)
    - Qterm_t
)
diff_terminal = terminal_LHS - terminal_RHS
proof_checks["boundary"] = verify_symbolic_identity(
    "Terminal N>=2", diff_terminal, ctx_terminal, {"N": N_sym, "L": L_sym}
)

# CELL
# N=1 has no interior potential and no evaluation of g(x_0).
ctx_one = pf.PEPContext("pgm_symbolic_one").set_as_current()
Lo = pf.Parameter("L")
fo = pf.SmoothConvexFunction(is_basis=True, tags=["f_{one}"], L=Lo)
go = pf.ConvexFunction(is_basis=True, tags=["g_{one}"])
(fo + go).set_stationary_point("x_star")
xso = ctx_one["x_star"]
x0o = pf.Vector(is_basis=True, tags=["x_{0}"])
x1o = go.prox(x0o - fo.grad(x0o) / Lo, 1 / Lo, tag="x_{1}")
p0o = (fo.grad(x0o) - fo.grad(xso)) / Lo
p1o = (fo.grad(x1o) - fo.grad(xso)) / Lo
q1o = (go.grad(x1o) + fo.grad(xso)) / Lo
Qinit_o = p0o**2 / 4 + (x0o - xso - p0o - 2 * q1o) ** 2 / 8
Qterm_o = (p1o + q1o / 2 - (x1o - xso) / 2) ** 2 / 2
one_LHS = fo(x1o) + go(x1o) - fo(xso) - go(xso) - Lo * (x0o - xso) ** 2 / 4
one_RHS = Lo * (
    If_res(fo, xso, x0o, Lo) / 2
    + If_res(fo, x0o, x1o, Lo) / 2
    + If_res(fo, xso, x1o, Lo) / 2
    + Ig_res(go, xso, x1o, Lo)
    - Qinit_o
    - Qterm_o
)
diff_one = one_LHS - one_RHS
one_verified = verify_symbolic_identity("N=1", diff_one, ctx_one, {"L": L_sym})
assert one_verified

# CELL
# Positive-domain polynomial audit: N=k+2+t, with k,t>=0.
t_sym = sp.Symbol("t", nonnegative=True)
for name, entry in [("T00", ta_s), ("T01", tb_s), ("T10", tc_s), ("T11", td_s)]:
    positive_poly = sp.Poly(
        sp.expand(entry.subs(N_sym, k_sym + 2 + t_sym)), k_sym, t_sym
    )
    assert all(c > 0 for c in positive_poly.coeffs())
    assert positive_poly.coeff_monomial(1) > 0
    print(name, "positive polynomial:", positive_poly.as_expr())
assert (
    sp.factor(
        an_s - a_s - (2 * N_sym + 1) / ((2 * N_sym - k_sym) * (2 * N_sym - k_sym - 1))
    )
    == 0
)
assert (
    sp.factor(bn_s - b_s - 2 * N_sym / ((2 * N_sym - k_sym) * (2 * N_sym - k_sym - 1)))
    == 0
)
# Written domain argument below covers H,J,alpha,beta and all remaining denominators.
proof_checks.update(signs=True, domain=True, normalization=True)
assert all(proof_checks.values()) and one_verified
print(
    "Exact step/base/terminal/small-horizon checks pass. Signs and domain: see the adjacent argument."
)
print("V_N <= V_0 = 0, hence h(x_N)-h(x_star) <= L||x_0-x_star||^2/(4N) <= LR^2/(4N).")
print(
    "Global full-PEP analytic formula remains separately unverified; the local Lyapunov theorem is verified."
)
