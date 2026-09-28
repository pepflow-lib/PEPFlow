# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def V_k_basis(k):
    if k == 0:
        return []
    d0 = ctx_b2["x_0"] - ctx_b2["x_star"]
    if k == N:
        return [d0]
    astar = f.grad(ctx_b2["x_star"])
    return [
        astar,
        d0,
        ctx_b2[f"x_{k}"] - ctx_b2["x_star"],
        f.grad(ctx_b2[f"x_{k}"]) - astar,
    ]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == N:
        return ["x_0-x_star"]
    return ["a_star", "x_0-x_star", f"x_{k}-x_star", f"a_{k}-a_star"]
