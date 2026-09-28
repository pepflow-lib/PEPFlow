grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
group_terms = {name:term for name,term in weighted_terms.items() if name != 'initial_condition'}
term_assignment = {}
for name in group_terms:
    owner, pair = name.split(':')
    first, second = pair.split(',')
    if name == f'h:x_star,x_{N_int}':
        term_assignment[name] = 'boundary'
    elif first == 'x_star' and owner == 'f':
        term_assignment[name] = int(second.split('_')[1])-1
    else:
        i,j = int(first.split('_')[1]),int(second.split('_')[1])
        assert abs(i-j)==1
        term_assignment[name] = max(i,j)-1
S_assignment = {'S_full':'boundary'}
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for step in range(N_int):
    partial_sum += sum((group_terms[name] for name,target in term_assignment.items() if target == step),pf.Scalar.zero())
    partial_sum -= sum((S_piece_terms[name] for name,target in S_assignment.items() if target == step),pf.Scalar.zero())
    lyap.append(partial_sum)
ranks, singular_values = [], []
for k,Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords,dtype=float)
    values = np.linalg.svd(matrix,compute_uv=False)
    singular_values.append(values.tolist())
    rank = int(np.linalg.matrix_rank(matrix,tol=rank_tolerance))
    ranks.append(rank)
    print(f'rank V_{k}: {rank}')
    if k == 0:
        print()
retained = ranks[rank_left:N_int+1-rank_right]
print('Interior rank is constant at this N:',len(retained)>=3 and len(set(retained))==1,'boundary exclusions:',(rank_left,rank_right))
boundary_names = [name for name,target in term_assignment.items() if target=='boundary']
boundary_S = [name for name,target in S_assignment.items() if target=='boundary']
assert len(boundary_names)<=1 and len(boundary_S)<=1
leftover = sum((group_terms[name] for name in boundary_names),pf.Scalar.zero())-sum((S_piece_terms[name] for name in boundary_S),pf.Scalar.zero())
coverage = lyap[N_int]+leftover-(sum(group_terms.values(),pf.Scalar.zero())-S_scalar)
coverage_errors = []
for expression in (coverage,sum(S_piece_terms.values(),pf.Scalar.zero())-S_scalar):
    value = pm.eval_scalar(expression)
    errors = [float(np.max(np.abs(np.asarray(coords,dtype=float)),initial=0)) for coords in (value.inner_prod_coords,value.func_coords,np.asarray(value.offset))]
    coverage_errors.append(errors)
    assert max(errors)<=1e-5
for k in range(N_int):
    increment = sum((group_terms[name] for name,target in term_assignment.items() if target==k),pf.Scalar.zero())
    value = pm.eval_scalar(lyap[k+1]-lyap[k]-increment)
    assert all(np.allclose(np.asarray(coords,dtype=float),0,atol=1e-5,rtol=0) for coords in (value.inner_prod_coords,value.func_coords,np.asarray(value.offset)))
# Every increment is a sum of nonnegative numerical multipliers times convex residuals <=0.
assert all(certificate['named_dual_values'][name]>=-1e-6 for name in group_terms)
assert set(term_assignment)==set(group_terms) and set(S_assignment)==set(S_piece_terms)
grouping_checked = True
rank_credible = all(all(value<rank_tolerance/10 or value>rank_tolerance*10 for value in values) for values in singular_values)
print('Full-coordinate coverage errors:',coverage_errors)
