coeff_by_k={}
coefficient_residuals={}
function_coefficients={}
for k in range(N_int+1):
    vectors=V_k_basis(k)
    if vectors:
        C=find_symmetric_coefficient_matrix(lyap[k],vectors,pep_context=ctx,resolve_parameters=params_sp,indep_tol=1e-7,span_tol=1e-5)
        matrix=np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
    else:
        C=np.zeros((0,0))
        matrix=np.zeros((len(ctx.basis_vectors()),0))
    target=np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords,float)
    residual=float(np.linalg.norm(matrix@C@matrix.T-target,ord='fro'))
    assert residual<=1e-5*max(1,float(np.linalg.norm(target,ord='fro')))
    coeff_by_k[k]=C
    coefficient_residuals[k]=residual
    if k==0:
        function_coefficients[k]=[0.0,0.0]
    else:
        function_coefficients[k]=[sum(value for name,value in b3['named_dual_values'].items() if value is not None and name.startswith(owner+':x_star,') and int(name.split(',')[1][2:])<=k) for owner in ('f','g')]
    print(f'k={k}: quadratic reconstruction residual {residual:.3g}; function-gap coefficients {function_coefficients[k]}; offset 0')
    if vectors:
        pf.pprint_labeled_matrix(C,V_k_basis_labels(k),precision=7)
