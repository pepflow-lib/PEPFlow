# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def exact_coefficients(k, N, L):
    return sp.Matrix([[2 * k**2 / N**2, 2 * k * L / N**2], [2 * k * L / N**2, 0]])


pf.pprint_labeled_matrix(
    np.asarray(exact_coefficients(k_symbol, N_symbol, L_symbol), dtype=object),
    ["A(x_k)", "x_k-x_0"],
    ["A(x_k)", "x_k-x_0"],
    precision=0,
)
# Compare with numerical sample data without conflating exact proof and solver closeness.
for index in range(1, N_int + 1):
    exact = np.asarray(
        exact_coefficients(sp.Integer(index), sp.Integer(N_int), sp.Integer(1)),
        dtype=float,
    )
    error = float(np.max(np.abs(exact - coeff_by_k[index])))
    print(
        f"k={index}: exact/numerical coefficient discrepancy {error:.8g}; match at atol=1e-4: {error <= 1e-4}"
    )
print(
    "The exact coefficients follow from symbolic equations and boundary normalization; the selected numerical dual has a slightly different scale and is retained unchanged."
)
