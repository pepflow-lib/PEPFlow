coeff_by_k={}
coefficient_residuals={}
independence={}
extraction_tolerances=dict(indep_tol=1e-7,span_tol=1e-5)
required_indices=list(range(N_int+1))
for k in required_indices:
    chosen=V_k_basis(k)
    target=np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords,dtype=float)
    if not chosen:
        assert ranks[k]==0 and np.linalg.norm(target)<=1e-5
        C=np.zeros((0,0))
        residual=float(np.linalg.norm(target))
        basis_rank=0
    else:
        coords=np.column_stack([pm.eval_vector(v).coords for v in chosen]).astype(float)
        basis_rank=int(np.linalg.matrix_rank(coords,tol=1e-7))
        assert basis_rank==len(chosen)==ranks[k]
        C=find_symmetric_coefficient_matrix(lyap[k],chosen,pep_context=ctx,resolve_parameters=params_sp,**extraction_tolerances)
        assert np.array_equal(C,C.T)
        residual=float(np.linalg.norm(coords@C@coords.T-target,ord='fro'))
        assert residual<=1e-5*max(1.0,np.linalg.norm(target,ord='fro'))
    coeff_by_k[k]=C
    coefficient_residuals[k]=residual
    independence[k]=basis_rank
    print(f'k={k}: rank {basis_rank} basis {V_k_basis_labels(k)}; reconstruction residual {residual:.3e}')
    if chosen:
        pf.pprint_labeled_matrix(pf.MatrixWithNames(C,V_k_basis_labels(k),V_k_basis_labels(k)))
    evaluated=pm.eval_scalar(lyap[k])
    assert np.max(np.abs(np.asarray(evaluated.func_coords,dtype=float)),initial=0)==0
    assert float(evaluated.offset)==0
    print('Function terms: none; scalar offset: 0')
