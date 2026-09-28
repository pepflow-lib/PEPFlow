# Executed by the OGM notebook in a shared namespace with the required globals.
# Not a standalone script; validate it through notebook execution.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Recurrence-based basis template; no fitted coefficients or solver access."""


def b4_theta_values(n):
    values = [sp.Integer(1)]
    for i in range(n):
        factor = 8 if i == n - 1 else 4
        values.append(((1 + sp.sqrt(1 + factor * values[-1] ** 2)) / 2).evalf(50))
    return values


def b4_function():
    functions = list(ctx.func_to_triplets)
    assert len(functions) == 1 and str(functions[0]) == "f"
    return functions[0]


def initial_gap():
    return ctx["x_0"] - ctx["x_star"]


def current_gap(k):
    return ctx[f"x_{k}"] - ctx["x_star"]


def current_gradient(k):
    assert 0 <= k < N_int
    return b4_function().grad(ctx[f"x_{k}"])


def gradient_step_gap(j):
    return ctx[f"y_{j}"] - ctx["x_star"]


def auxiliary_gap(k):
    theta = b4_theta_values(N_int)
    return theta[k] * ctx[f"x_{k}"] - (theta[k] - 1) * ctx[f"y_{k}"] - ctx["x_star"]


def V_k_basis(k):
    assert N_int >= 4 and 0 <= k <= N_int
    if k == 0:
        return []
    if k == N_int:
        return [initial_gap()]
    if k in (1, N_int - 1):
        return [initial_gap(), current_gradient(k), gradient_step_gap(k + 1)]
    return [
        initial_gap(),
        current_gradient(k),
        auxiliary_gap(k + 1),
        gradient_step_gap(k + 1),
    ]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == N_int:
        return ["r"]
    labels = ["r", f"g_{k}"]
    if 2 <= k <= N_int - 2:
        labels.append(f"q_{k + 1}")
    labels.append(f"h_{k + 1}")
    return labels
