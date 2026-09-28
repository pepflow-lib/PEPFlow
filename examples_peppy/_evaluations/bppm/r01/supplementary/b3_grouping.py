# All normalized interpolation residuals are <=0, with nonnegative duals.
# The accumulated sums therefore have nonpositive increments.
group_terms = {**interpolation_terms, **extra_terms}
term_assignment = {}
for name in group_terms:
    if name == f'h:x_star,x_{N_int}':
        term_assignment[name] = 'boundary'
    else:
        pair = name.split(':')[1].split(',')
        indices = [int(tag[2:]) for tag in pair if tag != 'x_star']
        term_assignment[name] = max(indices)-1
assert set(term_assignment) == set(group_terms)
assert not extra_terms
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for k in range(N_int):
    partial_sum += sum((term for name,term in group_terms.items() if term_assignment[name]==k),pf.Scalar.zero())
    partial_sum -= sum((term for name,term in S_piece_terms.items() if S_assignment[name]==k),pf.Scalar.zero())
    lyap.append(partial_sum)
rank_tolerance = 1e-4
rank_left,rank_right=1,1
ranks=[]
singular_values=[]
for k,Vk in enumerate(lyap):
    matrix=np.asarray(pm.eval_scalar(Vk).inner_prod_coords,dtype=float)
    singular=np.linalg.svd(matrix,compute_uv=False)
    singular_values.append(singular.tolist())
    rank=int(np.linalg.matrix_rank(matrix,tol=rank_tolerance))
    ranks.append(rank)
    print(f'rank V_{k}: {rank}')
    if k==0:
        print()
retained_ranks=ranks[rank_left:N_int+1-rank_right]
print('Interior rank is constant at this N:',len(retained_ranks)>=3 and len(set(retained_ranks))==1,'boundary exclusions:',(rank_left,rank_right))
rank_credible=all(not any(rank_tolerance/10 < s < rank_tolerance*10 for s in sv) for sv in singular_values)
assert rank_credible
