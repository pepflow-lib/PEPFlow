# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# %% Compare the exact closed coefficients with the reconstructed numerical potential.
def closed_coefficient_matrix(index, horizon, smoothness):
    n = sp.Integer(horizon)
    ell = sp.sympify(smoothness)
    if index == 0:
        return sp.zeros(0)
    if index == horizon:
        return sp.Matrix([[-ell / (4 * n)]])
    t = 2 * n - index
    C = sp.zeros(4)
    C[0, 0] = -ell / (4 * n)
    C[1, 1] = ell * (n - index) / t**2
    C[1, 3] = C[3, 1] = -1 / (2 * t)
    C[2, 2] = -beta_closed(index, horizon) / ell
    return C


def closed_gap_coefficients(index, horizon):
    if index == 0:
        return sp.S.Zero, sp.S.Zero
    if index == horizon:
        return sp.S.One, sp.S.One
    t = sp.Integer(2 * horizon - index)
    return (index + 1) / t, index / t


closed_comparison = {}
for index in range(N_int + 1):
    C_exact = closed_coefficient_matrix(index, N_int, sp.S.One)
    C_float = np.array(C_exact, dtype=float).reshape(coeff_by_k[index].shape)
    assert np.allclose(C_float, coeff_by_k[index], atol=1e-4, rtol=1e-5)
    basis_exact = V_k_basis(index)
    exact_sample = sum(
        (
            float(C_exact[i, j]) * basis_exact[i] * basis_exact[j]
            for i, j in np.ndindex(C_float.shape)
        ),
        pf.Scalar.zero(),
    )
    alpha_exact, gamma_exact = closed_gap_coefficients(index, N_int)
    if index:
        exact_sample += float(alpha_exact) * (
            f(ctx[f"x_{index}"]) - f(ctx["x_star"])
        ) + float(gamma_exact) * (g(ctx[f"x_{index}"]) - g(ctx["x_star"]))
    difference = pm.eval_scalar(exact_sample - lyap[index])
    errors = {
        key: max_abs(value)
        for key, value in [
            ("gram", difference.inner_prod_coords),
            ("function", difference.func_coords),
            ("offset", difference.offset),
        ]
    }
    assert max(errors.values()) < 1e-4
    closed_comparison[str(index)] = errors
    print(
        "Closed coefficient matrix at k=", index, "; complete scalar residuals:", errors
    )
    pf.pprint_labeled_matrix(C_float, V_k_basis_labels(index), precision=7)
    print("Exact function coefficients:", alpha_exact, gamma_exact)
print("True selected certificate S:")
pf.pprint_labeled_matrix(
    np.asarray(b4["S_matrix"], dtype=float),
    [str(v) for v in ctx.basis_vectors()],
    precision=6,
)
