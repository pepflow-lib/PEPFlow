# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

boundary_names = [name for name, step in term_assignment.items() if step == "boundary"]
boundary_S = [name for name, step in S_assignment.items() if step == "boundary"]
if (
    sum(name in interpolation_terms for name in boundary_names) > 1
    or len(boundary_S) > 1
):
    raise ValueError("Revisit the permitted terminal interpolation/S leftovers")
omitted = sum(
    (group_terms[name] for name, step in term_assignment.items() if step == "omitted"),
    pf.Scalar.zero(),
)
leftover = sum((group_terms[name] for name in boundary_names), pf.Scalar.zero())
leftover -= sum((S_piece_terms[name] for name in boundary_S), pf.Scalar.zero())
coverage_diff = (
    lyap[N_int]
    + leftover
    + omitted
    - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
)
piece_diff = sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar
for label, expression in (
    ("coverage", coverage_diff),
    ("S pieces", piece_diff),
    ("omitted", omitted),
):
    value = pm.eval_scalar(expression)
    for coords in (
        value.inner_prod_coords,
        value.func_coords,
        np.asarray(value.offset),
    ):
        if not np.allclose(
            np.asarray(coords, dtype=float),
            0,
            atol=tol["identity_atol"],
            rtol=tol["identity_rtol"],
        ):
            raise ValueError(f"Full-coordinate {label} check failed")
# Every subtracted S piece must have the nonnegative numerical sign used here.
for name, piece in S_piece_terms.items():
    value = pm.eval_scalar(piece)
    matrix = np.asarray(value.inner_prod_coords, dtype=float)
    if not np.allclose(
        value.func_coords, 0, atol=tol["identity_atol"], rtol=0
    ) or not np.allclose(value.offset, 0, atol=tol["identity_atol"], rtol=0):
        raise ValueError(f"S piece has unexpected function/offset terms: {name}")
    if (
        matrix.size
        and np.linalg.eigvalsh((matrix + matrix.T) / 2).min() < -tol["psd_tol"]
    ):
        raise ValueError(f"S piece has the wrong numerical sign: {name}")
# Step identities follow the chosen assignments; check them, including the initial terms.
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
    for coords in (
        value.inner_prod_coords,
        value.func_coords,
        np.asarray(value.offset),
    ):
        if not np.allclose(
            np.asarray(coords, dtype=float),
            0,
            atol=tol["identity_atol"],
            rtol=tol["identity_rtol"],
        ):
            raise ValueError(f"Partial-sum increment identity failed at k={k}")
grouping_checked = True
M_final = pm.eval_scalar(lyap[N_int]).inner_prod_coords.astype(float)
rank_final = int(np.linalg.matrix_rank(M_final, tol=rank_tolerance))
print(f"lyap[{N_int}] rank:", rank_final)
print("Coverage checked with all scalar components and explicit boundary leftovers.")
