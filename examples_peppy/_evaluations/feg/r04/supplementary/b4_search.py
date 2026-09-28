search_tolerances=dict(zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
searched_bases, searched_coeffs = {}, {}
for k in range(1,N_int+1):
    chosen,C = find_basis_with_sparsest_coefficients(lyap[k],spanning_by_k[k],pep_context=ctx,resolve_parameters=params_sp,zero_tol=search_tolerances["zero_tol"],indep_tol=search_tolerances["indep_tol"],span_tol=search_tolerances["span_tol"])
    assert len(chosen)==ranks[k]
    searched_bases[k]=chosen
    searched_coeffs[k]=C
    print(f'k={k}: rank {ranks[k]} sparse basis: {[labels_by_id[id(v)] for v in chosen]}')
    print(f'  zero coefficients: {int(np.sum(np.abs(C)<search_tolerances["zero_tol"]))}/{C.size}')

