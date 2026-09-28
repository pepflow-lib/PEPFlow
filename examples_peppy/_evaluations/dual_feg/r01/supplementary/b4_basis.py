# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def V_k_basis(k):
    if k == 0:
        return []
    if k == N_int:
        return [ctx["x_0"] - ctx[f"x_{N_int}"], ctx[f"g_{N_int}"]]
    return [
        ctx["x_0"] - ctx[f"x_{N_int}"],
        ctx[f"z_{k}"],
        ctx[f"x_{k}"] - ctx[f"x_{N_int}"],
        ctx[f"g_{N_int}"],
    ]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == N_int:
        return ["x_0-x_N", "A(x_N)"]
    return ["x_0-x_N", f"z_{k}", f"x_{k}-x_N", "A(x_N)"]
