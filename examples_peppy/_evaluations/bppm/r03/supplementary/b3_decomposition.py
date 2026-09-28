# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

D = np.asarray(certificate["numerical_decomposition"]["D"], dtype=float)
E = np.asarray(certificate["numerical_decomposition"]["ell_coords"], dtype=float)
assert certificate["numerical_decomposition"]["basis_labels"] == basis_labels
assert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
# One complete PSD block retains every tiny eigencomponent as a boundary remainder.
S_piece_terms = {"S_full": S_scalar}
assert np.linalg.eigvalsh((S_array + S_array.T) / 2).min() >= -1e-6
