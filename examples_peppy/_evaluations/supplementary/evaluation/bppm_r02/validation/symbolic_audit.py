"""Independent verification of only the submitted BPPM identities; no proof repair."""

import json
from pathlib import Path

import sympy as s

j, N, a, R = s.symbols("j N alpha R")
x, y, z, o = s.symbols("x y z o")
fx, fy, fz = s.symbols("fx fy fz")
hx, hy, hz, ho = s.symbols("hx hy hz ho")
gx, gy, go, gf = s.symbols("gx gy go gf")


# x is previous, y is next, z is optimum, o is initial.
def D(hu, hv, gv, u, v):
    return hu - hv - gv * (u - v)


D0 = D(hz, ho, go, z, o)
Dx = D(hz, hx, gx, z, x)
Dy = D(hz, hy, gy, z, y)
Vprev = (j - 1) * (fx - fz) / N + (Dx - D0) / (a * N)
Vnext = j * (fy - fz) / N + (Dy - D0) / (a * N)
Cfstar = fy - fz + gf * (z - y)
Cfprev = fy - fx + gf * (x - y)
Chback = hx - hy + gx * (y - x)
Chforward = hy - hx + gy * (x - y)
rhs = (
    Cfstar / N
    + (j - 1) * Cfprev / N
    + j * Chback / (a * N)
    + (j - 1) * Chforward / (a * N)
)
step = s.factor((Vnext - Vprev - rhs).subs(gy, gx - a * gf))
four = ((go - gy) * (z - y) + (y - o) * go + ho - hy) / (a * N) + j * (fy - fz) / N
boundary = s.factor(
    (fy - fz - R / (a * N)) - (Vnext.subs(j, N) + (D0 - R) / (a * N) - Dy / (a * N))
)
results = {
    "step": str(step),
    "four_vector": str(s.factor(four - Vnext)),
    "boundary": str(boundary),
    "base": str(s.factor(Vprev.subs({j: 1, x: o, hx: ho, gx: go}))),
}
assert all(v == "0" for v in results.values())
results["scope"] = (
    "Fresh exact expansion of submitted bilinear identities, with arbitrary symbolic j,N,alpha,R. Scalar-coordinate representation suffices since every inner-product term is bilinear and the cancellation is coordinatewise; no dimension-dependent identity is used. Sign/domain implications inspected in notebook."
)
Path("symbolic-audit.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results))
