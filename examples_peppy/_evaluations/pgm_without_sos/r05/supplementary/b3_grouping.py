grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
group_terms = {name:term for name,term in weighted_terms.items() if name != tau_name}
assert set(group_terms) == set(interpolation_terms), 'Explicitly handle unexpected extras'
term_assignment = {name:int(name.split(',')[1][2:])-1 for name in group_terms}
S_assignment = {}
for label in S_piece_terms:
    pivot = len(D)-1-int(label)
    chronological_index = (pivot-3)//2 if pivot>=3 else 0
    S_assignment[label] = max(-1,min(N_int-1,chronological_index-1))
assert set(term_assignment)==set(group_terms)
assert set(S_assignment)==set(S_piece_terms)
assert all(-1<=step<N_int for step in term_assignment.values())
assert all(-1<=step<N_int for step in S_assignment.values())
# Each increment is a sum of weighted nonpositive interpolation residuals
# minus nonnegative quadratic pieces; hence V_{k+1} <= V_k.
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for k in range(N_int):
    assigned_steps = {-1,0} if k==0 else {k}
    partial_sum += sum((group_terms[name] for name,step in term_assignment.items()
                        if step in assigned_steps),pf.Scalar.zero())
    partial_sum -= sum((S_piece_terms[name] for name,step in S_assignment.items()
                        if step in assigned_steps),pf.Scalar.zero())
    lyap.append(partial_sum)
ranks=[]
singular_values=[]
for k,Vk in enumerate(lyap):
    matrix=np.asarray(pm.eval_scalar(Vk).inner_prod_coords,dtype=float)
    ranks.append(int(np.linalg.matrix_rank(matrix,tol=rank_tolerance)))
    singular_values.append(np.linalg.svd(matrix,compute_uv=False).tolist())
    print(f'rank V_{k}: {ranks[-1]}')
    if k==0:
        print()
retained_ranks=ranks[rank_left:N_int+1-rank_right]
print('Interior rank is constant at this N:', len(retained_ranks)>=3 and len(set(retained_ranks))==1,
      'boundary exclusions:',(rank_left,rank_right))
coverage_diff = lyap[N_int]-(sum(group_terms.values(),pf.Scalar.zero())-S_scalar)
piece_diff = sum(S_piece_terms.values(),pf.Scalar.zero())-S_scalar
coverage_residuals={}
for label,expression in (('coverage',coverage_diff),('S pieces',piece_diff)):
    value=pm.eval_scalar(expression)
    coverage_residuals[label]=[]
    for coords in (value.inner_prod_coords,value.func_coords,np.asarray(value.offset)):
        error=float(np.max(np.abs(np.asarray(coords,dtype=float)),initial=0))
        coverage_residuals[label].append(error)
        assert error<=tol['identity_atol']
minimum_piece_eigenvalue=0.0
for name,piece in S_piece_terms.items():
    value=pm.eval_scalar(piece)
    assert np.allclose(value.func_coords,0,atol=1e-5,rtol=0)
    assert np.allclose(value.offset,0,atol=1e-5,rtol=0)
    matrix=np.asarray(value.inner_prod_coords,dtype=float)
    mineig=float(np.linalg.eigvalsh((matrix+matrix.T)/2).min())
    minimum_piece_eigenvalue=min(minimum_piece_eigenvalue,mineig)
    assert mineig>=-1e-6
for k in range(N_int):
    assigned_steps={-1,0} if k==0 else {k}
    increment=sum((group_terms[name] for name,step in term_assignment.items() if step in assigned_steps),pf.Scalar.zero())
    increment-=sum((S_piece_terms[name] for name,step in S_assignment.items() if step in assigned_steps),pf.Scalar.zero())
    value=pm.eval_scalar(lyap[k+1]-lyap[k]-increment)
    for coords in (value.inner_prod_coords,value.func_coords,np.asarray(value.offset)):
        assert np.allclose(np.asarray(coords,dtype=float),0,atol=1e-5,rtol=0)
boundary_names=[]
boundary_S=[]
grouping_checked=True
print('Full-coordinate coverage residuals:',coverage_residuals)
print('Minimum piece eigenvalue:',minimum_piece_eigenvalue)
