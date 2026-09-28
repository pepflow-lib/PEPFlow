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
from pgm_setup import f  # noqa: E402 - imports follow runtime or notebook setup

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup
from pepflow.lyapunov_utils import (  # noqa: E402 - imports follow runtime or notebook setup
    find_basis_with_sparsest_coefficients,
    vectors_in_column_space,
)

b3 = json.loads((NOTEBOOK_DIR / "state/pgm_b3.json").read_text())
ctx, pb, lyap, sample = construct(b3, verbose=False)
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
rows = []
for k in range(1, b3["N_verify"] + 1):
    pairs = [("d0", ctx["x_0"] - ctx["x_star"])]
    if k < b3["N_verify"]:
        pairs += [
            ("dk", ctx[f"x_{k}"] - ctx["x_star"]),
            ("astar", f.grad(ctx["x_star"])),
            ("ak", f.grad(ctx[f"x_{k}"])),
        ]
        pairs += [
            (a + "-" + b, x - y) for (a, x), (b, y) in combinations(list(pairs), 2)
        ]
    vecs = vectors_in_column_space(
        lyap[k],
        [v for _, v in pairs],
        pep_context=ctx,
        resolve_parameters={"L": sp.S.One, "R": sp.S.One},
        rtol=1e-4,
        atol=1e-4,
    )
    basis, C = find_basis_with_sparsest_coefficients(
        lyap[k],
        vecs,
        pep_context=ctx,
        resolve_parameters={"L": sp.S.One, "R": sp.S.One},
        zero_tol=1e-6,
        indep_tol=1e-7,
        span_tol=1e-5,
    )
    labels = [label for v in basis for label, u in pairs if u is v]
    row = {
        "k": k,
        "candidate_count": len(vecs),
        "selected_labels": labels,
        "basis_size": len(basis),
        "required_rank": sample["rank_profile"][k],
        "C": C.tolist(),
        "zero_count": int(np.sum(abs(C) < 1e-6)),
    }
    rows.append(row)
    print(row)
(NOTEBOOK_DIR / "supplementary/b4-sparse-basis-trial.json").write_text(
    json.dumps(rows, indent=2)
)
