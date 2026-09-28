def V_k_structure(k):
    vectors=V_k_basis(k)
    C=coeff_by_k[k]
    return sum((float(C[i,j])*vectors[i]*vectors[j] for i,j in np.ndindex(C.shape)),pf.Scalar.zero())


component_residuals={}
for k in required_indices:
    diff=pm.eval_scalar(V_k_structure(k)-lyap[k])
    target=pm.eval_scalar(lyap[k])
    component_residuals[str(k)]={}
    for name,residual,part in (('gram',diff.inner_prod_coords,target.inner_prod_coords),('function',diff.func_coords,target.func_coords),('offset',diff.offset,target.offset)):
        error=float(np.max(np.abs(np.asarray(residual,dtype=float)),initial=0))
        scale=float(np.max(np.abs(np.asarray(part,dtype=float)),initial=0))
        assert error<=1e-4+1e-5*scale
        component_residuals[str(k)][name]=error
print('Every index passes full-expression reconstruction:',component_residuals)
