# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def V_k_basis(k):
    if k == 0:
        return []
    h_local = next(q for q in ctx.func_to_triplets if str(q) == "h")
    return [
        ctx["x_0"] - ctx["x_star"],
        h_local.grad(ctx["x_0"]),
        ctx[f"x_{k}"] - ctx["x_star"],
        h_local.grad(ctx[f"x_{k}"]),
    ]


def V_k_basis_labels(k):
    if k == 0:
        return []
    return ["x_0-x_star", "grad_h(x_0)", f"x_{k}-x_star", f"grad_h(x_{k})"]
