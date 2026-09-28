# Reuse the saved complete reverse-LDL factors; never truncate small pieces.
D = np.asarray(certificate['numerical_decomposition']['D'], dtype=float)
E = np.asarray(certificate['numerical_decomposition']['ell_coords'], dtype=float)
assert np.array_equal(D, np.diag(np.diag(D)))
ell = [sum((float(coef)*vector for coef,vector in zip(row,basis)), pf.Vector.zero()) for row in E]
S_piece_terms = {i: float(D[i,i])*ell[i]**2 for i in range(len(D))}
S_assignment = {i: N_int-i//2-1 if i < 2*N_int else -1 for i in S_piece_terms}
assert np.allclose(E.T@D@E, S_array, atol=1e-4, rtol=1e-5)
for piece in S_piece_terms.values():
    evaluated_piece = pm.eval_scalar(piece)
    assert np.allclose(evaluated_piece.func_coords, 0, atol=1e-5, rtol=0)
    assert abs(float(evaluated_piece.offset)) <= 1e-5
    assert np.linalg.eigvalsh(np.asarray(evaluated_piece.inner_prod_coords,float)).min() >= -1e-6
# CELL
# Nonpositive interpolation residuals minus nonnegative S pieces give V_(k+1)<=V_k.
grouping_checked = False
group_terms = {name:term for name,term in weighted_terms.items() if name != tau_name}
term_assignment = {}
for name in group_terms:
    pair = interpolation_pairs[name]
    assert pair is not None
    ri, ci = pair
    j = int(ci[2:])
    assert ri == 'x_star' or int(ri[2:])+1 == j
    term_assignment[name] = j-1
assert set(term_assignment) == set(group_terms)
assert set(S_assignment) == set(S_piece_terms)
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
lyap = [pf.Scalar.zero()]
partial_sum = sum((term for name,term in group_terms.items() if term_assignment[name] == -1), pf.Scalar.zero())
partial_sum -= sum((piece for i,piece in S_piece_terms.items() if S_assignment[i] == -1), pf.Scalar.zero())
for k in range(N_int):
    partial_sum += sum((term for name,term in group_terms.items() if term_assignment[name] == k), pf.Scalar.zero())
    partial_sum -= sum((piece for i,piece in S_piece_terms.items() if S_assignment[i] == k), pf.Scalar.zero())
    lyap.append(partial_sum)
ranks = []
singular_values = []
for k,Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, float)
    singular = np.linalg.svd(matrix, compute_uv=False)
    singular_values.append(singular.tolist())
    rank = int(np.sum(singular > rank_tolerance))
    ranks.append(rank)
    print(f'rank V_{k}: {rank}')
    if k == 0:
        print()
retained_ranks = ranks[rank_left:N_int+1-rank_right]
print('Interior rank is constant at this N:',len(retained_ranks)>=3 and len(set(retained_ranks))==1,'boundary exclusions:',(rank_left,rank_right))
# No interpolation or S piece is omitted or held at the terminal boundary.
coverage_diff = lyap[N_int] - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
piece_diff = sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar
checks = [('coverage',coverage_diff), ('S pieces',piece_diff)]
for k in range(N_int):
    targets = {-1,0} if k == 0 else {k}
    increment = sum((term for name,term in group_terms.items() if term_assignment[name] in targets),pf.Scalar.zero())
    increment -= sum((piece for i,piece in S_piece_terms.items() if S_assignment[i] in targets),pf.Scalar.zero())
    checks.append((f'increment_{k}',lyap[k+1]-lyap[k]-increment))
coverage_residuals = {}
for label, expression in checks:
    evaluated = pm.eval_scalar(expression)
    residual = max(float(np.max(np.abs(np.asarray(coords,float)),initial=0)) for coords in
                   (evaluated.inner_prod_coords,evaluated.func_coords,np.asarray(evaluated.offset)))
    coverage_residuals[label] = residual
    assert residual <= 1e-5
assert all(value is not None and value >= -1e-6 for name,value in saved_duals.items() if name in group_terms)
grouping_checked = True
print('Full-coordinate coverage and increment checks:',coverage_residuals)

