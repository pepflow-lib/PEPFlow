# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Reallocated per-step PSD blocks reproduce the same saved S.
# These are finite-sample numerical blocks, distinct from the supplied analytic SOS candidate.
allocation = certificate["reallocated_S_pieces"]
assert allocation["certificate_id"] == certificate["certificate_id"]
assert allocation["N"] == N
S_piece_terms = {}
for j, saved_matrix in enumerate(allocation["Q"], 1):
    matrix = np.asarray(saved_matrix, dtype=float)
    assert matrix.shape == S_saved.shape
    assert np.all(np.isfinite(matrix))
    assert np.allclose(matrix, matrix.T, atol=1e-6, rtol=0)
    assert np.linalg.eigvalsh((matrix + matrix.T) / 2).min() >= -1e-6
    S_piece_terms[f"{j}:block"] = sum(
        (
            float(matrix[i, col_idx]) * basis[i] * basis[col_idx]
            for i, col_idx in np.ndindex(matrix.shape)
        ),
        pf.Scalar.zero(),
    )
S_assignment = {name: int(name.split(":")[0]) - 1 for name in S_piece_terms}
piece_diff = pm.eval_scalar(sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar)
assert all(
    maxabs(v) <= 1e-5
    for v in (piece_diff.inner_prod_coords, piece_diff.func_coords, piece_diff.offset)
)
for piece in S_piece_terms.values():
    ev = pm.eval_scalar(piece)
    assert maxabs(ev.func_coords) <= 1e-5 and maxabs(ev.offset) <= 1e-5
