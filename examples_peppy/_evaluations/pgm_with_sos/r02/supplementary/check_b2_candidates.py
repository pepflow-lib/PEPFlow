import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime", root / "supplementary/helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
from candidates import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    lambda_candidate,
    sos_scalar,
)
from certificate import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    inventory,
    residual_of,
    verify,
)

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup

data = json.loads((root / "supplementary/b2-sparse-hypothesis1.json").read_text())
checks, ctx, pb, _ = verify(data, data["opt_value"])
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": 1, "R": 1})
S = pm.eval_scalar(sos_scalar(ctx, 4))
print(
    "SOS discrepancy",
    np.max(
        abs(np.asarray(S.inner_prod_coords, dtype=float) - np.asarray(data["S_matrix"]))
    ),
)
print(
    "SOS norm ratios",
    np.linalg.norm(np.asarray(S.inner_prod_coords, dtype=float))
    / np.linalg.norm(data["S_matrix"]),
)
weighted = pf.Scalar.zero()
errors = []
for c, origin, owner, group in inventory(ctx, pb):
    if origin == "initial":
        coeff = 1 / pf.Parameter("L") if False else __import__("sympy").Rational(1, 16)
    else:
        left, right = c.name.split(":")[1].split(",")
        coeff = lambda_candidate(owner, left, right, 4)
        value = data["named_dual_values"][c.name] or 0.0
        errors.append(abs(float(coeff) - value))
    weighted += coeff * residual_of(c)
diff = pm.eval_scalar(
    pb.performance_metric
    - __import__("sympy").Rational(1, 16)
    - weighted
    + sos_scalar(ctx, 4)
)
print("lambda fit", max(errors))
print("exact residual", diff.inner_prod_coords, diff.func_coords, diff.offset)
