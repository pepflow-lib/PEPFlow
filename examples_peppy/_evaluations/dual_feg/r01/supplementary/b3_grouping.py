# Residuals are <=0; nonnegative weighted residuals are added, so V is nonincreasing.
grouping_checked=False
rank_tolerance=1e-4
rank_left,rank_right=1,1
group_terms={name:term for name,term in weighted_terms.items() if name!=tau_name}
term_assignment={}
for name in group_terms:
    if name==f'A monotone:x_{N_int},x_star':
        term_assignment[name]='boundary'
    elif name==f'A Lipschitz:x_{N_int-1},x_{N_int}':
        term_assignment[name]=N_int-1
    else:
        pairs=interpolation_pairs[name]
        assert pairs is not None
        ytag=next(tag for tag in pairs if tag.startswith('y_'))
        term_assignment[name]=int(ytag.split('_')[1])
assert set(term_assignment)==set(group_terms)
assert set(S_assignment)==set(S_piece_terms)
lyap=[pf.Scalar.zero()]
partial_sum=pf.Scalar.zero()
for step in range(N_int):
    partial_sum+=sum((group_terms[name] for name,target in term_assignment.items() if target==step),pf.Scalar.zero())
    partial_sum-=sum((S_piece_terms[name] for name,target in S_assignment.items() if target==step),pf.Scalar.zero())
    lyap.append(partial_sum)
ranks=[]
singular_values=[]
for k,Vk in enumerate(lyap):
    matrix=np.asarray(pm.eval_scalar(Vk).inner_prod_coords,dtype=float)
    sv=np.linalg.svd(matrix,compute_uv=False)
    singular_values.append(sv.tolist())
    rank=int(np.linalg.matrix_rank(matrix,tol=rank_tolerance))
    ranks.append(rank)
    print(f'rank V_{k}: {rank}')
    if k==0:
        print()
retained=ranks[rank_left:N_int+1-rank_right]
print('Interior rank is constant at this N:',len(retained)>=3 and len(set(retained))==1,'boundary exclusions:',(rank_left,rank_right))
boundary_names=[name for name,step in term_assignment.items() if step=='boundary']
boundary_S=[name for name,step in S_assignment.items() if step=='boundary']
assert len(boundary_names)<=1 and len(boundary_S)<=1
leftover=sum((group_terms[name] for name in boundary_names),pf.Scalar.zero())-sum((S_piece_terms[name] for name in boundary_S),pf.Scalar.zero())
coverage=lyap[N_int]+leftover-(sum(group_terms.values(),pf.Scalar.zero())-S_scalar)
piece_diff=sum(S_piece_terms.values(),pf.Scalar.zero())-S_scalar
coverage_residuals={}
for label,expr in [('coverage',coverage),('S pieces',piece_diff)]:
    value=pm.eval_scalar(expr)
    arrs=[value.inner_prod_coords,value.func_coords,np.asarray(value.offset)]
    coverage_residuals[label]=max(float(np.max(np.abs(np.asarray(a,dtype=float)),initial=0)) for a in arrs)
    assert coverage_residuals[label]<=tol['identity_atol']
for name,piece in S_piece_terms.items():
    value=pm.eval_scalar(piece)
    assert np.allclose(value.func_coords,0,atol=1e-5,rtol=0) and np.allclose(value.offset,0,atol=1e-5,rtol=0)
    assert np.linalg.eigvalsh(np.asarray(value.inner_prod_coords,dtype=float)).min()>=-tol['psd_tol']
for k in range(N_int):
    increment=sum((group_terms[name] for name,target in term_assignment.items() if target==k),pf.Scalar.zero())
    increment-=sum((S_piece_terms[name] for name,target in S_assignment.items() if target==k),pf.Scalar.zero())
    value=pm.eval_scalar(lyap[k+1]-lyap[k]-increment)
    for a in [value.inner_prod_coords,value.func_coords,np.asarray(value.offset)]:
        assert np.allclose(np.asarray(a,dtype=float),0,atol=tol['identity_atol'],rtol=0)
grouping_checked=True
print('Full-coordinate coverage:',coverage_residuals)
