# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Compare the derived analytic matrices with the B4 numerical extraction.
analytic_comparison = {}
for k in range(1, N + 1):
    if k == N:
        C_exact = sp.Matrix([[-sp.Rational(1, 4 * N)]])
        gaps_exact = sp.Matrix([1, 1])
    else:
        denominator = sp.Integer(2 * N - k)
        C_exact = sp.zeros(4)
        C_exact[1, 1] = -sp.Rational(1, 4 * N)
        C_exact[2, 2] = sp.Rational(N - k, 1) / denominator**2
        C_exact[3, 3] = 1 / (2 * denominator)
        C_exact[0, 2] = C_exact[2, 0] = C_exact[2, 3] = C_exact[3, 2] = -1 / (
            2 * denominator
        )
        gaps_exact = sp.Matrix([(k + 1) / denominator, k / denominator])
    matrix_error = float(np.max(np.abs(np.array(C_exact, dtype=float) - coeff_by_k[k])))
    gap_error = float(
        np.max(
            np.abs(
                np.array(gaps_exact, dtype=float).reshape(-1) - function_coefficients[k]
            )
        )
    )
    analytic_comparison[str(k)] = {"matrix": matrix_error, "function": gap_error}
    assert max(matrix_error, gap_error) <= 1e-4
    print(
        "Derived matrix at k=",
        k,
        "numerical matrix/function errors=",
        matrix_error,
        gap_error,
    )
    pf.pprint_labeled_matrix(
        np.array(C_exact, dtype=object), V_k_basis_labels(k), V_k_basis_labels(k)
    )
