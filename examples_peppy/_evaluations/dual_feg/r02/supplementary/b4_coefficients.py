# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

coeff_by_k = {}
coefficient_residuals = {}
required_indices = list(range(N_int + 1))
extraction_tolerances = dict(indep_tol=1e-7, span_tol=1e-5)
for k in required_indices:
    basis_k = V_k_basis(k)
    target = np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords, dtype=float)
    if not basis_k:
        assert ranks[k] == 0 and np.linalg.norm(target, ord="fro") < 1e-5
        C = np.zeros((0, 0))
        residual = float(np.linalg.norm(target, ord="fro"))
    else:
        Q = np.column_stack([pm.eval_vector(v).coords for v in basis_k]).astype(float)
        assert int(np.linalg.matrix_rank(Q, tol=1e-7)) == len(basis_k) == ranks[k]
        C = find_symmetric_coefficient_matrix(
            lyap[k],
            basis_k,
            pep_context=ctx,
            resolve_parameters=params_sp,
            **extraction_tolerances,
        )
        residual = float(np.linalg.norm(Q @ C @ Q.T - target, ord="fro"))
        assert residual <= 1e-5 * max(1.0, np.linalg.norm(target, ord="fro"))
        assert np.array_equal(C, C.T)
    coeff_by_k[k] = C
    coefficient_residuals[k] = residual
    print(
        f"k={k}: rank {ranks[k]} basis {V_k_basis_labels(k)}; reconstruction residual {residual:.3e}"
    )
    if C.size:
        pf.pprint_labeled_matrix(C, row_labels=V_k_basis_labels(k))
    ev = pm.eval_scalar(lyap[k])
    assert np.asarray(ev.func_coords).size == 0 and float(ev.offset) == 0
    print("Function coordinates: absent; offset:", ev.offset)
