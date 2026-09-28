import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import configure  # ty: ignore[unresolved-import]

attempt, approved = configure()
import json  # noqa: E402 - imports follow runtime or notebook setup

import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
from ogm_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
    theta_sequence,
)

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup

s = json.loads((attempt / "supplementary/b2-chain-certificate.json").read_text())
N = s["N"]
ctx, pb, f = get_pep_setup(N, {"L": 1, "R": 1})
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": 1, "R": 1})
t = theta_sequence(N)
v = ctx[f"z_{N}"] - ctx["x_star"] - t[N] * ctx[f"g_{N}"]
q = np.asarray(pm.eval_vector(v).coords, dtype=float)
Sguess = np.outer(q, q) / (2 * t[N] ** 2)
S = np.array(s["S_matrix"])
print("candidate S residual", np.max(np.abs(Sguess - S)))
for name, val in s["named_dual_values"].items():
    if val is None or name == "initial_condition":
        continue
    a, b = name[2:].split(",")
    k = 0 if b == "z_0" else int(b[2:])
    predicted = (
        (2 * t[k] / t[N] ** 2 if k < N else 1 / t[N])
        if a == "x_star"
        else 2 * t[k - 1] ** 2 / t[N] ** 2
    )
    print(name, val, predicted, abs(val - predicted))
