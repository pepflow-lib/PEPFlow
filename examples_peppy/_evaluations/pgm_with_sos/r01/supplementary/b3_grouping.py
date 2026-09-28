# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Normalized interpolation residuals are <=0; subtracting each PSD square gives a nonincreasing sequence.
group_terms = {}
term_assignment = {}
for c, origin, _, _ in entries:
    if c.name == "initial_condition" or b2["named_dual_values"][c.name] is None:
        continue
    assert origin == "interpolation"
    residual = c.lhs - c.rhs
    if c.cmp == pf.Comparator.GE:
        residual = -residual
    group_terms[c.name] = b2["named_dual_values"][c.name] * residual
    row, col = c.name.split(":")[1].split(",")
    j = int(col[2:])
    term_assignment[c.name] = -1 if j == 0 else j - 1
assert set(term_assignment) == set(group_terms)
assert set(S_assignment) == set(S_piece_terms)
lyap = [pf.Scalar.zero()]
partial_sum = sum(
    (group_terms[name] for name, target in term_assignment.items() if target == -1),
    pf.Scalar.zero(),
)
for step in range(N):
    partial_sum += sum(
        (
            group_terms[name]
            for name, target in term_assignment.items()
            if target == step
        ),
        pf.Scalar.zero(),
    )
    partial_sum -= sum(
        (
            S_piece_terms[name]
            for name, target in S_assignment.items()
            if target == step
        ),
        pf.Scalar.zero(),
    )
    lyap.append(partial_sum)
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
ranks = []
singular_values = []
for k, Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, dtype=float)
    sv = np.linalg.svd(matrix, compute_uv=False)
    singular_values.append(sv.tolist())
    rank = int(np.linalg.matrix_rank(matrix, tol=rank_tolerance))
    ranks.append(rank)
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()
retained = ranks[rank_left : N + 1 - rank_right]
print(
    "Interior rank is constant at this N:",
    len(retained) >= 3 and len(set(retained)) == 1,
    "boundary exclusions:",
    (rank_left, rank_right),
)
coverage = lyap[N] - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
coverage_eval = pm.eval_scalar(coverage)
coverage_residual = max(
    maxabs(v)
    for v in (
        coverage_eval.inner_prod_coords,
        coverage_eval.func_coords,
        coverage_eval.offset,
    )
)
assert coverage_residual <= 1e-5
increment_residuals = []
for k in range(N):
    assigned = {-1, 0} if k == 0 else {k}
    increment = sum(
        (
            group_terms[name]
            for name, step in term_assignment.items()
            if step in assigned
        ),
        pf.Scalar.zero(),
    )
    increment -= sum(
        (
            S_piece_terms[name]
            for name, step in S_assignment.items()
            if step in assigned
        ),
        pf.Scalar.zero(),
    )
    ev = pm.eval_scalar(lyap[k + 1] - lyap[k] - increment)
    error = max(maxabs(v) for v in (ev.inner_prod_coords, ev.func_coords, ev.offset))
    increment_residuals.append(error)
    assert error <= 1e-5
grouping_checked = True
print("Full-coordinate coverage residual:", coverage_residual)
