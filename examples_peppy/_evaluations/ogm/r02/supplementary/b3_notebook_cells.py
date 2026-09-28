"""Partial-sum construction and full-coordinate coverage checks for B3."""

DECOMPOSITION = '''# The whole selected S is one PSD boundary piece; retain every matrix entry.
S_scalar = sum((float(S_array[i,j])*basis[i]*basis[j] for i,j in np.ndindex(S_array.shape)), pf.Scalar.zero())
S_piece_terms = {"terminal_S": S_scalar}
S_assignment = {"terminal_S": "boundary"}
piece_eval = pm.eval_scalar(S_piece_terms["terminal_S"])
assert np.allclose(np.asarray(piece_eval.inner_prod_coords, dtype=float), S_array, atol=1e-5, rtol=0)
assert np.allclose(np.asarray(piece_eval.func_coords, dtype=float), 0, atol=1e-5, rtol=0)
assert abs(float(piece_eval.offset)) <= 1e-5
assert np.linalg.eigvalsh(np.asarray(piece_eval.inner_prod_coords, dtype=float)).min() >= -1e-6
'''

GROUPING = '''# Residuals R_c <= 0 and nonnegative duals make these V_k nonincreasing.
grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
weighted_terms = {}
interpolation_terms = {}
extra_duals = {}
for constraint, origin, owner, group in entries:
    value = b2["named_dual_values"][constraint.name]
    if constraint.name in pb.relaxed_constraints:
        assert value is None
        continue
    assert value is not None
    residual = constraint.lhs-constraint.rhs
    if constraint.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
        residual = -residual
    weighted_terms[constraint.name] = float(value)*residual
    if origin == "interpolation":
        interpolation_terms[constraint.name] = weighted_terms[constraint.name]
    elif constraint.name != "initial_condition":
        extra_duals[constraint.name] = value
assert not extra_duals
group_terms = {name: term for name, term in weighted_terms.items() if name != "initial_condition"}
term_assignment = {}
for name in group_terms:
    ri, ci = name.split(":")[1].split(",")
    i, j = point_index(ri), point_index(ci)
    if i == -1 and j == 0:
        term_assignment[name] = -1
    elif (i == -1 or i == j-1) and 1 <= j <= N:
        term_assignment[name] = j-1
    else:
        raise ValueError("Unassigned active interpolation: " + name)
assert set(term_assignment) == set(group_terms)
assert set(S_assignment) == set(S_piece_terms)
lyap = [pf.Scalar.zero()]
partial_sum = sum((group_terms[name] for name, step in term_assignment.items() if step == -1), pf.Scalar.zero())
for step in range(N):
    partial_sum += sum((group_terms[name] for name, target in term_assignment.items() if target == step), pf.Scalar.zero())
    partial_sum -= sum((S_piece_terms[name] for name, target in S_assignment.items() if target == step), pf.Scalar.zero())
    lyap.append(partial_sum)
ranks, singular_values = [], []
for k, Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, dtype=float)
    singular_values.append(np.linalg.svd(matrix, compute_uv=False).tolist())
    rank = int(np.linalg.matrix_rank(matrix, tol=rank_tolerance))
    ranks.append(rank)
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()
retained_ranks = ranks[rank_left:N+1-rank_right]
print("Interior rank is constant at this N:", len(retained_ranks) >= 3 and len(set(retained_ranks)) == 1,
      "boundary exclusions:", (rank_left, rank_right))

boundary_names = [name for name, step in term_assignment.items() if step == "boundary"]
boundary_S = [name for name, step in S_assignment.items() if step == "boundary"]
assert len(boundary_names) <= 1 and len(boundary_S) <= 1
leftover = sum((group_terms[name] for name in boundary_names), pf.Scalar.zero())
leftover -= sum((S_piece_terms[name] for name in boundary_S), pf.Scalar.zero())
coverage_diff = lyap[N]+leftover-(sum(group_terms.values(), pf.Scalar.zero())-S_scalar)
coverage_checks = []
for label, expression in [("coverage", coverage_diff), ("pieces", sum(S_piece_terms.values(), pf.Scalar.zero())-S_scalar)]:
    evaluated = pm.eval_scalar(expression)
    errors = [float(np.max(np.abs(np.asarray(coords, dtype=float)), initial=0))
              for coords in (evaluated.inner_prod_coords, evaluated.func_coords, evaluated.offset)]
    assert max(errors) <= 1e-5
    coverage_checks.append({"label": label, "gram_function_offset": errors})
step_errors = []
for k in range(N):
    assigned_steps = {-1, 0} if k == 0 else {k}
    increment = sum((group_terms[name] for name, step in term_assignment.items() if step in assigned_steps), pf.Scalar.zero())
    increment -= sum((S_piece_terms[name] for name, step in S_assignment.items() if step in assigned_steps), pf.Scalar.zero())
    evaluated = pm.eval_scalar(lyap[k+1]-lyap[k]-increment)
    errors = [float(np.max(np.abs(np.asarray(coords, dtype=float)), initial=0))
              for coords in (evaluated.inner_prod_coords, evaluated.func_coords, evaluated.offset)]
    assert max(errors) <= 1e-5
    step_errors.append(errors)
grouping_checked = True
print("Full-coordinate coverage and step checks passed; only terminal S is left for the boundary argument.")
'''
