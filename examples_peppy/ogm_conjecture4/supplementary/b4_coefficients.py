# Executed by the OGM notebook in a shared namespace with the required globals.
# Not a standalone script; validate it through notebook execution.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Adopt the consistent recurrence basis and verify each quadratic expression."""

extraction_tolerances = dict(indep_tol=1e-7, span_tol=1e-5)
coeff_by_k = {}
coefficient_residuals = {}
basis_diagnostics = {}
required_indices = list(range(N_int + 1))
for k in required_indices:
    adopted = V_k_basis(k)
    labels = V_k_basis_labels(k)
    target = np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords, float)
    coordinates = (
        np.column_stack([pm.eval_vector(v).coords for v in adopted]).astype(float)
        if adopted
        else np.zeros((len(basis_labels), 0))
    )
    basis_rank = (
        int(np.linalg.matrix_rank(coordinates, tol=extraction_tolerances["indep_tol"]))
        if adopted
        else 0
    )
    assert basis_rank == len(adopted) == ranks[k]
    # Constructed template vectors are fresh objects and may use a different
    # order from the search, so extract for these actual final inputs.
    C = find_symmetric_coefficient_matrix(
        lyap[k],
        adopted,
        pep_context=ctx,
        resolve_parameters=params_sp,
        **extraction_tolerances,
    )
    assert C.shape == (ranks[k], ranks[k]) and np.array_equal(C, C.T)
    assert np.all(np.isfinite(C))
    residual = coordinates @ C @ coordinates.T - target
    error = float(np.linalg.norm(residual, ord="fro"))
    assert error <= extraction_tolerances["span_tol"] * max(
        1.0, np.linalg.norm(target, ord="fro")
    )
    coeff_by_k[k] = C
    coefficient_residuals[k] = error
    basis_diagnostics[k] = dict(
        rank=basis_rank,
        labels=labels,
        coords=coordinates.tolist(),
        frobenius_residual=error,
        max_abs_residual=float(np.max(np.abs(residual), initial=0.0)),
    )
    print(
        f"k={k}: rank {basis_rank} basis {labels}; reconstruction residual {error:.3e}"
    )
