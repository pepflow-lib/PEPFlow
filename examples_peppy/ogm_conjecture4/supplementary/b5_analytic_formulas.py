# Notebook code fragment; required globals are supplied by its caller.
# Retained for notebook execution or serialized proof/state source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

"""Explicit analytic alternative; the saved numerical certificate is unchanged."""


def b5_weights(s, horizon_q):
    total = 2 * horizon_q + 1
    return s * (2 * horizon_q - s) / (horizon_q * (total - s))


def b5_global_multipliers(n, smoothness, theta_values):
    """Exact sparse weights; p_i=x_i for i<n and p_n=y_n."""
    assert n >= 1
    horizon_q = theta_values[n - 1] ** 2
    chain = [b5_weights(theta_values[i] ** 2, horizon_q) for i in range(n)]
    star = [chain[0]] + [chain[i] - chain[i - 1] for i in range(1, n)] + [1 - chain[-1]]
    return {
        "initial": smoothness / (2 * (2 * horizon_q + 1)),
        "star": star,
        "forward_chain": chain,
        "all_other_interpolation_weights": 0,
    }


def b5_coefficients(s, horizon_q):
    denominator = 2 * horizon_q + 1 - s
    aa = (2 * horizon_q - s) / (4 * horizon_q * denominator)
    bb = -s / (4 * horizon_q * denominator**2)
    cc = s * (6 * horizon_q - 4 * s + 3) / (4 * horizon_q * denominator**3)
    return aa, bb, cc


def b5_global_sos(context, n, smoothness, theta_values):
    """The proved finite sum of squares, for any n>=1 and L>0."""
    context.set_as_current()
    owner = next(iter(context.func_to_triplets))
    squared_theta = [value**2 for value in theta_values[:n]]
    horizon_q = squared_theta[-1]
    total = 2 * horizon_q + 1
    weights = [b5_weights(value, horizon_q) for value in squared_theta]
    increments = (
        [weights[0]]
        + [weights[i] - weights[i - 1] for i in range(1, n)]
        + [1 - weights[-1]]
    )
    points = [context[f"x_{i}"] for i in range(n)] + [context[f"y_{n}"]]
    gradients = [owner.grad(point) for point in points]
    r_vector = context["x_0"] - context["x_star"]
    average = sum(
        (increments[i] * gradients[i] for i in range(n + 1)), pf.Vector.zero()
    )
    differences = [
        (gradients[i] - gradients[i + 1]) / (total - squared_theta[i]) for i in range(n)
    ]
    integral = sum(
        (squared_theta[i] ** 2 * differences[i] / 2 for i in range(n)), pf.Vector.zero()
    )
    result = smoothness / (2 * total) * (r_vector - total / smoothness * average) ** 2
    result += integral**2 / (smoothness * horizon_q**2)
    for j in range(n):
        left = squared_theta[j - 1] if j else sp.Integer(0)
        midpoint = (squared_theta[j] + left) / 2
        slope = sum(differences[j:], pf.Vector.zero())
        center = (
            sum(
                ((squared_theta[i] - midpoint) * differences[i] for i in range(j, n)),
                pf.Vector.zero(),
            )
            - integral / horizon_q
        )
        result += 3 * theta_values[j] / (smoothness * horizon_q) * center**2
        result += theta_values[j] ** 3 / (4 * smoothness * horizon_q) * slope**2
    return result


def b5_local_potential(context, n, k, smoothness, theta_values):
    context.set_as_current()
    owner = next(iter(context.func_to_triplets))
    horizon_q = theta_values[n - 1] ** 2
    tau_value = smoothness / (2 * (2 * horizon_q + 1))
    r_vector = context["x_0"] - context["x_star"]
    if k == -1:
        return pf.Scalar.zero()
    if k == n:
        return (
            owner(context[f"y_{n}"])
            - owner(context["x_star"])
            - tau_value * r_vector**2
        )
    assert 0 <= k < n
    s_value = theta_values[k] ** 2
    weight = b5_weights(s_value, horizon_q)
    aa, bb, cc = b5_coefficients(s_value, horizon_q)
    gradient = owner.grad(context[f"x_{k}"])
    auxiliary = (
        theta_values[k + 1] * context[f"x_{k + 1}"]
        - (theta_values[k + 1] - 1) * context[f"y_{k + 1}"]
        - context["x_star"]
    )
    step_gap = context[f"y_{k + 1}"] - context["x_star"]
    return (
        weight * (owner(context[f"x_{k}"]) - owner(context["x_star"]))
        - tau_value * r_vector**2
        - weight / (2 * smoothness) * gradient**2
        + smoothness
        * (aa * auxiliary**2 + 2 * bb * (auxiliary * step_gap) + cc * step_gap**2)
    )
