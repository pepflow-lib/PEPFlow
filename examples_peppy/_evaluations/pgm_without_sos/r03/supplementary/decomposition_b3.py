# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

# B2 spectral terminal assignment failed rank constancy; reverse LDL is an alternative of the same S.
D, ell = ldl_decompose_with_reversed_basis(S_sol, basis, print_output=False)
E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
assert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
S_piece_terms = {}
a = 0
while a < len(D):
    block = [a]
    if a + 1 < len(D) and (D[a, a + 1] != 0 or D[a + 1, a] != 0):
        block.append(a + 1)
    outside = [j for j in range(len(D)) if j not in block]
    assert not np.any(D[np.ix_(block, outside)] != 0)
    S_piece_terms[str(a)] = sum(
        (float(D[i, j]) * ell[i] * ell[j] for i in block for j in block),
        pf.Scalar.zero(),
    )
    a += len(block)
