coeff_by_k={}
coefficient_residuals={}
required_indices=list(range(N_int+1))
for k in required_indices:
    chosen=V_k_basis(k)
    value=pm.eval_scalar(lyap[k])
    target=np.asarray(value.inner_prod_coords,dtype=float)
    if chosen:
        matrix=np.column_stack([pm.eval_vector(v).coords for v in chosen]).astype(float)
        C=find_symmetric_coefficient_matrix(lyap[k],chosen,pep_context=ctx,resolve_parameters=params_sp,indep_tol=1e-7,span_tol=1e-5)
        residual=float(np.linalg.norm(matrix@C@matrix.T-target,ord='fro'))
    else:
        C=np.zeros((0,0))
        residual=float(np.linalg.norm(target,ord='fro'))
    assert np.array_equal(C,C.T)
    assert residual<=1e-5*max(1.0,np.linalg.norm(target,ord='fro'))
    assert np.allclose(value.func_coords,0,atol=1e-5,rtol=0) and abs(float(value.offset))<=1e-5
    coeff_by_k[k]=C
    coefficient_residuals[k]=residual
    print(f'k={k}: reconstruction residual {residual:.3g}; function coordinates {value.func_coords}; offset {value.offset}')
    if chosen:
        pf.pprint_labeled_matrix(pf.MatrixWithNames(C,V_k_basis_labels(k),V_k_basis_labels(k)))
    print('C=',C.tolist())
