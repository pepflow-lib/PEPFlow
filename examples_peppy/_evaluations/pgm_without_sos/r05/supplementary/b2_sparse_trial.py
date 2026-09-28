import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from owned_runtime import ROOT, configure  # ty: ignore[unresolved-import]

configure()
import json  # noqa: E402 - imports follow runtime or notebook setup
from fractions import Fraction  # noqa: E402 - imports follow runtime or notebook setup

import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
from pgm_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)
from solve_runtime import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    solve_primal,
)

ctx, pb, obj = get_pep_setup(4, {})
relaxed = []
for owner in ctx.func_to_triplets:
    for c in owner.get_interpolation_constraints(ctx):
        a, b = c.name.split(":")[1].split(",")
        keep = a == "x_star" or (
            a != "x_star" and b != "x_star" and int(b[2:]) == int(a[2:]) + 1
        )
        if not keep:
            relaxed.append(c.name)
pb.set_relaxed_constraints(relaxed)
result, meta = solve_primal(ctx, pb, {"L": 1, "R": 1})
duals = {
    name: np.asarray(c.dual_value).tolist()
    for name, c in result.dual_var_manager.named_constraints.items()
}
data = {
    "N": 4,
    "opt_value": result.opt_value,
    "solver": meta,
    "relaxed_constraints": relaxed,
    "named_duals": duals,
    "S_matrix": result.get_gram_dual_matrix().matrix.tolist(),
}
(ROOT / "supplementary" / "b2-sparse-trial.json").write_text(json.dumps(data, indent=2))
print("Bound", result.opt_value, "status", result.solver_status)
for name, value in duals.items():
    if np.asarray(value).ndim == 0:
        print(name, value, str(Fraction(float(value)).limit_denominator(1000)))
print("S eigenvalues", np.linalg.eigvalsh(result.get_gram_dual_matrix().matrix))
