# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

D = np.asarray(certificate["numerical_decomposition"]["D"], dtype=float)
E = np.asarray(certificate["numerical_decomposition"]["ell_coords"], dtype=float)
assert D.shape == (1, 1)
assert D[0, 0] >= 0
ell = [sum((float(coef) * v for coef, v in zip(E[0], basis)), pf.Vector.zero())]
S_piece_terms = {"terminal_square": float(D[0, 0]) * ell[0] ** 2}
value = pm.eval_scalar(S_piece_terms["terminal_square"] - S_scalar)
for coords in (value.inner_prod_coords, value.func_coords, np.asarray(value.offset)):
    assert np.allclose(
        np.asarray(coords, dtype=float), 0, atol=tol["identity_atol"], rtol=0
    )
