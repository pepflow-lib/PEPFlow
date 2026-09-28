# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Retain the complete numerical S as one PSD boundary piece."""

D = np.asarray(certificate["numerical_decomposition"]["D"], dtype=float)
E = np.asarray(certificate["numerical_decomposition"]["ell_coords"], dtype=float)
assert certificate["numerical_decomposition"]["basis_labels"] == [str(v) for v in basis]
assert np.all(np.diag(D) >= -1e-6)
assert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
S_piece_terms = {"full_S": S_scalar}
S_assignment = {"full_S": "boundary"}
assert np.linalg.eigvalsh((S_array + S_array.T) / 2).min() >= -1e-6
