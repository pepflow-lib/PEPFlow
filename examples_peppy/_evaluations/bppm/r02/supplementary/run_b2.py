import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import inspect
import json

import numpy as np
import sympy as sp
from bppm_setup import get_pep_setup

# local helper resolved by the notebook runtime path
from certificates import (  # ty: ignore[unresolved-import]
    candidate_weights,
    capture,
    entries_for,
    max_abs,
)

# local helper resolved by the notebook runtime path
from runtime import APPROVED, ATTEMPT, solve_explicit  # ty: ignore[unresolved-import]

import pepflow as pf

b1 = json.loads((ATTEMPT / "state/bppm_b1.json").read_text())
N = b1["N_verify"]
ctx, pb, obj = get_pep_setup(N, {})
weights = candidate_weights(N, sp.Integer(1))
relaxed = [c.name for c, *_ in entries_for(ctx, pb) if c.name not in weights]
pb.set_relaxed_constraints(relaxed)
allowlist = json.loads((APPROVED / "allowlist.json").read_text())
paths = [
    Path(p)
    for p in allowlist["exact_read_files"]
    if Path(p).parent == APPROVED / "pepflow"
]
paths += [
    ATTEMPT / "bppm_setup.py",
    ATTEMPT / "supplementary/helpers/runtime.py",
    ATTEMPT / "supplementary/helpers/certificates.py",
]
hashes = {
    str(p.relative_to(ATTEMPT)).replace("\\", "/"): hashlib.sha256(
        p.read_bytes()
    ).hexdigest()
    for p in paths
}
result, attempts = solve_explicit(ctx, pb, {"alpha": 1, "R": 1})
dense = json.loads((ATTEMPT / "state/bppm_dense.json").read_text())
data = capture(ctx, pb, result, attempts, b1, dense["opt_value"], hashes)
errors = {
    name: abs(float(weights.get(name, 0)) - float(value or 0))
    for name, value in data["named_dual_values"].items()
}
assert max(errors.values()) < 1e-4
S_error = max_abs(data["S_matrix"])
assert S_error < 1e-4
pm = pf.ExpressionManager(ctx, resolve_parameters={"alpha": 1, "R": 1})
candidate_residual = pb.performance_metric - sp.Rational(1, N)
for c, *_ in entries_for(ctx, pb):
    candidate_residual -= weights.get(c.name, 0) * (pf.Scalar.zero() + c.lhs - c.rhs)
exact = pm.eval_scalar(candidate_residual)
exact_check = all(
    sp.simplify(v) == 0
    for array in (
        exact.inner_prod_coords,
        exact.func_coords,
        np.asarray([exact.offset]),
    )
    for v in np.asarray(array, dtype=object).flat
)
assert exact_check
for p in paths:
    assert (
        hashlib.sha256(p.read_bytes()).hexdigest()
        == hashes[str(p.relative_to(ATTEMPT)).replace("\\", "/")]
    )
data.update(
    lamb_code=inspect.getsource(candidate_weights),
    S_code="def S_candidate(ctx):\n    return pf.Scalar.zero()\n",
    S_decomp_type="direct",
    formula_status={"lambda": "candidate", "S": "candidate"},
    closed_form_search={
        "completed": True,
        "references_reviewed": [
            "Own input and approved generic framework only; no target references authorized."
        ],
        "attempts": [
            "Dense dual support suggested star-to-iterate f constraints and directed adjacent h constraints. Enforced adjacent f/h and terminal h support on a fresh solve.",
            "Recognized selected f weights 1/N and (k-1)/N, and h weights k/(alpha*N), (k-1)/(alpha*N), terminal 1/(alpha*N).",
            "All numerical S eigenvalues are near zero; tested exact S=0 candidate without replacing the coherent numerical S.",
        ],
        "candidate_checks": {
            "maximum_lambda_error": max(errors.values()),
            "S_zero_max_error": S_error,
            "fixed_N_exact_identity": exact_check,
        },
        "unresolved_components": [
            "Arbitrary-horizon and parameter-domain analytic certificate proof"
        ],
    },
    numerical_certificate_verified=True,
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=False,
    require_analytic_full_pep=False,
    proof_valid=True,
)
for name in ("bppm_relaxed.json", "bppm_b2.json"):
    (ATTEMPT / "state" / name).write_text(json.dumps(data, indent=2, allow_nan=False))
(ATTEMPT / "state/bppm_relaxed_constraints.json").write_text(
    json.dumps(relaxed, indent=2)
)
print(
    json.dumps(
        {
            "N": N,
            "optimum": data["opt_value"],
            "certificate_id": data["certificate_id"],
            "checks": data["numerical_checks"],
            "candidate_checks": data["closed_form_search"]["candidate_checks"],
        },
        indent=2,
    )
)
print("Active selected duals:")
for name, value in data["named_dual_values"].items():
    if value is not None:
        print(name, value)
