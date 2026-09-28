# Notebook code fragment; required globals are supplied by its caller.
# Retained for notebook execution or serialized proof/state source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Canonical prefixes, numerical ranks, full scalar coverage and sign checks."""

grouping_checked = False
assert certificate_checked and not extra_terms
points = [f"x_{i}" for i in range(N_int)] + [f"y_{N_int}"]
group_terms = dict(interpolation_terms)
term_assignment = {f"f:x_star,{points[0]}": -1}
for step in range(N_int):
    term_assignment[f"f:x_star,{points[step + 1]}"] = step
    term_assignment[f"f:{points[step]},{points[step + 1]}"] = step
assert set(term_assignment) == set(group_terms)
assert set(weighted_terms) == set(group_terms) | {tau_name}
# Coordinate pivots and g_0 enter the initial boundary; g_j enters step j-1.
S_assignment = {name: max(-1, pivot - 3) for name, pivot in S_piece_pivots.items()}
assert set(S_assignment) == set(S_piece_terms)
assert all(-1 <= step < N_int for step in S_assignment.values())

rank_tolerance = 1e-6
rank_left = rank_right = 2
rank_convention = {
    "absolute_tolerance": rank_tolerance,
    "stability_interval": [1e-7, 1e-5],
    "scaling": "none; raw Gram coefficient matrices at L=R=1",
    "coordinate_order": "x_0,x_star,grad_f(x_0),...,grad_f(x_(N-1)),grad_f(y_N)",
}
assert params_sp == {"L": sp.S(1), "R": sp.S(1)}
recipe_id = "star_chain_prefix_all_reverse_ldl_pivots_v1"
lyap = [pf.Scalar.zero()]
partial_sum = sum(
    (group_terms[name] for name, step in term_assignment.items() if step == -1),
    pf.Scalar.zero(),
)
partial_sum -= sum(
    (S_piece_terms[name] for name, step in S_assignment.items() if step == -1),
    pf.Scalar.zero(),
)
for k in range(N_int):
    partial_sum += sum(
        (group_terms[name] for name, step in term_assignment.items() if step == k),
        pf.Scalar.zero(),
    )
    partial_sum -= sum(
        (S_piece_terms[name] for name, step in S_assignment.items() if step == k),
        pf.Scalar.zero(),
    )
    lyap.append(partial_sum)

ranks = []
singular_spectra = []
for k, Vk in enumerate(lyap):
    matrix = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, dtype=float)
    singular = np.linalg.svd(matrix, compute_uv=False)
    rank = int(np.count_nonzero(singular > rank_tolerance))
    ranks.append(rank)
    singular_spectra.append(singular.tolist())
    print(f"rank V_{k}: {rank}")
    if k == 0:
        print()
retained_ranks = ranks[rank_left : N_int + 1 - rank_right]
print(
    "Interior rank is constant at this N:",
    len(retained_ranks) >= 3 and len(set(retained_ranks)) == 1,
    "boundary exclusions:",
    (rank_left, rank_right),
)
rank_credible = all(
    int(np.count_nonzero(np.asarray(s) > 1e-7))
    == r
    == int(np.count_nonzero(np.asarray(s) > 1e-5))
    for r, s in zip(ranks, singular_spectra)
)
assert rank_credible, "Inspect the spectrum before accepting numerical rank"

boundary_names = []
boundary_S = []
omitted_names = []
coverage_diff = lyap[N_int] - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
piece_diff = sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar
coverage_residuals = {}
for label, expression in (("coverage", coverage_diff), ("S pieces", piece_diff)):
    value = pm.eval_scalar(expression)
    residuals = {}
    for kind, coords in (
        ("Gram", value.inner_prod_coords),
        ("function", value.func_coords),
        ("offset", value.offset),
    ):
        arr = np.asarray(coords, dtype=float)
        residuals[kind] = float(np.max(np.abs(arr), initial=0.0))
        assert np.allclose(arr, 0, atol=tol["identity_atol"], rtol=tol["identity_rtol"])
    coverage_residuals[label] = residuals

# Each weighted residual is <=0; subtracting each PSD piece preserves this sign.
for name in group_terms:
    assert saved_meta[name]["kind"] == "scalar"
    assert constraints_by_name[name].cmp.name == "LE"
    assert float(saved_duals[name]) >= 0
piece_min_eigenvalues = {}
for name, piece in S_piece_terms.items():
    value = pm.eval_scalar(piece)
    assert np.allclose(value.func_coords, 0, atol=tol["identity_atol"], rtol=0)
    assert np.allclose(value.offset, 0, atol=tol["identity_atol"], rtol=0)
    matrix = np.asarray(value.inner_prod_coords, dtype=float)
    minimum = float(np.linalg.eigvalsh((matrix + matrix.T) / 2).min())
    assert minimum >= -tol["psd_tol"]
    piece_min_eigenvalues[name] = minimum
increment_residuals = []
for k in range(N_int):
    assigned_steps = {-1, 0} if k == 0 else {k}
    increment = sum(
        (
            group_terms[name]
            for name, step in term_assignment.items()
            if step in assigned_steps
        ),
        pf.Scalar.zero(),
    )
    increment -= sum(
        (
            S_piece_terms[name]
            for name, step in S_assignment.items()
            if step in assigned_steps
        ),
        pf.Scalar.zero(),
    )
    value = pm.eval_scalar(lyap[k + 1] - lyap[k] - increment)
    row = [
        float(np.max(np.abs(np.asarray(c, dtype=float)), initial=0.0))
        for c in (value.inner_prod_coords, value.func_coords, value.offset)
    ]
    assert max(row) <= tol["identity_atol"]
    increment_residuals.append(row)
terminal_identity = pm.eval_scalar(
    pb.performance_metric
    - float(certificate["opt_value"])
    - weighted_terms[tau_name]
    - lyap[N_int]
)
terminal_residuals = [
    float(np.max(np.abs(np.asarray(c, dtype=float)), initial=0.0))
    for c in (
        terminal_identity.inner_prod_coords,
        terminal_identity.func_coords,
        terminal_identity.offset,
    )
]
assert max(terminal_residuals) <= tol["identity_atol"]
grouping_checked = True
print("Coverage: all interpolation terms and all S pieces; no leftovers.")
print("Full-coordinate coverage residuals:", coverage_residuals["coverage"])
print("Terminal identity residuals (Gram, function, offset):", terminal_residuals)
