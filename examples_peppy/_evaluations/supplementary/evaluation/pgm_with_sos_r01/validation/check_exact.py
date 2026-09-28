"""Independent polynomial audit of the submitted local identities; no proof repair."""

import json
from pathlib import Path

import sympy as t

n, i = t.symbols("N i", integer=True, positive=True)
L = t.symbols("L", positive=True)
p, x, ap, a, ast, d0 = t.symbols("dprev dcurrent aprev acurrent astar d0")
Fp, F, Fs, Gp, G, Gs = t.symbols("fprev fcurrent fstar gprev gcurrent gstar")
s = L * (p - x) - ap


def V(k, y, ay, fy, gy):
    D = 2 * n - k
    return (
        (k + 1) / D * (fy - Fs)
        + k / D * (gy - Gs)
        - ay * y / D
        + (ay - ast) ** 2 / (2 * L * D)
        + L * (n - k) / D**2 * y**2
        - L * d0**2 / (4 * n)
    )


If_star = F - Fs - a * x + (a - ast) ** 2 / (2 * L)
If_prev = F - Fp + a * (p - x) + (ap - a) ** 2 / (2 * L)
Ig_star = G - Gs - s * x
Ig_prev = G - Gp + s * (p - x)
If_initial = Fp - Fs - ap * p + (ap - ast) ** 2 / (2 * L)
c1 = n / ((2 * n + 1 - i) * (2 * n - i) * L)
u1 = i / (2 * n) * a + (2 * n - i) / (2 * n) * ap - ast
c2 = (
    (i - 1) / (2 * n - i) * (2 * n + 2) / (2 * n + 1)
    + 2 * n / ((2 * n - i) ** 2 * (2 * n + 1))
) / (2 * L)
u2 = ap + s - L * p / (2 * n + 1 - i)
c3 = i / (2 * n + 1 - i) * (2 * n) / (2 * n + 1) / (2 * L)
u3 = (2 * n + 1) / (2 * n) * (a + s) - (ap + s) / (2 * n) - L * x / (2 * n - i)
Q = c1 * u1**2 + c2 * u2**2 + c3 * u3**2


def rhs(terminal=False):
    alpha = 1 / (n + 1) if terminal else (2 * n + 1) / ((2 * n - i) * (2 * n + 1 - i))
    beta = 2 / (n + 1) if terminal else 2 * n / ((2 * n - i) * (2 * n + 1 - i))
    return (
        alpha * If_star
        + i / (2 * n + 1 - i) * If_prev
        + beta * Ig_star
        + (i - 1) / (2 * n + 1 - i) * Ig_prev
        - Q
    )


terminal = F - Fs + G - Gs - L * d0**2 / (4 * n)
exprs = {
    "interior": V(i, x, a, F, G) - V(i - 1, p, ap, Fp, Gp) - rhs(),
    "base": (V(1, x, a, F, G) - rhs().subs(i, 1) - If_initial / (2 * n)).subs(d0, p),
    "terminal": terminal - V(n - 1, p, ap, Fp, Gp) - rhs(True).subs(i, n),
    "N1": (terminal - rhs(True).subs(i, n) - If_initial / (2 * n))
    .subs(n, 1)
    .subs(d0, p),
}
results = {}
for name, expression in exprs.items():
    poly = t.Poly(
        t.expand(expression), p, x, ap, a, ast, d0, Fp, F, Fs, Gp, G, Gs, domain="EX"
    )
    residuals = [t.factor(c) for c in poly.coeffs()]
    assert all(c == 0 for c in residuals), (name, residuals)
    results[name] = {"all_polynomial_coefficients_exactly_zero": True, "residual": 0}
results["method"] = (
    "Each Gram monomial and independent function-value coefficient checked as a rational function of symbolic N,i,L. Since the submitted expressions are sums of Euclidean inner products, this one-coordinate polynomial identity extends by summing over arbitrary finite dimension."
)
Path("exact-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
