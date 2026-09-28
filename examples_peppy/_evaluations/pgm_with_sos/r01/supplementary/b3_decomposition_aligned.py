# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Align a factor of the saved numerical PSD slack to the supplied square families.
# This changes only the decomposition of the same S, not multipliers or solver data.
F_reference = np.sqrt(np.diag(D))[:, None] * E
s_eigenvalues, s_eigenvectors = np.linalg.eigh((S_saved + S_saved.T) / 2)
assert s_eigenvalues.min() >= -1e-6
S_sqrt = (s_eigenvectors * np.sqrt(np.maximum(s_eigenvalues, 0))) @ s_eigenvectors.T
align_left, _, align_right = np.linalg.svd(F_reference @ S_sqrt, full_matrices=False)
F_aligned = (align_left @ align_right) @ S_sqrt
assert np.allclose(F_aligned.T @ F_aligned, S_saved, atol=1e-5, rtol=0)
S_piece_terms = {}
for row, (j, family, _, _) in zip(F_aligned, pieces):
    vector = sum((float(coef) * v for coef, v in zip(row, basis)), pf.Vector.zero())
    S_piece_terms[f"{j}:{family}"] = vector**2
S_assignment = {name: int(name.split(":")[0]) - 1 for name in S_piece_terms}
piece_diff = pm.eval_scalar(sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar)
assert all(
    maxabs(v) <= 1e-5
    for v in (piece_diff.inner_prod_coords, piece_diff.func_coords, piece_diff.offset)
)
for piece in S_piece_terms.values():
    coords = pm.eval_scalar(piece)
    assert maxabs(coords.func_coords) <= 1e-5 and maxabs(coords.offset) <= 1e-5
    matrix = np.asarray(coords.inner_prod_coords, dtype=float)
    assert np.linalg.eigvalsh((matrix + matrix.T) / 2).min() >= -1e-6
