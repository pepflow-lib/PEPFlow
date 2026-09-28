# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# Use the complete S as one terminal PSD piece, including all small pivots.
S_piece_terms = {"terminal_S": S_scalar}
S_assignment = {"terminal_S": "boundary"}
D = D_saved
E = E_saved
ell = [
    sum((float(coef) * v for coef, v in zip(row, basis)), pf.Vector.zero()) for row in E
]
assert np.allclose(
    E.T @ D @ E,
    S_array,
    atol=tol["reconstruction_atol"],
    rtol=tol["reconstruction_rtol"],
)
