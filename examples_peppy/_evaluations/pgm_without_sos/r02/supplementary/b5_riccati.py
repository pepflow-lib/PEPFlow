import sympy as sp

k, t, b, c = sp.symbols("k t b c", real=True)
u, p, q, r = sp.symbols("u p q r", real=True)
v = u - p - q
ak = (k + 1) / t
ap = (k + 2) / (t - 1)
bk = k / t
bp = (k + 1) / (t - 1)
A = (t - k) / (2 * t**2)
Ap = (t - k - 2) / (2 * (t - 1) ** 2)
Vk = A * u * u - u * p / t - b * p * p
Vp = Ap * v * v - v * r / (t - 1) - c * r * r
Q = (
    (ap - ak) * (-r * v + r * r / 2)
    + ak * (r * (u - v) + (p - r) ** 2 / 2)
    + (bp - bk) * (-q * v)
    + bk * q * (u - v)
    - (Vp - Vk)
)
M = sp.Matrix(3, 3, lambda i, j: sp.factor(sp.diff(Q, [p, q, r][i], [p, q, r][j]) / 2))
print("M", M, flush=True)
det = sp.factor(M.det(method="domain-ge"))
print("det", det, flush=True)
rec = sp.factor(sp.solve(det, b)[0])
print("b(c)=", rec, flush=True)
print("b(0)=", sp.factor(rec.subs(c, 0)), flush=True)
# Backwards Möbius transform can be shifted by a particular solution.
for guess in [
    sp.Rational(0),
    k / (2 * t),
    k / (2 * t * t),
    (k + 1) / (2 * t),
    k * (t - k) / (4 * t * t),
]:
    dif = sp.factor(
        guess - rec.subs(c, guess.subs({k: k + 1, t: t - 1}, simultaneous=True))
    )
    print("guess", guess, "diff", dif, flush=True)
