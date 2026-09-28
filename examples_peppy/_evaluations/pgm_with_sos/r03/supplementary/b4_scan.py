import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import NOTEBOOK_DIR, configure  # ty: ignore[unresolved-import]

configure()
import json  # noqa: E402 - imports follow runtime or notebook setup
from itertools import (  # noqa: E402 - imports follow runtime or notebook setup
    combinations,
)

import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from grouping import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    construct,
)
from pgm_setup import f, g  # noqa: E402 - imports follow runtime or notebook setup

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup
from pepflow.lyapunov_utils import (  # noqa: E402 - imports follow runtime or notebook setup
    vectors_in_column_space,
)

b3 = json.loads((NOTEBOOK_DIR / "state/pgm_b3.json").read_text())
ctx, pb, lyap, sample = construct(b3, verbose=False)
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
n = b3["N_verify"]
base = [("d0", ctx["x_0"] - ctx["x_star"]), ("astar", f.grad(ctx["x_star"]))]
for j in range(n + 1):
    base.extend(
        [(f"d{j}", ctx[f"x_{j}"] - ctx["x_star"]), (f"a{j}", f.grad(ctx[f"x_{j}"]))]
    )
    if j:
        base.append((f"s{j}", g.grad(ctx[f"x_{j}"])))
pairs = base + [(a + "-" + b, x - y) for (a, x), (b, y) in combinations(base, 2)]
pairs += [
    (f"a{j}+s{j}", f.grad(ctx[f"x_{j}"]) + g.grad(ctx[f"x_{j}"]))
    for j in range(1, n + 1)
]
seen = []
clean = []
for label, v in pairs:
    co = np.asarray(pm.eval_vector(v).coords, dtype=float)
    if np.linalg.norm(co) > 1e-7 and not any(
        np.allclose(co, c, atol=1e-10, rtol=0) for c in seen
    ):
        clean.append((label, v))
        seen.append(co)
data = []
for k in range(1, n):
    good = vectors_in_column_space(
        lyap[k],
        [v for _, v in clean],
        pep_context=ctx,
        resolve_parameters={"L": sp.S.One, "R": sp.S.One},
        rtol=1e-4,
        atol=1e-4,
    )
    labels = [label for label, v in clean if any(v is g for g in good)]
    print(k, labels)
    data.append({"k": k, "labels": labels})
(NOTEBOOK_DIR / "supplementary/b4-scan.json").write_text(json.dumps(data, indent=2))
