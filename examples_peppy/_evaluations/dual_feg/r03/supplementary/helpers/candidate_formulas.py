"""Candidate full-PEP formulas inferred during this attempt's Block 2."""
import sympy as sp


def candidate_multipliers(n, lipschitz=sp.S.One):
    result = {"initial_condition": 4 * lipschitz**2 / sp.Integer(n)**2,
              f"A monotone:x_{n},x_star": 4 * lipschitz / n,
              f"A Lipschitz:x_{n-1},x_{n}": sp.S(2)}
    for k in range(n - 1):
        remaining = sp.Integer(n - k)
        result[f"A monotone:x_{n},x_half_{k}"] = 4 * lipschitz / (remaining * (remaining - 1))
        result[f"A Lipschitz:x_{k},x_half_{k}"] = 2 / remaining**2
    return result


def candidate_square(ctx, n, lipschitz=sp.S.One):
    return (2 * lipschitz / n * (ctx["x_0"] - ctx["x_star"]) - ctx[f"g_{n}"])**2
