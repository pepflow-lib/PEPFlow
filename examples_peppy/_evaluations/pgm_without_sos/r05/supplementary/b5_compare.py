# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from owned_runtime import ROOT, configure  # ty: ignore[unresolved-import]

configure()
exec((ROOT / "supplementary/replay_b4.py").read_text(encoding="utf-8-sig"))


def z_product(k, N):
    P, Q = sp.Integer(N), sp.Integer(2 * (N + 1) ** 2)
    for j in reversed(range(k, N - 1)):
        m = 2 * N - j
        A = 2 * (j + 1) * (m - 1) * ((j + 2) * m * (m - 1) - (j + 1))
        B = (j + 1) ** 2 * (m - 2) * (2 * N + 1)
        C = 4 * m * m * (m - 1) * ((2 * j + 3) * m - (3 * j + 4))
        D = 2 * m * m * (m - 2) * (j + 1) * (j + 2)
        P, Q = A * P + B * Q, C * P + D * Q
    return P / Q


def normalized_U(k, z, x, xnext, anchor, xs, fs, gs, L, N):
    m = 2 * N - k
    a = (k + 1) / m
    b = k / m
    A = (N - k - 1 + (k + 1) / (2 * m) - z) / (m - 1) ** 2
    B = 1 / (2 * m) + z / (m - 1)
    C = -(k - 1) / (2 * m) - z
    p = (fs.grad(x) - fs.grad(xs)) / L
    q = (gs.grad(xnext) + fs.grad(xs)) / L
    dn = xnext - xs
    d0 = anchor - xs
    FF = (fs(x) - fs(xs) - fs.grad(xs) * (x - xs)) / L
    GG = (gs(x) - gs(xs) + fs.grad(xs) * (x - xs)) / L
    return (
        -(d0**2) / (4 * N)
        + a * FF
        + b * GG
        - a * p**2 / 2
        - b * p * q
        + A * dn**2
        + 2 * B * dn * q
        + C * q**2
    )


for k in range(1, N_int):
    z = z_product(k, N_int)
    expr = normalized_U(
        sp.Integer(k),
        z,
        ctx[f"x_{k}"],
        ctx[f"x_{k + 1}"],
        ctx["x_0"],
        ctx["x_star"],
        f,
        g,
        sp.Integer(1),
        sp.Integer(N_int),
    )
    ev = pm.eval_scalar(expr - lyap[k])
    errors = [
        float(np.max(np.abs(np.asarray(v, dtype=float)), initial=0))
        for v in (ev.inner_prod_coords, ev.func_coords, ev.offset)
    ]
    print("k,z,errors", k, z, errors)
    assert max(errors) < 1e-4
