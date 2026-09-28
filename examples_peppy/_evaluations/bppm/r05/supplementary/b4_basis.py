# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Use point gaps and kernel gradients as a consistent geometric basis."""


def V_k_basis(k):
    if k == 0:
        return []
    return [
        ctx["x_star"] - ctx["x_0"],
        ctx["x_star"] - ctx[f"x_{k}"],
        h.grad(ctx["x_0"]),
        h.grad(ctx[f"x_{k}"]),
    ]


def V_k_basis_labels(k):
    if k == 0:
        return []
    return ["a_0", f"a_{k}", "q_0", f"q_{k}"]


for k in range(N_int + 1):
    vectors = V_k_basis(k)
    basis_matrix = (
        np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
        if vectors
        else np.zeros((len(ctx.basis_vectors()), 0))
    )
    basis_rank = int(np.linalg.matrix_rank(basis_matrix, tol=1e-7)) if vectors else 0
    assert basis_rank == len(vectors) == ranks[k]
    print(f"k={k}: rank {basis_rank} basis {V_k_basis_labels(k)}")
