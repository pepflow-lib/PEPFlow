# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

search_results = {}
for k in range(1, N_int + 1):
    sparse_basis, C = find_basis_with_sparsest_coefficients(
        lyap[k],
        spanning_by_k[k],
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=1e-6,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    assert len(sparse_basis) == ranks[k]
    sparse_labels = [labels_by_id[id(v)] for v in sparse_basis]
    print(f"k={k}, rank={ranks[k]}: sparse basis: {sparse_labels}")
    zeros = int(np.sum(np.abs(C) < 1e-6))
    print(f"zero coefficients: {zeros}/{C.size}")
    search_results[str(k)] = {
        "labels": sparse_labels,
        "C": C.tolist(),
        "zero_count": zeros,
    }
