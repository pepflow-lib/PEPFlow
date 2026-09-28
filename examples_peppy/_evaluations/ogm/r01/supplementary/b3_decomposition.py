# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

D = np.asarray(certificate["numerical_decomposition"]["D"], dtype=float)
E = np.asarray(certificate["numerical_decomposition"]["ell_coords"], dtype=float)
assert (
    certificate["numerical_decomposition"]["basis_labels"]
    == certificate["basis_vectors"]
)
ell = [
    sum((float(coef) * v for coef, v in zip(row, basis)), pf.Vector.zero()) for row in E
]
assert D.shape == (1, 1) and float(D[0, 0]) > 0
S_piece_terms = {"terminal_square": float(D[0, 0]) * ell[0] ** 2}
assert max(coords_max(sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar)) < 1e-5
for piece in S_piece_terms.values():
    value = pm.eval_scalar(piece)
    assert (
        np.min(np.linalg.eigvalsh(np.asarray(value.inner_prod_coords, dtype=float)))
        > -1e-6
    )
    assert np.max(np.abs(np.asarray(value.func_coords, dtype=float)), initial=0) < 1e-5
    assert abs(float(value.offset)) < 1e-5
