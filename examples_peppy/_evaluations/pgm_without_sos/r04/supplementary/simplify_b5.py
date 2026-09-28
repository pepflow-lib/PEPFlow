import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import runtime
import sympy as s

k, N, C, t, z = s.symbols("k N C t z")
# SymPy accepts locals at runtime; its installed overloads omit this keyword.
formula = s.sympify(  # ty: ignore[no-matching-overload]
    (runtime.ATTEMPT / "supplementary/b5-recurrence.txt").read_text(),
    locals={"k": k, "N": N, "C": C},
)
r = s.factor(formula.subs(N, (t + k) / 2))
print("r=", r)
for factor in [-1, 1]:
    for shift in [0, 1]:
        v = factor * (k + shift) / (2 * t)
        vn = v.subs({k: k + 1, t: t - 1}, simultaneous=True)
        print("candidate", v, "defect", s.factor(r.subs(C, vn) - v))
# Scale beta to isolate the rational Riccati recurrence.
print(
    "scaled",
    s.factor(
        2
        * t
        * t
        / (k * (k + 1))
        * r.subs(C, z * (k + 1) * (k + 2) / (2 * (t - 1) ** 2))
    ),
)
