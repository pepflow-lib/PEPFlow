sparse_search_results={}
for k in range(1,N_int+1):
    sparse_basis,sparse_C=find_basis_with_sparsest_coefficients(lyap[k],spanning_by_k[k],pep_context=ctx,resolve_parameters=params_sp,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    assert len(sparse_basis)==ranks[k]
    sparse_search_results[str(k)]={'labels':[labels_by_id[id(v)] for v in sparse_basis],'coefficients':sparse_C.tolist(),'zero_count':int(np.sum(np.abs(sparse_C)<1e-6))}
    print(f'k={k}, rank {ranks[k]}')
    print('sparse basis:',sparse_search_results[str(k)]['labels'])
    print(f'zero coefficients: {np.sum(np.abs(sparse_C)<1e-6)}/{sparse_C.size}')
