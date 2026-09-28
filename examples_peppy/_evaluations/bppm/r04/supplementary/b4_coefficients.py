coeff_by_k,coefficient_residuals,function_samples,component_residuals = {},{},{},{}
required_indices=list(range(N_int+1))
for k in required_indices:
    selected_basis=V_k_basis(k)
    ev=pm.eval_scalar(lyap[k])
    target=np.asarray(ev.inner_prod_coords,dtype=float)
    if k==0:
        assert np.linalg.matrix_rank(target,tol=1e-4)==0
        coeff_by_k[k]=np.zeros((0,0))
        coefficient_residuals[k]=max_abs(target)
        function_samples[k]={'h':0.0,'f':0.0,'offset':float(ev.offset)}
        print('k=0: empty quadratic basis; zero initial expression checked')
        continue
    B=np.column_stack([pm.eval_vector(v).coords for v in selected_basis]).astype(float)
    assert np.linalg.matrix_rank(B,tol=1e-7)==len(selected_basis)==ranks[k]
    C=find_symmetric_coefficient_matrix(lyap[k],selected_basis,pep_context=ctx,resolve_parameters=params_sp,indep_tol=1e-7,span_tol=1e-5)
    assert np.allclose(B@C@B.T,target,atol=1e-4,rtol=1e-5)
    coeff_by_k[k]=C
    coefficient_residuals[k]=max_abs(B@C@B.T-target)
    print(f'k={k}: rank {ranks[k]} basis {V_k_basis_labels(k)}, residual {coefficient_residuals[k]}')
    pf.pprint_labeled_matrix(pf.MatrixWithNames(C,V_k_basis_labels(k),V_k_basis_labels(k)))
    h_difference=h_obj(ctx['x_0'])-h_obj(ctx[f'x_{k}'])
    f_difference=f_obj(ctx[f'x_{k}'])-f_obj(ctx['x_star'])
    A=np.column_stack([pm.eval_scalar(v).func_coords for v in (h_difference,f_difference)]).astype(float)
    coefficients=np.linalg.lstsq(A,np.asarray(ev.func_coords,dtype=float),rcond=None)[0]
    assert np.linalg.matrix_rank(A,tol=1e-7)==2
    assert np.allclose(A@coefficients,np.asarray(ev.func_coords,dtype=float),atol=1e-4,rtol=1e-5)
    function_samples[k]={'h':float(coefficients[0]),'f':float(coefficients[1]),'offset':float(ev.offset)}
    print('Function terms: h(x_0)-h(x_k), f(x_k)-f(x_star); coefficients:',coefficients,'offset:',ev.offset)
