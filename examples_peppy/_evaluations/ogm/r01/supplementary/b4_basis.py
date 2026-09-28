# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def V_k_basis(k):
    if k == 0:
        return []
    anchor = ctx["x_0"] - ctx["x_star"]
    if k == N_int:
        return [
            anchor,
            ctx[f"z_{N_int}"]
            - ctx["x_star"]
            - theta_sequence(N_int)[-1] * ctx[f"g_{N_int}"],
        ]
    return [anchor, ctx[f"g_{k}"], ctx[f"z_{k + 1}"] - ctx["x_star"]]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == N_int:
        return ["x_0-x_star", "z_N-x_star-theta_N*g_N"]
    return ["x_0-x_star", f"g_{k}", f"z_{k + 1}-x_star"]
