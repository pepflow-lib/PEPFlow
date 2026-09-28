# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

t_s, n_s = sp.symbols("t N", integer=True, positive=True)
l_s = sp.Symbol("L", positive=True)
u_s, v_s = sp.symbols("mu_Lip mu_Mon", real=True)
ctx_step = pf.PEPContext("symbolic_step").set_as_current()
t_p = pf.Parameter("t_symbolic")
n_p = pf.Parameter("N_symbolic")
l_p = pf.Parameter("L_symbolic")
u_p = pf.Parameter("mu_Lip")
v_p = pf.Parameter("mu_Mon")
A_step = pf.LipschitzMonotoneOperator(is_basis=True, tags=["A_{step}"], L=l_p)
x0_step = pf.Vector(is_basis=True, tags=["x_{0,step}"])
X_step = pf.Vector(is_basis=True, tags=["x_{N,step}"])
x_step = pf.Vector(is_basis=True, tags=["x_{k,step}"])
z_step = pf.Vector(is_basis=True, tags=["z_{k,step}"])
g_step = A_step(x_step)
G_step = A_step(X_step)
y_step = (x_step - z_step / l_p - g_step / l_p).add_tag("y_{k,step}")
h_step = A_step(y_step)
x_next = y_step - ((t_p - 1) / t_p) * (h_step - g_step) / l_p
z_next = ((t_p - 1) / t_p) * z_step - h_step / t_p
V_step = potential(t_p, x_step, z_step, X_step, x0_step, G_step, l_p, n_p)
V_next = potential(t_p - 1, x_next, z_next, X_step, x0_step, G_step, l_p, n_p)
I_lip = (g_step - h_step) ** 2 - l_p**2 * (x_step - y_step) ** 2
I_mon = -(G_step - h_step) * (X_step - y_step)
step_LHS = V_next - V_step
step_RHS_unknown = u_p * I_lip + v_p * I_mon
pm_discovery = pf.ExpressionManager(
    ctx_step,
    resolve_parameters=cast(
        dict[str, pf.NUMERICAL_TYPE],
        {
            "t_symbolic": t_s,
            "N_symbolic": n_s,
            "L_symbolic": l_s,
            "mu_Lip": u_s,
            "mu_Mon": v_s,
        },
    ),
)
parts = symbolic_components(step_LHS - step_RHS_unknown, pm_discovery)
equations = [v for part in parts[:2] for v in part] + [parts[2]]
local_solution = sp.solve(equations, (u_s, v_s), dict=True)
assert local_solution == [{u_s: 2 / t_s**2, v_s: 4 * l_s / (t_s * (t_s - 1))}] or all(
    sp.simplify(local_solution[0][p] - q) == 0
    for p, q in [(u_s, 2 / t_s**2), (v_s, 4 * l_s / (t_s * (t_s - 1)))]
)
print("Derived local multipliers:", local_solution)
step_RHS = (2 / t_p**2) * I_lip + (4 * l_p / (t_p * (t_p - 1))) * I_mon
step_diff = step_LHS - step_RHS
pm_step = pf.ExpressionManager(
    ctx_step,
    resolve_parameters=cast(
        dict[str, pf.NUMERICAL_TYPE],
        {"t_symbolic": t_s, "N_symbolic": n_s, "L_symbolic": l_s},
    ),
)
proof_checks["step"] = verify_exact("Interior step (t>=2)", step_diff, pm_step)

coefficient_basis = [G_step, z_step, x_step - x0_step, X_step - x0_step]
C_symbolic = [
    [0, -2, 2 * l_p / t_p, -2 * l_p * (n_p - t_p) / (n_p * t_p)],
    [-2, -2, 2 * l_p / t_p, -2 * l_p / t_p],
    [2 * l_p / t_p, 2 * l_p / t_p, 0, 0],
    [-2 * l_p * (n_p - t_p) / (n_p * t_p), -2 * l_p / t_p, 0, 0],
]
coefficient_form = sum(
    (
        C_symbolic[i][j] * coefficient_basis[i] * coefficient_basis[j]
        for i in range(4)
        for j in range(4)
    ),
    pf.Scalar.zero(),
)
coefficient_identity_passed = verify_exact(
    "General-L coefficient representation", coefficient_form - V_step, pm_step
)
C_display = sp.Matrix(
    [
        [0, -2, 2 * l_s / t_s, -2 * l_s * (n_s - t_s) / (n_s * t_s)],
        [-2, -2, 2 * l_s / t_s, -2 * l_s / t_s],
        [2 * l_s / t_s, 2 * l_s / t_s, 0, 0],
        [-2 * l_s * (n_s - t_s) / (n_s * t_s), -2 * l_s / t_s, 0, 0],
    ]
)
pf.pprint_labeled_matrix(
    np.array(C_display, dtype=object),
    row_labels=["g_N", "z_k", "x_k-x_0", "x_N-x_0"],
    precision=0,
)
