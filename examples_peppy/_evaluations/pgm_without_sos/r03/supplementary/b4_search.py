searched_basis={}
for k in range(1,N_int):
    vecs,C=find_basis_with_sparsest_coefficients(lyap[k],in_column[k],pep_context=ctx,resolve_parameters=params_sp,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    assert len(vecs)==4
    labels=[next(label for label,v in candidate_pairs if v is vector) for vector in vecs]
    searched_basis[k]=labels
    print(f'k={k}, rank 4; sparse basis: {labels}')
    print(f'zero coefficients: {int(np.sum(np.abs(C)<1e-6))}/{C.size}')
