# B3 provisional partial sums at N=4, using the rechecked numerical certificate.
# %%
D_saved=np.asarray(b2['numerical_decomposition']['D'],dtype=float)
E_saved=np.asarray(b2['numerical_decomposition']['ell_coords'],dtype=float)
assert np.allclose(E_saved.T@D_saved@E_saved,S_array,atol=1e-5,rtol=0)
assert np.allclose(D_saved,np.diag(np.diag(D_saved)),atol=0,rtol=0)
ell_saved=[sum((float(c)*v for c,v in zip(row,basis)),pf.Vector.zero()) for row in E_saved]
S_piece_terms={i:float(D_saved[i,i])*ell_saved[i]**2 for i in range(len(D_saved))}
group_terms={c.name:duals[c.name]*(pf.Scalar.zero()+c.lhs-c.rhs) for c,*_ in entries
             if c.name!='initial_condition' and duals[c.name] is not None}
term_assignment={name:int(name.split(',')[1][2:])-1 for name in group_terms}
basis_times=[0 if label in ['x_0','x_star','grad_f(x_star)'] else int(label.split('x_')[1].split(')')[0])
             for label in selected['basis_vectors']]
S_assignment={i:max(0,max((basis_times[j] for j,v in enumerate(row) if abs(v)>1e-5),default=0)-1)
              for i,row in enumerate(E_saved)}
lyap=[pf.Scalar.zero()]
partial_sum=sum((group_terms[name] for name,target in term_assignment.items() if target==-1),pf.Scalar.zero())
for step in range(N):
    partial_sum+=sum((group_terms[name] for name,target in term_assignment.items() if target==step),pf.Scalar.zero())
    partial_sum-=sum((S_piece_terms[i] for i,target in S_assignment.items() if target==step),pf.Scalar.zero())
    lyap.append(partial_sum)
ranks=[]
singular_values=[]
for k,Vk in enumerate(lyap):
    sv=np.linalg.svd(np.asarray(pm.eval_scalar(Vk).inner_prod_coords,dtype=float),compute_uv=False)
    singular_values.append(sv.tolist())
    ranks.append(int(np.sum(sv>1e-4)))
    print(f'rank V_{k}: {ranks[-1]}')
    if k==0:
        print()
print('Interior rank is constant at this N:',len(set(ranks[1:N]))==1,'boundary exclusions:',(1,1))
S_scalar=sum((float(S_array[i,j])*basis[i]*basis[j] for i,j in np.ndindex(S_array.shape)),pf.Scalar.zero())
coverage=lyap[N]-(sum(group_terms.values(),pf.Scalar.zero())-S_scalar)
piece_diff=sum(S_piece_terms.values(),pf.Scalar.zero())-S_scalar
coverage_residuals={}
for label,expression in [('coverage',coverage),('pieces',piece_diff)]:
    value=pm.eval_scalar(expression)
    maxima=[max_abs(value.inner_prod_coords),max_abs(value.func_coords),max_abs(value.offset)]
    coverage_residuals[label]=maxima
    assert max(maxima)<1e-5
piece_min_eigs=[]
for piece in S_piece_terms.values():
    value=pm.eval_scalar(piece)
    assert max_abs(value.func_coords)==0 and max_abs(value.offset)==0
    piece_min_eigs.append(float(np.linalg.eigvalsh(np.asarray(value.inner_prod_coords,dtype=float)).min()))
assert min(piece_min_eigs)>=-1e-6
for k in range(N):
    steps={-1,0} if k==0 else {k}
    increment=sum((group_terms[name] for name,target in term_assignment.items() if target in steps),pf.Scalar.zero())
    increment-=sum((S_piece_terms[i] for i,target in S_assignment.items() if target in steps),pf.Scalar.zero())
    value=pm.eval_scalar(lyap[k+1]-lyap[k]-increment)
    assert max(max_abs(value.inner_prod_coords),max_abs(value.func_coords),max_abs(value.offset))<1e-5
print('Full-coordinate coverage residuals:',coverage_residuals)
print('Every interpolation contribution and S piece is assigned; no terminal leftovers. Normalization remains a boundary term.')
print('Increments are nonpositive interpolation residuals minus PSD pieces, hence the intended direction is nonincreasing.')
