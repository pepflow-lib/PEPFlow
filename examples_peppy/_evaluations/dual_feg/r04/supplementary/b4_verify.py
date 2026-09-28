# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

formula_residuals, component_residuals = {}, {}
for k in range(N_int + 1):
    C_guess = coeff_pattern(k, N_int)
    error = float(np.max(np.abs(C_guess - coeff_by_k[k]), initial=0.0))
    formula_residuals[k] = error
    assert np.allclose(C_guess, coeff_by_k[k], atol=1e-4, rtol=1e-5)
    print(f"k={k}: candidate coefficient maximum error {error:.3e}")
    pf.pprint_labeled_matrix(
        pf.MatrixWithNames(C_guess, V_k_basis_labels(k), V_k_basis_labels(k))
    )
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[str(k)] = {}
    for name, residual, component in (
        ("gram", diff.inner_prod_coords, target.inner_prod_coords),
        ("function", diff.func_coords, target.func_coords),
        ("offset", diff.offset, target.offset),
    ):
        actual = np.asarray(residual, dtype=float)
        scale = float(np.max(np.abs(np.asarray(component, dtype=float)), initial=0.0))
        error = float(np.max(np.abs(actual), initial=0.0))
        assert np.isfinite(actual).all() and error <= 1e-4 + 1e-5 * scale
        component_residuals[str(k)][name] = error
print(
    "All required indices, including initial and terminal cases, reconstructed in every scalar component."
)
