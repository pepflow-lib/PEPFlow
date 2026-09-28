def closed_coeff(k,n,Lvalue=sp.S.One):
    if k==0:
        return sp.zeros(0,0)
    if k==n:
        return sp.Matrix([[-Lvalue/(4*n)]])
    m=sp.Integer(2*n-k)
    return sp.Matrix([[-Lvalue/(4*n),0,0,0],[0,Lvalue*(n-k)/m**2,-1/(2*m),-1/(2*m)],[0,-1/(2*m),-T_exact(k,n)/(2*Lvalue*m**2),0],[0,-1/(2*m),0,0]])

formula_residuals=[]
for numerical_sample in samples:
    cctx=numerical_sample['ctx']
    cctx.set_as_current()
    cpm=numerical_sample['pm']
    cn=numerical_sample['N_int']
    for ck,Vnumeric in enumerate(numerical_sample['lyap']):
        if ck==0:
            vectors=[]
            Vformula=pf.Scalar.zero()
        elif ck==cn:
            vectors=[cctx['x_0']-cctx['x_star']]
            Vformula=-sp.Rational(1,4*cn)*vectors[0]**2+f(cctx[f'x_{ck}'])-f(cctx['x_star'])+g(cctx[f'x_{ck}'])-g(cctx['x_star'])
        else:
            vectors=[cctx['x_0']-cctx['x_star'],cctx[f'x_{ck}']-cctx['x_star'],f.grad(cctx[f'x_{ck}'])-f.grad(cctx['x_star']),f.grad(cctx['x_star'])]
            Cexact=closed_coeff(ck,cn)
            Vformula=sum((Cexact[i,j]*vectors[i]*vectors[j] for i,j in np.ndindex(Cexact.shape)),pf.Scalar.zero())
            Vformula+=sp.Rational(ck+1,2*cn-ck)*(f(cctx[f'x_{ck}'])-f(cctx['x_star']))+sp.Rational(ck,2*cn-ck)*(g(cctx[f'x_{ck}'])-g(cctx['x_star']))
        delta=cpm.eval_scalar(Vformula-Vnumeric)
        target=cpm.eval_scalar(Vnumeric)
        errors={}
        for name,part,reference in [('gram',delta.inner_prod_coords,target.inner_prod_coords),('function',delta.func_coords,target.func_coords),('offset',delta.offset,target.offset)]:
            error=float(np.max(np.abs(np.asarray(part,float)),initial=0))
            scale=float(np.max(np.abs(np.asarray(reference,float)),initial=0))
            assert error<=1e-5+1e-5*scale,(cn,ck,name,error)
            errors[name]=error
        formula_residuals.append({'N':cn,'k':ck,**errors})
        print(f'Closed-form full-coordinate check N={cn}, k={ck}: {errors}')
        if cn==4 and vectors:
            labels=V_k_basis_labels(ck)
            Cnumeric=find_symmetric_coefficient_matrix(Vnumeric,vectors,pep_context=cctx,resolve_parameters=numerical_sample['params_sp'],indep_tol=1e-7,span_tol=1e-5)
            pf.pprint_labeled_matrix(np.asarray(closed_coeff(ck,cn),dtype=object),labels,precision=7)
            pf.pprint_labeled_matrix(Cnumeric-np.asarray(closed_coeff(ck,cn),float),labels,precision=7)
print('Formula comparisons include function gaps and endpoints; no numerical match is used as the analytic proof.')
