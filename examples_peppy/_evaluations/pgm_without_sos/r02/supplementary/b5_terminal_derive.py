import sympy as sp

n, L, b = sp.symbols("n L b", positive=True)
u, p, q, r, s = sp.symbols("u p q r s", real=True)
F, Fp, G, Gp = sp.symbols("F Fp G Gp", real=True)
v = u - (p + q) / L
k = n - 1
t = n + 1
Vk = L / t**2 * u * u - u * (p + s) / t - b * p * p / L + n / t * F + (n - 1) / t * G
VN = Fp + Gp
Q = (
    (1 / t) * (Fp - (r + s) * v + r * r / (2 * L))
    + (n / t) * (Fp - F + (r + s) * (u - v) + (p - r) ** 2 / (2 * L))
    + (2 / t) * (Gp - (q - s) * v)
    + ((n - 1) / t) * (Gp - G + (q - s) * (u - v))
    - (VN - Vk)
)
M = sp.Matrix(
    4, 4, lambda i, j: sp.factor(sp.diff(Q, [u, p, q, r][i], [u, p, q, r][j]) / 2)
)
M = M.subs(b, (n - 1) / (2 * (n + 1) ** 2))
print("terminal matrix", M)
R = M
for i in [3, 2, 1, 0]:
    pivot = sp.factor(R[i, i])
    print("pivot", i, pivot)
    if pivot == 0:
        continue
    row = [sp.factor(R[i, j] / pivot) for j in range(4)]
    print("factor", row)
    R = sp.Matrix(4, 4, lambda a, b: sp.factor(R[a, b] - pivot * row[a] * row[b]))
