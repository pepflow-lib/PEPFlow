def V_k_structure(k):
    vectors=V_k_basis(k)
    C=coeff_by_k[k]
    return sum((float(C[i,j])*vectors[i]*vectors[j] for i,j in np.ndindex(C.shape)),pf.Scalar.zero())

component_residuals={}
for k in required_indices:
    difference=pm.eval_scalar(V_k_structure(k)-lyap[k])
    target=pm.eval_scalar(lyap[k])
    component_residuals[str(k)]={}
    for label,actual,reference in [('gram',difference.inner_prod_coords,target.inner_prod_coords),('function',difference.func_coords,target.func_coords),('offset',difference.offset,target.offset)]:
        arr=np.asarray(actual,dtype=float)
        target_arr=np.asarray(reference,dtype=float)
        error=float(np.max(np.abs(arr),initial=0))
        scale=float(np.max(np.abs(target_arr),initial=0))
        assert error<=1e-4+1e-5*scale
        component_residuals[str(k)][label]=error
print('Full-expression reconstruction passed at all indices, including both endpoints.')
