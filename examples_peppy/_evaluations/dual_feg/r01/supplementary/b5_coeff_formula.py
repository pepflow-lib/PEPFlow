# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def coeff_formula(k, N, L_value=1):
    NN = sp.sympify(N)
    LL = sp.sympify(L_value)
    if k == 0:
        return sp.zeros(0, 0)
    if k == N:
        return sp.Matrix([[0, -2 * LL / NN], [-2 * LL / NN, 2]])
    t = NN - k
    return sp.Matrix(
        [
            [0, 0, 0, -2 * LL / NN],
            [0, -2, 2 * LL / t, -2],
            [0, 2 * LL / t, 0, 2 * LL / t],
            [-2 * LL / NN, -2, 2 * LL / t, 0],
        ]
    )


formula_errors = {}
for k in range(N_int + 1):
    candidate_C = np.asarray(coeff_formula(k, N_int), dtype=float).reshape(
        coeff_by_k[k].shape
    )
    error = float(np.max(np.abs(candidate_C - coeff_by_k[k]), initial=0))
    formula_errors[k] = error
    assert error <= 1e-4
    print(f"k={k}: exact-formula vs numerical coefficient max error {error:.3e}")
    if candidate_C.size:
        pf.pprint_labeled_matrix(
            pf.MatrixWithNames(
                np.asarray(coeff_formula(k, N_int), dtype=object),
                V_k_basis_labels(k),
                V_k_basis_labels(k),
            )
        )
