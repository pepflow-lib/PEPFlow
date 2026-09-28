import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import NOTEBOOK_DIR, configure  # ty: ignore[unresolved-import]

configure()
import json  # noqa: E402 - imports follow runtime or notebook setup

import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from grouping import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    construct,
)
from pgm_setup import f, g  # noqa: E402 - imports follow runtime or notebook setup

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup
from pepflow.lyapunov_utils import (  # noqa: E402 - imports follow runtime or notebook setup
    find_symmetric_coefficient_matrix,
    vectors_in_column_space,
)

b3 = json.loads((NOTEBOOK_DIR / "state/pgm_b3.json").read_text())
ctx, pb, lyap, sample = construct(b3, verbose=False)
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
rows = []
for k in range(1, b3["N_verify"] + 1):
    labels = ["d0", "dk", "ak-astar", "ak+sk"]
    vectors = [
        ctx["x_0"] - ctx["x_star"],
        ctx[f"x_{k}"] - ctx["x_star"],
        f.grad(ctx[f"x_{k}"]) - f.grad(ctx["x_star"]),
        f.grad(ctx[f"x_{k}"]) + g.grad(ctx[f"x_{k}"]),
    ]
    if k == b3["N_verify"]:
        labels, vectors = labels[:1], vectors[:1]
    good = vectors_in_column_space(
        lyap[k],
        vectors,
        pep_context=ctx,
        resolve_parameters={"L": sp.S.One, "R": sp.S.One},
        rtol=1e-4,
        atol=1e-4,
    )
    B = np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
    M = np.array(pm.eval_scalar(lyap[k]).inner_prod_coords, dtype=float)
    inv = np.linalg.pinv(B)
    C = inv @ M @ inv.T
    err = np.linalg.norm(B @ C @ B.T - M)
    try:
        coeff = find_symmetric_coefficient_matrix(
            lyap[k],
            vectors,
            pep_context=ctx,
            resolve_parameters={"L": sp.S.One, "R": sp.S.One},
            indep_tol=1e-7,
            span_tol=1e-5,
        )
        status = "passed"
    except ValueError as e:
        status = str(e)
    row = {
        "k": k,
        "labels": labels,
        "in_col_count": len(good),
        "error": float(err),
        "status": status,
        "C": C.tolist(),
    }
    rows.append(row)
    print(json.dumps(row))
(NOTEBOOK_DIR / "supplementary/b4-initial-template.json").write_text(
    json.dumps(rows, indent=2)
)
