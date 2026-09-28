search_tolerances=dict(zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
search_basis_by_k={}
search_coeff_by_k={}
for k in range(1,N_int+1):
    found,C=find_basis_with_sparsest_coefficients(lyap[k],spanning_by_k[k],pep_context=ctx,resolve_parameters=params_sp,zero_tol=search_tolerances["zero_tol"],indep_tol=search_tolerances["indep_tol"],span_tol=search_tolerances["span_tol"])
    assert len(found)==ranks[k]
    search_basis_by_k[k]=found
    search_coeff_by_k[k]=C
    print(f'k={k}, rank={ranks[k]}')
    print('  sparse basis:',[label_by_id[id(v)] for v in found])
    print('  zero coefficients:',int(np.sum(np.abs(C)<1e-6)),'/',C.size)

