required_indices=list(range(N_int+1))
extraction_tolerances=dict(indep_tol=1e-7,span_tol=1e-5)
coeff_by_k, coefficient_residuals, independence = {}, {}, {}
for k in required_indices:
    vectors=V_k_basis(k)
    target=pm.eval_scalar(lyap[k])
    target_matrix=np.asarray(target.inner_prod_coords,dtype=float)
    assert np.allclose(target.func_coords,0,atol=1e-5,rtol=0) and abs(target.offset)<=1e-5
    if not vectors:
        assert ranks[k]==0 and np.linalg.norm(target_matrix,ord='fro')<=1e-5
        coeff_by_k[k]=np.zeros((0,0))
        coefficient_residuals[k]=float(np.linalg.norm(target_matrix,ord='fro'))
        independence[k]=0
        print(f'k={k}: rank 0 basis []; reconstruction residual {coefficient_residuals[k]}')
        continue
    B=np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
    independence[k]=int(np.linalg.matrix_rank(B,tol=1e-7))
    assert independence[k]==len(vectors)==ranks[k]
    C=find_symmetric_coefficient_matrix(lyap[k],vectors,pep_context=ctx,resolve_parameters=params_sp,**extraction_tolerances)
    assert np.array_equal(C,C.T)
    residual=float(np.linalg.norm(B@C@B.T-target_matrix,ord='fro'))
    assert residual<=1e-5*max(1.,float(np.linalg.norm(target_matrix,ord='fro')))
    coeff_by_k[k]=C
    coefficient_residuals[k]=residual
    print(f'k={k}: rank {independence[k]} basis {V_k_basis_labels(k)}; reconstruction residual {residual}')
    pf.pprint_labeled_matrix(pf.MatrixWithNames(C,V_k_basis_labels(k),V_k_basis_labels(k)))
    print('Function coordinates:',target.func_coords,'offset:',target.offset)
