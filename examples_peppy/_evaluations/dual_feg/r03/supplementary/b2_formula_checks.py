"""Finite sample checks of candidate formulas; no all-horizon proof claim."""

from typing import Any

# Preserve the recorded import initialization order.
# isort: split
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "supplementary"), str(ROOT / "supplementary/helpers")]
import numpy as np  # noqa: E402
import run_b1  # noqa: E402,F401
import sympy as sp  # noqa: E402

# local helper resolved by the notebook runtime path
from candidate_formulas import (  # noqa: E402  # ty: ignore[unresolved-import]
    candidate_multipliers,
    candidate_square,
)

# local helper resolved by the notebook runtime path
from certificate import inventory  # noqa: E402  # ty: ignore[unresolved-import]
from dual_feg_setup import get_pep_setup  # noqa: E402

import pepflow as pf  # noqa: E402

selected = json.loads((ROOT / "supplementary/b2-structured-candidate.json").read_text())
guesses = candidate_multipliers(selected["N_verify"])
errors = {
    name: abs(float(value) - selected["named_dual_values"][name])
    for name, value in guesses.items()
}
print("Candidate multiplier errors", errors)
samples = []
for n in [1, 2, 3, 4, 6]:
    ctx, pb, _ = get_pep_setup(n, {"L": sp.S.One, "R": sp.S.One})
    pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
    multiplier = candidate_multipliers(n)
    constraints = {c.name: c for c, *_ in inventory(ctx, pb)}
    weighted = sum(
        (
            value * (constraints[name].lhs - constraints[name].rhs)
            for name, value in multiplier.items()
        ),
        pf.Scalar.zero(),
    )
    square = candidate_square(ctx, n)
    residual = pm.eval_scalar(
        pb.performance_metric - sp.Rational(4, n**2) - weighted + square,
        sympy_mode=True,
    )
    matrix = sp.Matrix(residual.inner_prod_coords).applyfunc(sp.simplify)
    funcs = [sp.simplify(x) for x in residual.func_coords]
    offset = sp.simplify(residual.offset)
    exact_zero = (
        matrix == sp.zeros(*matrix.shape) and all(x == 0 for x in funcs) and offset == 0
    )
    sample: dict[str, Any] = dict(
        N=n, exact_identity_zero=bool(exact_zero), offset=str(offset)
    )
    if n == selected["N_verify"]:
        square_data = pm.eval_scalar(square)
        sample["S_candidate_gram_max_abs"] = float(
            np.max(
                np.abs(
                    np.asarray(square_data.inner_prod_coords, dtype=float)
                    - selected["S_matrix"]
                )
            )
        )
        sample["S_candidate_func_max_abs"] = float(
            np.max(np.abs(np.asarray(square_data.func_coords, dtype=float)), initial=0)
        )
        sample["S_candidate_offset_abs"] = float(abs(square_data.offset))
    if not exact_zero:
        sample["nonzero_entries"] = [
            (i, j, str(matrix[i, j]))
            for i, j in np.ndindex(matrix.shape)
            if matrix[i, j] != 0
        ]
    samples.append(sample)
    print(sample)
record = dict(
    lambda_candidate_errors=errors,
    lambda_comparison_passed=max(errors.values()) <= 1e-4,
    comparison_atol=1e-4,
    samples=samples,
    analytic_full_pep_verified=False,
)
(ROOT / "supplementary/b2-formula-checks.json").write_text(json.dumps(record, indent=2))
