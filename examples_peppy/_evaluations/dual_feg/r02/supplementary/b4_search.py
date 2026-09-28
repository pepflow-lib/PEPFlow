# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

search_tolerances = dict(zero_tol=1e-6, indep_tol=1e-7, span_tol=1e-5)
search_results = {}
for k, in_col in spanning_by_k.items():
    sparse_basis, C = find_basis_with_sparsest_coefficients(
        lyap[k],
        in_col,
        pep_context=ctx,
        resolve_parameters=params_sp,
        zero_tol=search_tolerances["zero_tol"],
        indep_tol=search_tolerances["indep_tol"],
        span_tol=search_tolerances["span_tol"],
    )
    assert len(sparse_basis) == ranks[k]
    labels = [labels_by_id[id(v)] for v in sparse_basis]
    zeros = int(np.sum(np.abs(C) < search_tolerances["zero_tol"]))
    print(
        f"k={k}, rank={ranks[k]}: sparse basis: {labels}; zero coefficients: {zeros}/{C.size}"
    )
    search_results[str(k)] = {
        "labels": labels,
        "C": C.tolist(),
        "zero_count": zeros,
        "coefficient_count": int(C.size),
    }
