"""Exact local analytic alternative; no SDP, fitting, outside example or web."""

import json
from pathlib import Path

import sympy as sp

q, t, z = sp.symbols("q t z")
T = 2 * q + 1
s = t**2
p = t**2 - t
h = T - s
hp = T - p


def weight(x):
    return x * (2 * q - x) / (q * (T - x))


def coefficient(x):
    hx = T - x
    return sp.Matrix(
        [
            [(2 * q - x) / (4 * q * hx), -x / (4 * q * hx**2)],
            [-x / (4 * q * hx**2), x * (6 * q - 4 * x + 3) / (4 * q * hx**3)],
        ]
    )


def zero_matrix(mat):
    result = [sp.factor(sp.cancel(value)) for value in mat]
    assert all(value == 0 for value in result), result
    return [str(value) for value in result]


# Old state (Q,H)=(q_j,h_j), x_j=(Q+(t-1)H)/t, v=g_j/L.
# New state is (Q-2*t*v,x_j-v).
F = sp.Matrix([[1, 0], [1 / t, (t - 1) / t]])
control = sp.Matrix([2 * t, 1])
M = coefficient(s)
Mp = coefficient(p)
e = sp.simplify(
    2 * F.T * M * control - weight(s) * F[1, :].T + sp.Matrix([0, weight(p)])
)
d = sp.factor(weight(s) - (control.T * M * control)[0])
P = 8 * q * t - 6 * q - 4 * t**3 + 4 * t**2 + 4 * t - 3
d_formula = t**2 * P / (4 * q * h**3)
gamma = 3 * t * (t - 1) / (4 * q * hp * P)
n = sp.Matrix([1, -(T - 2 * p) / hp])
schur = Mp - F.T * M * F - e * e.T / (4 * d)

checks = {}
checks["pivot_formula"] = zero_matrix(sp.Matrix([d - d_formula]))
checks["local_schur_factor"] = zero_matrix(schur - gamma * n * n.T)
D = (Mp - F.T * M * F).row_join(e / 2)
D = D.col_join((e.T / 2).row_join(sp.Matrix([[d]])))
factor = sp.Matrix([e[0] / (2 * d), e[1] / (2 * d), 1])
n3 = sp.Matrix([n[0], n[1], 0])
checks["local_full_matrix_factor"] = zero_matrix(
    D - d * factor * factor.T - gamma * n3 * n3.T
)

# Initial interpolation minus the proposed U_0 expression.
tau = 1 / (2 * T)
K = sp.Matrix([[1, -2], [1, -1]])
initial = (
    sp.Matrix([[tau, -weight(1) / 2], [-weight(1) / 2, weight(1)]])
    - K.T * coefficient(1) * K
)
initial_vector = sp.Matrix([1, -T])
initial_coefficient = 1 / (32 * q**4 * T)
checks["initial_factor"] = zero_matrix(
    initial - initial_coefficient * initial_vector * initial_vector.T
)

# Terminal interpolation minus (f(y_N)-f*)-tau*||r||^2.
terminal = coefficient(q) - sp.Matrix([[0, 0], [0, 1 / (2 * (q + 1) ** 2)]])
terminal_vector = sp.Matrix([1, -1 / (q + 1)])
checks["terminal_factor"] = zero_matrix(
    terminal - terminal_vector * terminal_vector.T / (4 * (q + 1))
)

# Actual transitions satisfy t>1 and q>=t^2; t>=1 suffices for P>0.
P_positive = (
    (8 * t - 6) * (q - t**2) + 4 * t**2 * (t - 1) + 2 * (t - 1) ** 2 + 8 * (t - 1) + 3
)
checks["P_positive_decomposition"] = zero_matrix(sp.Matrix([P - P_positive]))
derivative = (1 - T / (T - z) ** 2) / q
checks["weight_derivative"] = zero_matrix(
    sp.Matrix([sp.diff(weight(z), z) - derivative])
)
checks["weight_derivative_lower_bound"] = zero_matrix(
    sp.Matrix([(q + 1) ** 2 - T - q**2])
)
checks["terminal_weight"] = zero_matrix(sp.Matrix([1 - weight(q) - 1 / (q + 1)]))
w = sp.Matrix([T - 2 * s, T - s])
costate = sp.Matrix([(q - s) / (2 * q), s / (2 * q * (T - s))])
checks["coefficient_costate"] = zero_matrix(M * w - costate)

record = {
    "status": "exact rational local identities and all-horizon sign proof",
    "scope": "analytic alternative potential; not saved numerical reverse-LDL grouping",
    "domain": "integer N>=1, L>0, q=theta[N-1]^2>=1; 0<=s<=q",
    "normalization": "Use v=g/L; multiply each quadratic potential/remainder by L",
    "b(s)": str(weight(z)),
    "M(s)": [[str(value) for value in row] for row in coefficient(z).tolist()],
    "d": str(d_formula),
    "e": [str(sp.factor(value)) for value in e],
    "gamma": str(gamma),
    "n": [str(value) for value in n],
    "P": str(P),
    "P_positive_decomposition": str(P_positive),
    "initial_coefficient": str(initial_coefficient),
    "terminal_extra_square_coefficient": "1/(4*(q+1))",
    "checks": checks,
    "SDP_calls": 0,
    "web_calls": 0,
    "validation_command": ".venv/Scripts/python.exe -B examples_peppy/ogm_conjecture4_test_20260916_2am/supplementary/b5_local_derivation.py",
}
output = Path(__file__).with_suffix(".json")
output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(
    json.dumps(
        {"output": str(output), "checks": len(checks), "all_exact_zero": True}, indent=2
    )
)
