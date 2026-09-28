grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1,1
group_terms = {name:term for name,term in weighted_terms.items() if name != tau_name}
term_assignment = {}
for name in group_terms:
    left_tag,right_tag = name.split(':')[1].split(',')
    j = 0 if right_tag=='z_0' else int(right_tag.split('_')[1])
    if left_tag=='x_star' and j==0:
        term_assignment[name] = -1
    elif left_tag=='x_star' or left_tag==('z_0' if j==1 else f'x_{j-1}'):
        term_assignment[name] = j-1
    else:
        raise ValueError(f'Unassigned term {name}')
S_assignment = {'terminal_square':'boundary'}
assert set(term_assignment)==set(group_terms)
lyap = [pf.Scalar.zero()]
partial_sum = sum((term for name,term in group_terms.items() if term_assignment[name]==-1),pf.Scalar.zero())
for step in range(N_int):
    partial_sum += sum((term for name,term in group_terms.items() if term_assignment[name]==step),pf.Scalar.zero())
    partial_sum -= sum((term for name,term in S_piece_terms.items() if S_assignment[name]==step),pf.Scalar.zero())
    lyap.append(partial_sum)
ranks,singular_values = [],[]
for k,Vk in enumerate(lyap):
    M = np.asarray(pm.eval_scalar(Vk).inner_prod_coords,dtype=float)
    ranks.append(int(np.linalg.matrix_rank(M,tol=rank_tolerance)))
    singular_values.append(np.linalg.svd(M,compute_uv=False).tolist())
    print(f'rank V_{k}: {ranks[-1]}')
    if k==0:
        print()
retained = ranks[rank_left:N_int+1-rank_right]
print('Interior rank is constant at this N:',len(retained)>=3 and len(set(retained))==1,'boundary exclusions:',(rank_left,rank_right))
boundary_names = [name for name,step in term_assignment.items() if step=='boundary']
boundary_S = [name for name,step in S_assignment.items() if step=='boundary']
assert len(boundary_names)<=1 and len(boundary_S)<=1
leftover = sum((group_terms[name] for name in boundary_names),pf.Scalar.zero())-sum((S_piece_terms[name] for name in boundary_S),pf.Scalar.zero())
coverage_diff = lyap[N_int]+leftover-(sum(group_terms.values(),pf.Scalar.zero())-S_scalar)
coverage_residuals = {}
for label,expression in [('coverage',coverage_diff),('S_pieces',sum(S_piece_terms.values(),pf.Scalar.zero())-S_scalar)]:
    ev = pm.eval_scalar(expression)
    maxima = [float(np.max(np.abs(np.asarray(coords,dtype=float)),initial=0)) for coords in (ev.inner_prod_coords,ev.func_coords,np.asarray(ev.offset))]
    coverage_residuals[label] = maxima
    assert max(maxima)<=tol['identity_atol']
for name,piece in S_piece_terms.items():
    ev = pm.eval_scalar(piece)
    assert np.allclose(ev.func_coords,0,atol=1e-5,rtol=0)
    assert abs(float(ev.offset))<=1e-5
    assert np.linalg.eigvalsh(np.asarray(ev.inner_prod_coords,dtype=float)).min()>=-1e-6
for k in range(N_int):
    assigned = {-1,0} if k==0 else {k}
    increment = sum((group_terms[name] for name,step in term_assignment.items() if step in assigned),pf.Scalar.zero())-sum((S_piece_terms[name] for name,step in S_assignment.items() if step in assigned),pf.Scalar.zero())
    ev = pm.eval_scalar(lyap[k+1]-lyap[k]-increment)
    for coords in (ev.inner_prod_coords,ev.func_coords,np.asarray(ev.offset)):
        assert np.allclose(np.asarray(coords,dtype=float),0,atol=1e-5,rtol=0)
# Each weighted interpolation residual is <=0 and each subtracted square >=0.
# Hence V_{k+1}<=V_k, including all three initial interpolation contributions.
grouping_checked = True
print('Coverage residuals:',coverage_residuals)
# Singular values are retained in supplementary evidence, without a notebook dump.

