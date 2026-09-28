"""Exact candidate formulas derived from this attempt's sparse certificate."""
import pepflow as pf
import sympy as sp


def aid_pieces(ctx, f, g, L, N):
    n = sp.S(N)
    pieces = []
    for j in range(1, int(N) + 1):
        i = sp.S(j)
        xp, x, xs = ctx[f"x_{j-1}"], ctx[f"x_{j}"], ctx["x_star"]
        ap, a, astar, s = f.grad(xp), f.grad(x), f.grad(xs), g.grad(x)
        c1 = n / ((2*n+1-i)*(2*n-i)) / L
        u1 = i/(2*n)*a + (2*n-i)/(2*n)*ap - astar
        c2 = ((i-1)/(2*n-i)*(2*n+2)/(2*n+1) + 2*n/((2*n-i)**2*(2*n+1))) / (2*L)
        u2 = ap+s-L/(2*n+1-i)*(xp-xs)
        c3 = i/(2*n+1-i)*(2*n)/(2*n+1)/(2*L)
        u3 = (2*n+1)/(2*n)*(a+s)-(ap+s)/(2*n)-L/(2*n-i)*(x-xs)
        pieces.extend([(j, 'u1', c1, u1), (j, 'u2', c2, u2), (j, 'u3', c3, u3)])
    return pieces


def multiplier_candidate(name, N):
    n = sp.S(N)
    if name == 'initial_condition':
        return sp.Rational(1, 4)/n
    owner, pair = name.split(':')
    row, col = pair.split(',')
    if col == 'x_star':
        return sp.S.Zero
    j = sp.S(int(col[2:]))
    if row == 'x_star':
        if owner == 'f':
            if j == 0:
                return 1/(2*n)
            if j == n:
                return 1/(n+1)
            return (2*n+1)/((2*n-j)*(2*n+1-j))
        if j == n:
            return 2/(n+1)
        return 2*n/((2*n-j)*(2*n+1-j))
    i = sp.S(int(row[2:]))
    if j != i+1:
        return sp.S.Zero
    return (i+1)/(2*n-i) if owner == 'f' else i/(2*n-i)


def square_sum(pieces):
    return sum((c*u**2 for _, _, c, u in pieces), pf.Scalar.zero())
