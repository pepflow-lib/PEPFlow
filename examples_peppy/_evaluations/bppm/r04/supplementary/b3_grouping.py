# All residuals are normalized <=0, with nonnegative numerical multipliers.
# Thus each increment is nonpositive; V_0=0 and V_k is nonincreasing.
grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
group_terms = {name: term for name, term in weighted_terms.items() if name != tau_name}
term_assignment = {}
for name in group_terms:
    owner, points = name.split(':')
    ri, ci = points.split(',')
    if owner == 'h' and ri == 'x_star':
        assert ci == f'x_{N_int}'
        term_assignment[name] = 'boundary'
    elif ri == 'x_star':
        term_assignment[name] = int(ci.split('_')[1])-1
    else:
        i, j = int(ri.split('_')[1]), int(ci.split('_')[1])
        assert abs(i-j) == 1
        term_assignment[name] = max(i,j)-1
assert set(term_assignment) == set(group_terms)
assert set(S_assignment) == set(S_piece_terms)
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for step in range(N_int):
    partial_sum += sum((group_terms[name] for name, target in term_assignment.items() if target == step), pf.Scalar.zero())
    partial_sum -= sum((S_piece_terms[name] for name, target in S_assignment.items() if target == step), pf.Scalar.zero())
    lyap.append(partial_sum)
ranks, singular_values = [], []
for k,Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords,dtype=float)
    singular = np.linalg.svd(matrix,compute_uv=False)
    rank = int(np.count_nonzero(singular > rank_tolerance))
    ranks.append(rank)
    singular_values.append(singular.tolist())
    print(f'rank V_{k}: {rank}')
    if k == 0:
        print()
retained_ranks = ranks[rank_left:N_int+1-rank_right]
print('Interior rank is constant at this N:',len(retained_ranks)>=3 and len(set(retained_ranks))==1,'boundary exclusions:',(rank_left,rank_right))
rank_credible = all(not np.any((np.asarray(s)>rank_tolerance/10)&(np.asarray(s)<rank_tolerance*10)) for s in singular_values)
assert rank_credible
