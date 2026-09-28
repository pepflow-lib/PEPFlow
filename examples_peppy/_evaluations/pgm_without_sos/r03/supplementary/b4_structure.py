def V_k_structure(k):
    vectors=V_k_basis(k)
    C=coeff_by_k[k]
    quadratic=sum((float(C[i,j])*vectors[i]*vectors[j] for i,j in np.ndindex(C.shape)),pf.Scalar.zero())
    if k==0:
        return quadratic
    af,ag=function_coefficients[k]
    return quadratic+af*(f(ctx[f'x_{k}'])-f(ctx['x_star']))+ag*(g(ctx[f'x_{k}'])-g(ctx['x_star']))

component_residuals={}
for k in range(N_int+1):
    diff=pm.eval_scalar(V_k_structure(k)-lyap[k])
    target=pm.eval_scalar(lyap[k])
    component_residuals[str(k)]={}
    for name,part,reference in [('gram',diff.inner_prod_coords,target.inner_prod_coords),('function',diff.func_coords,target.func_coords),('offset',diff.offset,target.offset)]:
        error=float(np.max(np.abs(np.asarray(part,float)),initial=0))
        scale=float(np.max(np.abs(np.asarray(reference,float)),initial=0))
        assert error<=1e-4+1e-5*scale
        component_residuals[str(k)][name]=error
print('All-index full-expression reconstruction:',component_residuals)
