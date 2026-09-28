# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

search_results = {}
search_tolerances = dict(zero_tol=1e-6, indep_tol=1e-7, span_tol=1e-5)
for k in range(1, N_int + 1):
    chosen, C = find_basis_with_sparsest_coefficients(
        lyap[k],
        spanning_by_k[k],
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=1e-6,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    assert len(chosen) == ranks[k]
    selected_labels = [labels_by_id[id(v)] for v in chosen]
    search_results[k] = dict(labels=selected_labels, matrix=C.tolist())
    print(f"k={k}, rank {ranks[k]}: sparse basis: {selected_labels}")
    print(f"  zero coefficients: {int(np.sum(np.abs(C) < 1e-6))}/{C.size}")
