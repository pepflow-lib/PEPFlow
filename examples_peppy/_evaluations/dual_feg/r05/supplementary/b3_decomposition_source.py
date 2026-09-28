# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

S_piece_terms = {"whole_S": S_scalar}
S_assignment = {"whole_S": "boundary"}
S_check = pm.eval_scalar(S_scalar)
assert np.max(np.abs(S_check.func_coords), initial=0) == 0
assert S_check.offset == 0
assert (
    np.linalg.eigvalsh(np.asarray(S_check.inner_prod_coords, dtype=float)).min()
    >= -1e-6
)
