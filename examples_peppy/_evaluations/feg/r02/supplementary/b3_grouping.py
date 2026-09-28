grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
group_terms = {name:term for name,term in weighted_terms.items() if name != tau_name}
term_assignment = {}
for name in group_terms:
    if name == f'A monotone:x_{N_int},x_star':
        term_assignment[name] = 'boundary'
    elif name == 'A Lipschitz:x_1,x_1/2':
        term_assignment[name] = 0
    elif name.startswith('A monotone:'):
        point = name.split(':')[1].split(',')[0]
        term_assignment[name] = int(point.split('_')[1])
    elif name.startswith('A Lipschitz:'):
        point = name.split(':')[1].split(',')[0]
        term_assignment[name] = int(point.split('_')[1].split('+')[0])
    else:
        raise ValueError('Unassigned term '+name)
assert set(term_assignment) == set(group_terms)
assert all(t == 'boundary' or t in range(N_int) for t in term_assignment.values())
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for step in range(N_int):
    partial_sum += sum((group_terms[name] for name,t in term_assignment.items() if t==step),pf.Scalar.zero())
    partial_sum -= sum((S_piece_terms[name] for name,t in S_assignment.items() if t==step),pf.Scalar.zero())
    lyap.append(partial_sum)
ranks=[]
singular_values=[]
for k,Vk in enumerate(lyap):
    matrix=np.asarray(pm.eval_scalar(Vk).inner_prod_coords,dtype=float)
    spectrum=np.linalg.svd(matrix,compute_uv=False)
    singular_values.append(spectrum.tolist())
    ranks.append(int(np.linalg.matrix_rank(matrix,tol=rank_tolerance)))
    print(f'rank V_{k}: {ranks[-1]}')
    if k==0:
        print()
retained_ranks=ranks[rank_left:N_int+1-rank_right]
print('Interior rank is constant at this N:',len(retained_ranks)>=3 and len(set(retained_ranks))==1,'boundary exclusions:',(rank_left,rank_right))
boundary_names=[name for name,t in term_assignment.items() if t=='boundary']
boundary_S=[name for name,t in S_assignment.items() if t=='boundary']
assert len(boundary_names)<=1 and len(boundary_S)<=1
leftover=sum((group_terms[name] for name in boundary_names),pf.Scalar.zero())-sum((S_piece_terms[name] for name in boundary_S),pf.Scalar.zero())
coverage_diff=lyap[N_int]+leftover-(sum(group_terms.values(),pf.Scalar.zero())-S_scalar)
coverage_residuals=[]
for expr in (coverage_diff,sum(S_piece_terms.values(),pf.Scalar.zero())-S_scalar):
    evaluated=pm.eval_scalar(expr)
    coverage_residuals.append(max(float(np.max(np.abs(np.asarray(coords,dtype=float)),initial=0)) for coords in (evaluated.inner_prod_coords,evaluated.func_coords,np.asarray(evaluated.offset))))
    assert coverage_residuals[-1]<=tol['identity_atol']
for piece in S_piece_terms.values():
    evaluated=pm.eval_scalar(piece)
    assert np.allclose(evaluated.func_coords,0,atol=tol['identity_atol'],rtol=0)
    assert abs(float(evaluated.offset))<=tol['identity_atol']
    assert np.linalg.eigvalsh(np.asarray(evaluated.inner_prod_coords,dtype=float)).min()>=-tol['psd_tol']
for k in range(N_int):
    increment=sum((group_terms[name] for name,t in term_assignment.items() if t==k),pf.Scalar.zero())
    increment-=sum((S_piece_terms[name] for name,t in S_assignment.items() if t==k),pf.Scalar.zero())
    evaluated=pm.eval_scalar(lyap[k+1]-lyap[k]-increment)
    for coords in (evaluated.inner_prod_coords,evaluated.func_coords,np.asarray(evaluated.offset)):
        assert np.allclose(np.asarray(coords,dtype=float),0,atol=tol['identity_atol'],rtol=0)
# Every increment is a sum of nonpositive interpolation residuals with nonnegative multipliers.
# Terminal monotonicity and PSD terms remain boundary obligations; the normalization is separate.
grouping_checked=True
print('Full-coordinate coverage and nonincreasing-sign checks passed:',coverage_residuals)
