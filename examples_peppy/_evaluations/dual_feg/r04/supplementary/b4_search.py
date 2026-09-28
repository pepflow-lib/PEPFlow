search_tolerances = {'zero_tol': 1e-6, 'indep_tol': 1e-7, 'span_tol': 1e-5}
sparse_search = {}
for k in range(1, N_int + 1):
    # These anchors occur throughout the terminal-star construction.
    anchors = [next(vector for label, vector in unique_pairs if label == label_needed)
               for label_needed in (f'A(x_{N_int})', 'x_0-x_N')]
    sparse_basis, sparse_C = find_basis_with_sparsest_coefficients(
        lyap[k], in_column_by_k[k], pep_context=ctx, resolve_parameters=params_sp,
        fixed_vectors=anchors, **search_tolerances)
    assert len(sparse_basis) == ranks[k]
    sparse_labels = [next(label for label, vector in unique_pairs if vector is v) for v in sparse_basis]
    sparse_search[k] = {'labels': sparse_labels, 'C': sparse_C.tolist()}
    print(f'k={k}, rank={ranks[k]}: sparse basis: {sparse_labels}')
    print(f"zero coefficients: {np.count_nonzero(np.abs(sparse_C)<search_tolerances['zero_tol'])}/{sparse_C.size}")
