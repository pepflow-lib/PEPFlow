# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

required_indices = list(range(N_int + 1))
coeff_by_k = {}
coefficient_residuals = {}
for k in required_indices:
    vectors = V_k_basis(k)
    target = np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords, dtype=float)
    if not vectors:
        assert np.linalg.matrix_rank(target, tol=1e-4) == 0
        coeff_by_k[k] = np.zeros((0, 0))
        coefficient_residuals[k] = float(np.linalg.norm(target))
        print("k=0: rank 0 basis []")
        continue
    coordinates = np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(
        float
    )
    rank = int(np.linalg.matrix_rank(coordinates, tol=1e-7))
    assert rank == len(vectors) == ranks[k]
    C = find_symmetric_coefficient_matrix(
        lyap[k],
        vectors,
        pep_context=ctx,
        resolve_parameters=params_sp,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    error = float(np.linalg.norm(coordinates @ C @ coordinates.T - target, ord="fro"))
    assert error <= 1e-5 * max(1.0, float(np.linalg.norm(target, ord="fro")))
    assert np.array_equal(C, C.T)
    coeff_by_k[k] = C
    coefficient_residuals[k] = error
    print(
        f"k={k}: rank {rank} basis {V_k_basis_labels(k)}; reconstruction residual {error}"
    )
    pf.pprint_labeled_matrix(C, V_k_basis_labels(k))


def coeff_pattern(k, N, alpha):
    if k == 0:
        return np.zeros((0, 0))
    C = np.zeros((4, 4))
    C[0, 1] = C[1, 0] = 1 / (2 * alpha * N)
    C[2, 3] = C[3, 2] = -1 / (2 * alpha * N)
    return C


fit_errors = {
    str(k): float(
        np.max(
            np.abs(coeff_by_k[k] - coeff_pattern(k, N_int, params_sp["alpha"])),
            initial=0,
        )
    )
    for k in required_indices
}
assert max(fit_errors.values()) <= 1e-4
print("Coefficient candidate residuals:", fit_errors)
