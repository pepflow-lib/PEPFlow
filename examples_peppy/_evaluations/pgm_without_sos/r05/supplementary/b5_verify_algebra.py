import sympy as sp

k, N, W = sp.symbols("k N W", real=True)
u, p, q, r, s, d = sp.symbols("u p q r s d", real=True)
F, G, H, J = sp.symbols("F G H J", real=True)


def coeff(k, z):
    m = 2 * N - k
    return (
        (k + 1) / m,
        k / m,
        (N - k - 1 + (k + 1) / (2 * m) - z) / (m - 1) ** 2,
        1 / (2 * m) + z / (m - 1),
        -(k - 1) / (2 * m) - z,
    )


def V(k, z, u, p, q, F, G):
    a, b, A, B, C = coeff(k, z)
    return (
        -d * d / (4 * N)
        + a * F
        + b * G
        - a * p * p / 2
        - b * p * q
        + A * u * u
        + 2 * B * u * q
        + C * q * q
    )


def squares(k, W, u, q, r, s):
    m = 2 * N - k
    HH = 2 * (m - 1) ** 2 * W + (k + 1) * (m - 2)
    JJ = 2 * (m - 1) * ((2 * k + 3) * m - (3 * k + 4)) * W + (m - 2) * (k + 1) * (k + 2)
    alpha = HH / (2 * (m - 2) ** 2)
    beta = JJ / (2 * (m - 1) * HH)
    gamma = (2 * (m - 1) * W + (k + 1) * (m - 2)) / HH
    delta = (k + 1) / (2 * m * beta)
    Z = (k + 1) / (2 * m) - (k + 1) ** 2 / (4 * m * m * beta)
    return Z, alpha * (s - u / (m - 1) + gamma * r) ** 2 + beta * (
        r + delta * (q - u / (m - 1))
    ) ** 2


Z, Q = squares(k, W, u, q, r, s)
a, b, *_ = coeff(k, Z)
an, bn, *_ = coeff(k + 1, W)
If = H - F + r * (p + q) + (r - p) ** 2 / 2
Ifs = H - r * u + r * r / 2
Ig = J - G + q * (p + q)
Igs = J - q * u
T = a * If + (an - a) * Ifs + b * Ig + (bn - b) * Igs
assert (
    sp.factor(T - Q - (V(k + 1, W, u - r - s, r, s, H, J) - V(k, Z, u, p, q, F, G)))
    == 0
)
print("Step square formula exact")
z = sp.symbols("z")
a0 = 1 / (2 * N)
Qinit = p * p / (4 * N) + z / (2 * N - 1) ** 2 * (d - p - 2 * N * q) ** 2
base = sp.factor(a0 * (F - p * d + p * p / 2) - V(0, z, d - p - q, p, q, F, G) - Qinit)
print("Base initial residual:", base)
assert base == 0
m = 2 * N - k
AA = 2 * (k + 1) * (m - 1) * ((k + 2) * m * (m - 1) - (k + 1))
BB = (k + 1) ** 2 * (m - 2) * (2 * N + 1)
CC = 4 * m * m * (m - 1) * ((2 * k + 3) * m - (3 * k + 4))
DD = 2 * m * m * (m - 2) * (k + 1) * (k + 2)
assert sp.factor(Z - (AA * W + BB) / (CC * W + DD)) == 0
print("Matrix product recurrence exact")
a, b, *_ = coeff(N - 1, N / (2 * (N + 1) ** 2))
T = a * If + (1 - a) * Ifs + b * Ig + (1 - b) * Igs
Qterm = (r + N * q / (N + 1) - u / (N + 1)) ** 2 / 2
assert (
    sp.factor(
        T
        - Qterm
        - (H + J - d * d / (4 * N) - V(N - 1, N / (2 * (N + 1) ** 2), u, p, q, F, G))
    )
    == 0
)
print("Terminal exact")
