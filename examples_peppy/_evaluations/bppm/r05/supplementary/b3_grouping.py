"""Adjacent-index partial sums; all increments are nonpositive."""
grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
group_terms = {name: term for name, term in weighted_terms.items() if name != tau_name}
term_assignment = {}
for name in group_terms:
    if name == f'h:x_star,x_{N_int}':
        term_assignment[name] = 'boundary'
    else:
        owner, pair = name.split(':')
        first, second = pair.split(',')
        if owner == 'f' and first == 'x_star':
            term_assignment[name] = int(second.split('_')[1]) - 1
        else:
            i, j = int(first.split('_')[1]), int(second.split('_')[1])
            assert abs(i-j) == 1
            term_assignment[name] = max(i, j) - 1
assert set(term_assignment) == set(group_terms)
assert set(S_assignment) == set(S_piece_terms)
assert all(step in set(range(N_int)) | {'boundary'} for step in term_assignment.values())

# Positive inequality weights and subtracted PSD pieces ensure V_{k+1} <= V_k.
lyap = [pf.Scalar.zero()]
partial_sum = pf.Scalar.zero()
for step in range(N_int):
    partial_sum += sum((group_terms[name] for name, target in term_assignment.items()
                        if target == step), pf.Scalar.zero())
    partial_sum -= sum((S_piece_terms[name] for name, target in S_assignment.items()
                        if target == step), pf.Scalar.zero())
    lyap.append(partial_sum)
ranks = []
singular_values = []
for k, Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, dtype=float)
    singular_values.append(np.linalg.svd(matrix, compute_uv=False).tolist())
    rank = int(np.linalg.matrix_rank(matrix, tol=rank_tolerance))
    ranks.append(rank)
    print(f'rank V_{k}: {rank}')
    if k == 0:
        print()
retained_ranks = ranks[rank_left:N_int+1-rank_right]
print('Interior rank is constant at this N:', len(retained_ranks)>=3 and len(set(retained_ranks))==1,
      'boundary exclusions:', (rank_left, rank_right))

boundary_names = [name for name, step in term_assignment.items() if step == 'boundary']
boundary_S = [name for name, step in S_assignment.items() if step == 'boundary']
assert len(boundary_names) <= 1 and len(boundary_S) <= 1
leftover = sum((group_terms[name] for name in boundary_names), pf.Scalar.zero())
leftover -= sum((S_piece_terms[name] for name in boundary_S), pf.Scalar.zero())
coverage_diff = lyap[N_int] + leftover - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
piece_diff = sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar
coverage_residuals = {}
for label, expression in (('coverage', coverage_diff), ('S pieces', piece_diff)):
    value = pm.eval_scalar(expression)
    components = [np.asarray(value.inner_prod_coords,dtype=float), np.asarray(value.func_coords,dtype=float), np.asarray(value.offset,dtype=float)]
    coverage_residuals[label] = max(float(np.max(np.abs(v),initial=0)) for v in components)
    assert all(np.allclose(v, 0, atol=1e-5, rtol=0) for v in components)
for k in range(N_int):
    increment = sum((group_terms[name] for name, step in term_assignment.items() if step == k), pf.Scalar.zero())
    increment -= sum((S_piece_terms[name] for name, step in S_assignment.items() if step == k), pf.Scalar.zero())
    value = pm.eval_scalar(lyap[k+1] - lyap[k] - increment)
    assert all(np.allclose(np.asarray(v,dtype=float),0,atol=1e-5,rtol=0)
               for v in (value.inner_prod_coords, value.func_coords, value.offset))
for piece in S_piece_terms.values():
    value = pm.eval_scalar(piece)
    matrix = np.asarray(value.inner_prod_coords,dtype=float)
    assert np.allclose(np.asarray(value.func_coords,dtype=float),0,atol=1e-5,rtol=0)
    assert np.allclose(float(value.offset),0,atol=1e-5,rtol=0)
    assert np.linalg.eigvalsh((matrix+matrix.T)/2).min()>=-1e-6
assert all(value >= -1e-6 for value in saved_duals.values() if value is not None)
grouping_checked = True
rank_credible = all(not any(rank_tolerance/10 <= s <= rank_tolerance*10 for s in values) for values in singular_values)
print('Coverage and increment identities passed:', coverage_residuals)
