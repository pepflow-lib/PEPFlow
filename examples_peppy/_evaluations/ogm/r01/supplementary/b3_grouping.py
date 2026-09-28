# Each assigned weighted interpolation residual is <= 0, so V is nonincreasing.
# The single nonnegative S square is left for the final boundary argument.
term_assignment = {}
for name,(left,right) in interpolation_pairs.items():
    j = 0 if right == 'z_0' else int(right.split('_')[1])
    term_assignment[name] = -1 if j == 0 else j-1
S_assignment = {'terminal_square': 'boundary'}
assert set(term_assignment) == set(group_terms)
assert set(S_assignment) == set(S_piece_terms)
lyap = [pf.Scalar.zero()]
partial_sum = sum((group_terms[name] for name,target in term_assignment.items() if target == -1),pf.Scalar.zero())
for step in range(N_int):
    partial_sum += sum((group_terms[name] for name,target in term_assignment.items() if target == step),pf.Scalar.zero())
    lyap.append(partial_sum)
rank_tolerance = 1e-4
rank_left,rank_right = 1,1
ranks, singular_values = [],[]
for k,Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords,dtype=float)
    singular_values.append(np.linalg.svd(matrix,compute_uv=False).tolist())
    ranks.append(int(np.linalg.matrix_rank(matrix,tol=rank_tolerance)))
    print(f'rank V_{k}: {ranks[-1]}')
    if k == 0:
        print()
retained_ranks = ranks[rank_left:N_int+1-rank_right]
print('Interior rank is constant at this N:',len(retained_ranks)>=3 and len(set(retained_ranks))==1,'boundary exclusions:',(rank_left,rank_right))
boundary_names = []
boundary_S = ['terminal_square']
leftover = -S_piece_terms['terminal_square']
coverage = lyap[N_int]+leftover-(sum(group_terms.values(),pf.Scalar.zero())-S_scalar)
coverage_residual = coords_max(coverage)
assert max(coverage_residual) < 1e-5
for k in range(N_int):
    targets = {-1,0} if k == 0 else {k}
    increment = sum((group_terms[name] for name,target in term_assignment.items() if target in targets),pf.Scalar.zero())
    assert max(coords_max(lyap[k+1]-lyap[k]-increment)) < 1e-5
rank_credible = all(not any(rank_tolerance/10 <= s <= rank_tolerance*10 for s in values) for values in singular_values)
grouping_checked = True
