"""Symbolic coefficient recurrence from the discovered four-vector structure."""

import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path[:0] = [
        str(root / "supplementary/approved"),
        str(root / "supplementary/h"),
        str(root),
    ]
    # local helper resolved by the notebook runtime path
    from runtime import configure  # ty: ignore[unresolved-import]

    configure()
    import sympy as sp

    k, N = sp.symbols("k N", integer=True)
    t, u = sp.symbols("t u")
    d, p, q, s = sp.symbols("d p q s")
    a = lambda j: (j + 1) / (2 * N - j)  # noqa: E731 - retain the archived notebook helper
    b = lambda j: j / (2 * N - j)  # noqa: E731 - retain the archived notebook helper
    A = lambda j: (N - j) / (2 * N - j) ** 2  # noqa: E731 - retain the archived notebook helper
    c = lambda j: 1 / (2 * N - j)  # noqa: E731 - retain the archived notebook helper
    dn = d - p - s
    Ifstar = -q * dn + q * q / 2
    Igstar = -s * dn
    Ifstep = q * (d - dn) + (p - q) ** 2 / 2
    Igstep = s * (d - dn)
    V = A(k) * d * d - c(k) * d * p - t * p * p
    W = A(k + 1) * dn * dn - c(k + 1) * dn * q - u * q * q
    S = sp.expand(
        (a(k + 1) - a(k)) * Ifstar
        + (b(k + 1) - b(k)) * Igstar
        + a(k) * Ifstep
        + b(k) * Igstep
        - W
        + V
    )
    vec = sp.Matrix([q, s, d, p])
    M = sp.hessian(S, vec) / 2
    M = M.applyfunc(sp.factor)
    print("S matrix", M)
    rem = M.copy()
    pivots = []
    factors = []
    for j in range(2):
        pivot = sp.factor(rem[j, j])
        row = (rem[:, j] / pivot).applyfunc(sp.factor)
        pivots.append(pivot)
        factors.append(row)
        rem = (rem - pivot * row * row.T).applyfunc(sp.factor)
    print("pivots", pivots)
    print("factors", factors)
    print("remainder", rem)
    recurrence = sp.solve(rem[3, 3], t)[0]
    print("t recurrence:", sp.factor(recurrence))
    m, r = sp.symbols("m r")
    scaled = sp.factor((2 * (2 * N - k) ** 2 / k) * recurrence)
    scaled = sp.factor(
        scaled.subs(N, (m + k) / 2).subs(u, (k + 1) * r / (2 * (m - 1) ** 2))
    )
    print("scaled recurrence r_k:", scaled)
    chosen = {
        t: k * (N - k) / (2 * (2 * N - k) ** 2),
        u: (k + 1) * (N - k - 1) / (2 * (2 * N - k - 1) ** 2),
    }
    print("SIMPLE pivots", [sp.factor(v.subs(chosen)) for v in pivots])
    print("SIMPLE factors", [v.subs(chosen).applyfunc(sp.factor) for v in factors])
    print("SIMPLE residual", sp.factor(rem[3, 3].subs(chosen)))
    n = sp.symbols("n", nonnegative=True)
    print(
        "POS form",
        [sp.factor(v.subs(chosen).subs(N, k + 1 + n)) for v in pivots + [rem[3, 3]]],
    )
    small = {t: k / (2 * (2 * N - k) ** 2), u: (k + 1) / (2 * (2 * N - k - 1) ** 2)}
    print(
        "SMALL POS",
        [sp.factor(v.subs(small).subs(N, k + 1 + n)) for v in pivots + [rem[3, 3]]],
    )
    (root / "supplementary/b5-recurrence.txt").write_text(
        "\n".join(
            [str(M), str(pivots), str(factors), str(rem), str(sp.factor(recurrence))]
        )
    )


if __name__ == "__main__":
    main()
