# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Every increment is a sum of nonpositive weighted residuals minus PSD pieces.
grouping_checked = False
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
group_terms = {name: term for name, term in weighted_terms.items() if name != tau_name}
term_assignment = {
    name: int(interpolation_pairs[name][1][2:]) - 1 for name in group_terms
}
basis_times = [
    0
    if label in ["x_0", "x_star", "grad_f(x_star)"]
    else int(label.split("x_")[1].split(")")[0])
    for label in basis_labels
]
S_assignment = {
    i: max(
        0,
        max((basis_times[j] for j, v in enumerate(row) if abs(v) > 1e-5), default=0)
        - 1,
    )
    for i, row in enumerate(E_saved)
}
assert set(term_assignment) == set(group_terms) and set(S_assignment) == set(
    S_piece_terms
)
assert set(term_assignment.values()).issubset(set(range(-1, N)))
assert set(S_assignment.values()).issubset(set(range(N)))
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
        (S_piece_terms[i] for i, target in S_assignment.items() if target == step),
        pf.Scalar.zero(),
    )
    lyap.append(partial_sum)
ranks = []
singular_values = []
for k, Vk in enumerate(lyap):
    sv = np.linalg.svd(
        np.asarray(pm.eval_scalar(Vk).inner_prod_coords, dtype=float), compute_uv=False
    )
    singular_values.append(sv.tolist())
    ranks.append(int(np.sum(sv > rank_tolerance)))
    print(f"rank V_{k}: {ranks[-1]}")
    if k == 0:
        print()
retained_ranks = ranks[rank_left : N + 1 - rank_right]
print(
    "Interior rank is constant at this N:",
    len(retained_ranks) >= 3 and len(set(retained_ranks)) == 1,
    "boundary exclusions:",
    (rank_left, rank_right),
)
coverage = lyap[N] - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
coverage_value = pm.eval_scalar(coverage)
coverage_residuals = [
    max_abs(coverage_value.inner_prod_coords),
    max_abs(coverage_value.func_coords),
    max_abs(coverage_value.offset),
]
assert max(coverage_residuals) < 1e-5
increment_residuals = []
for k in range(N):
    steps = {-1, 0} if k == 0 else {k}
    increment = sum(
        (
            group_terms[name]
            for name, target in term_assignment.items()
            if target in steps
        ),
        pf.Scalar.zero(),
    )
    increment -= sum(
        (S_piece_terms[i] for i, target in S_assignment.items() if target in steps),
        pf.Scalar.zero(),
    )
    value = pm.eval_scalar(lyap[k + 1] - lyap[k] - increment)
    residual = max(
        max_abs(value.inner_prod_coords),
        max_abs(value.func_coords),
        max_abs(value.offset),
    )
    assert residual < 1e-5
    increment_residuals.append(residual)
# Inspect a fixed margin about the frozen rank threshold; ambiguity triggers recovery.
rank_credible = all(not any(1e-5 <= v <= 1e-3 for v in sv) for sv in singular_values)
assert rank_credible
boundary_names = []
boundary_S = []
grouping_checked = True
print(
    "Full-coordinate coverage residuals:",
    coverage_residuals,
    "maximum increment residual:",
    max(increment_residuals),
)
