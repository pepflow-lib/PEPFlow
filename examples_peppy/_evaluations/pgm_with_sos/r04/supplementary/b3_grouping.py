# Direct pieces from the B2 aid, each a sum of three nonnegative squares.
pieces, coefficients, vectors = supplied_sos(ctx, N_int, 1)
S_piece_terms = {f'S_{i+1}':piece for i,piece in enumerate(pieces)}
S_assignment = {name:i for i,name in enumerate(S_piece_terms)}
# With interpolation residuals <= 0, every assigned contribution minus its
# nonnegative S piece gives a nonpositive increment.
group_terms = {name:term for name,term in weighted_terms.items() if name != tau_name}
term_assignment = {}
for name in group_terms:
    left, right = name.split(':')[1].split(',')
    term_assignment[name] = int(right[2:])-1
assert set(term_assignment) == set(group_terms)
assert set(S_assignment) == set(S_piece_terms)
lyap = [pf.Scalar.zero()]
partial_sum = sum((term for name,term in group_terms.items() if term_assignment[name] == -1), pf.Scalar.zero())
for step in range(N_int):
    partial_sum += sum((term for name,term in group_terms.items() if term_assignment[name] == step), pf.Scalar.zero())
    partial_sum -= S_piece_terms[f'S_{step+1}']
    lyap.append(partial_sum)
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
ranks, singular_values = [], []
for k, value in enumerate(lyap):
    matrix = pm.eval_scalar(value).inner_prod_coords.astype(float)
    singular_values.append(np.linalg.svd(matrix,compute_uv=False).tolist())
    rank = int(np.linalg.matrix_rank(matrix,tol=rank_tolerance))
    ranks.append(rank)
    print(f'rank V_{k}: {rank}')
    if k == 0:
        print()
retained_ranks = ranks[rank_left:N_int+1-rank_right]
print('Interior rank is constant at this N:', len(retained_ranks)>=3 and len(set(retained_ranks))==1,'boundary exclusions:',(rank_left,rank_right))
assert len(retained_ranks)>=3 and len(set(retained_ranks))==1
# Credibility check records all singular values, including numerical residuals.
# No retained singular value lies in [tolerance/2, 2*tolerance].
rank_credible = all(not any(5e-5 <= v <= 2e-4 for v in singular_values[k]) for k in range(1,N_int))
assert rank_credible


