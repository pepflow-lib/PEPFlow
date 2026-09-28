"""Common exact PEPFlow constructors for the analytic alternative potential."""

import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import sympy as sp

import pepflow as pf


def b5_parameters():
    L, q, t, R = [pf.Parameter(name) for name in ("L", "q", "t", "R")]
    symbols = dict(zip(("L", "q", "t", "R"), sp.symbols("L q t R", positive=True)))
    symbols["R"] = sp.Symbol("R", nonnegative=True)
    return L, q, t, R, symbols


def b5_weight(s, q):
    return s * (2 * q - s) / (q * (2 * q + 1 - s))


def b5_coefficients(s, q):
    h = 2 * q + 1 - s
    return (
        (2 * q - s) / (4 * q * h),
        -s / (4 * q * h**2),
        s * (6 * q - 4 * s + 3) / (4 * q * h**3),
    )


def b5_quadratic(s, Q, H, q):
    A, B, C = b5_coefficients(s, q)
    return A * (Q**2) + 2 * B * (Q * H) + C * (H**2)


def b5_potential(s, x, g, Q, H, r, f, xs, L, q):
    b = b5_weight(s, q)
    return (
        b * (f(x) - f(xs))
        - L / (2 * (2 * q + 1)) * (r**2)
        - b / (2 * L) * (g**2)
        + L * b5_quadratic(s, Q, H, q)
    )


def b5_star(x, g, f, xs, L):
    return f(x) - f(xs) - g * (x - xs) + (g**2) / (2 * L)


def b5_chain(x, gx, y, gy, f, L):
    return f(y) - f(x) - gy * (y - x) + ((gy - gx) ** 2) / (2 * L)


@lru_cache(None)
def b5_reduce(expression):
    return sp.cancel(expression)


def b5_exact_scalar(label, expression, ctx, parameters):
    manager = pf.ExpressionManager(ctx, resolve_parameters=parameters)
    value = manager.eval_scalar(expression, sympy_mode=True)
    results = {}
    for kind, coords in (
        ("Gram", value.inner_prod_coords),
        ("function", value.func_coords),
        ("offset", value.offset),
    ):
        array = np.asarray(coords, dtype=object)
        reduced = [b5_reduce(sp.sympify(item)) for item in array.flat]
        assert all(item == 0 for item in reduced), (label, kind, reduced)
        assert not any(item.has(sp.Float) for item in array.flat), (
            label,
            kind,
            "floating input",
        )
        results[kind] = {
            "shape": list(array.shape),
            "entries": len(reduced),
            "exact_zero": True,
        }
    return {"label": label, "components": results}


def b5_native_residual(f, ctx, name):
    constraints = f.get_interpolation_constraints(ctx)
    constraint = next(item for item in constraints if item.name == name)
    assert constraint.cmp.name == "LE"
    return constraint.lhs - constraint.rhs


def b5_write_result(path, checks):
    record = {
        "scope": "exact symbolic PEPFlow identities; all Gram/function/offset coordinates",
        "SDP_calls": 0,
        "checks": checks,
    }
    Path(path).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
