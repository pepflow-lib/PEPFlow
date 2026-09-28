"""Acquire the B3-requested second complete sample, without rank analysis."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "supplementary"), str(ROOT / "supplementary/helpers")]
import numpy as np  # noqa: E402
import run_b1  # noqa: E402,F401

# local helper resolved by the notebook runtime path
from candidate_formulas import (  # noqa: E402  # ty: ignore[unresolved-import]
    candidate_multipliers,
    candidate_square,
)

# local helper resolved by the notebook runtime path
from certificate import (  # noqa: E402  # ty: ignore[unresolved-import]
    capture,
    certificate_id,
    verify_certificate,
)
from dual_feg_setup import get_pep_setup  # noqa: E402

prior = json.loads((ROOT / "state/dual_feg_b2.json").read_text())
hashes = dict(prior["certificate_provenance"]["source_hashes"])
hashes["supplementary/b2_confirm_n6.py"] = hashlib.sha256(
    Path(__file__).read_bytes()
).hexdigest()
n, params = 6, json.loads(prior["params_json"])
dense = capture(get_pep_setup, n, params, [], hashes)
(ROOT / "supplementary/b2-N6-dense.json").write_text(json.dumps(dense, indent=2))
print(
    "N=6 dense",
    dense["opt_value"],
    dense["certificate_provenance"]["solver_status"],
    flush=True,
)
keep = {"initial_condition", f"A monotone:x_{n},x_star", f"A Lipschitz:x_{n - 1},x_{n}"}
for k in range(n - 1):
    keep.add(f"A monotone:x_{n},x_half_{k}")
    keep.add(f"A Lipschitz:x_{k},x_half_{k}")
dropped = [name for name in dense["constraint_metadata"] if name not in keep]
selected = capture(get_pep_setup, n, params, dropped, hashes)
checks, ctx, pm, checked = verify_certificate(
    selected, get_pep_setup, dense["opt_value"]
)
selected["numerical_checks"] = checks
print("N=6 numerical checks", checks, flush=True)
assert checks["passed"]
candidate = candidate_multipliers(n)
lambda_error = max(
    abs(float(value) - selected["named_dual_values"][name])
    for name, value in candidate.items()
)
square = pm.eval_scalar(candidate_square(ctx, n))
square_error = float(
    np.max(
        np.abs(np.asarray(square.inner_prod_coords, dtype=float) - selected["S_matrix"])
    )
)
state = {**prior, **selected}
state["closed_form_search"] = {
    **prior["closed_form_search"],
    "reused_from_certificate_id": prior["certificate_id"],
    "N6_comparison": {
        "lambda_max_abs_error": lambda_error,
        "S_gram_max_abs_error": square_error,
        "comparison_atol": 1e-4,
        "passed": lambda_error <= 1e-4 and square_error <= 1e-4,
    },
}
state["numerical_certificate_verified"] = True
state["analytic_full_pep_verified"] = False
state["lyapunov_proof_verified"] = False
state["certificate_id"] = certificate_id(state)
state["sample_role"] = (
    "Additional B3 confirmation sample; selected main handoff remains N=4"
)
for relative, expected in hashes.items():
    assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
(ROOT / "supplementary/b2-N6.json").write_text(
    json.dumps(state, indent=2, allow_nan=False)
)
print("N=6 candidate comparisons", state["closed_form_search"]["N6_comparison"])
print("N=6 complete certificate saved", state["certificate_id"])
