# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

extraction_tolerances = {"indep_tol": 1e-7, "span_tol": 1e-5}
coeff_by_k, coefficient_residuals, independence = {}, {}, {}
for k in range(N_int + 1):
    vectors = V_k_basis(k)
    target = np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords, dtype=float)
    if vectors:
        B = np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
        basis_rank = int(np.linalg.matrix_rank(B, tol=1e-7))
        assert basis_rank == len(vectors) == ranks[k]
        C = find_symmetric_coefficient_matrix(
            lyap[k],
            vectors,
            pep_context=ctx,
            resolve_parameters=params_sp,
            **extraction_tolerances,
        )
        residual = float(np.linalg.norm(B @ C @ B.T - target, ord="fro"))
    else:
        basis_rank = 0
        assert ranks[k] == 0
        C = np.zeros((0, 0))
        residual = float(np.linalg.norm(target, ord="fro"))
    assert np.array_equal(C, C.T)
    assert residual <= 1e-5 * max(1.0, np.linalg.norm(target, ord="fro"))
    coeff_by_k[k], coefficient_residuals[k], independence[k] = C, residual, basis_rank
    print(
        f"k={k}: rank {basis_rank} basis {V_k_basis_labels(k)}; reconstruction residual {residual:.3e}"
    )
    pf.pprint_labeled_matrix(
        pf.MatrixWithNames(C, V_k_basis_labels(k), V_k_basis_labels(k))
    )
    ev = pm.eval_scalar(lyap[k])
    assert (
        np.allclose(ev.func_coords, 0, atol=1e-5, rtol=0)
        and abs(float(ev.offset)) < 1e-5
    )
    print("Function-value terms: none; offset:", float(ev.offset))
