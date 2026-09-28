# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# All interpolation residuals are <= 0; each subtracted S piece is PSD.
# Thus these partial sums use the nonincreasing sign convention.
rank_tolerance = 1e-4
rank_left, rank_right = 1, 1
group_terms = {name: term for name, term in weighted_terms.items() if name != tau_name}
term_assignment = {name: int(name.split(",")[1][2:]) - 1 for name in group_terms}
S_assignment = {}
for name, piece in S_piece_terms.items():
    M = np.asarray(pm.eval_scalar(piece).inner_prod_coords, float)
    row = E[int(name)]
    support = [j for j, v in enumerate(row) if abs(v) > 1e-5]
    pivot_label = basis_labels[max(support)]
    index = (
        int(pivot_label.split("x_")[1].split(")")[0])
        if "x_" in pivot_label and "star" not in pivot_label
        else 0
    )
    S_assignment[name] = min(N_int - 1, max(-1, index - 1))
    assert np.linalg.eigvalsh((M + M.T) / 2).min() >= -1e-6
assert set(term_assignment) == set(group_terms)
assert set(S_assignment) == set(S_piece_terms)
lyap = [pf.Scalar.zero()]
partial_sum = sum(
    (term for name, term in group_terms.items() if term_assignment[name] == -1),
    pf.Scalar.zero(),
)
partial_sum -= sum(
    (piece for name, piece in S_piece_terms.items() if S_assignment[name] == -1),
    pf.Scalar.zero(),
)
for step in range(N_int):
    partial_sum += sum(
        (term for name, term in group_terms.items() if term_assignment[name] == step),
        pf.Scalar.zero(),
    )
    partial_sum -= sum(
        (piece for name, piece in S_piece_terms.items() if S_assignment[name] == step),
        pf.Scalar.zero(),
    )
    lyap.append(partial_sum)
ranks = []
singular_values = []
for k, Vk in enumerate(lyap):
    M = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, float)
    singular_values.append(np.linalg.svd(M, compute_uv=False).tolist())
    ranks.append(int(np.linalg.matrix_rank(M, tol=rank_tolerance)))
    print(f"rank V_{k}: {ranks[-1]}")
    if k == 0:
        print()
retained = ranks[rank_left : N_int + 1 - rank_right]
print(
    "Interior rank is constant at this N:",
    len(retained) >= 3 and len(set(retained)) == 1,
    "boundary exclusions:",
    (rank_left, rank_right),
)
coverage_diff = lyap[N_int] - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
piece_diff = sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar
coverage_residuals = {}
for label, expression in [("coverage", coverage_diff), ("S pieces", piece_diff)]:
    value = pm.eval_scalar(expression)
    coords = [value.inner_prod_coords, value.func_coords, np.asarray(value.offset)]
    coverage_residuals[label] = max(
        float(np.max(np.abs(np.asarray(c, float)), initial=0)) for c in coords
    )
    assert all(np.allclose(np.asarray(c, float), 0, atol=1e-5, rtol=0) for c in coords)
for k in range(N_int):
    assigned = {-1, 0} if k == 0 else {k}
    increment = sum(
        (
            term
            for name, term in group_terms.items()
            if term_assignment[name] in assigned
        ),
        pf.Scalar.zero(),
    )
    increment -= sum(
        (
            piece
            for name, piece in S_piece_terms.items()
            if S_assignment[name] in assigned
        ),
        pf.Scalar.zero(),
    )
    value = pm.eval_scalar(lyap[k + 1] - lyap[k] - increment)
    assert all(
        np.allclose(np.asarray(c, float), 0, atol=1e-5, rtol=0)
        for c in [value.inner_prod_coords, value.func_coords, np.asarray(value.offset)]
    )
boundary_names = []
boundary_S = []
grouping_checked = True
print("Full-coordinate coverage and step identities:", coverage_residuals)
