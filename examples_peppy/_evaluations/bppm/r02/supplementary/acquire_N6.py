import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import json
import shutil

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
from runtime import ATTEMPT, solve_explicit  # ty: ignore[unresolved-import]

sample4 = ATTEMPT / "supplementary/samples/N4"
sample4.mkdir(parents=True, exist_ok=True)
for name in (
    "bppm_b2.json",
    "bppm_dense.json",
    "bppm_relaxed.json",
    "bppm_relaxed_constraints.json",
):
    destination = sample4 / name
    if not destination.exists():
        shutil.copyfile(ATTEMPT / "state" / name, destination)
sample6 = ATTEMPT / "supplementary/samples/N6"
sample6.mkdir(parents=True, exist_ok=True)
selected = json.loads((ATTEMPT / "state/bppm_b2.json").read_text())
b1 = json.loads((ATTEMPT / "state/bppm_b1.json").read_text())
b1["N_verify"] = 6
hashes = selected["certificate_provenance"]["source_hashes"]
for rel, digest in hashes.items():
    assert hashlib.sha256((ATTEMPT / rel).read_bytes()).hexdigest() == digest
ctx, pb, obj = get_pep_setup(6, {})
dense_result, dense_attempts = solve_explicit(
    ctx, pb, {"alpha": sp.Integer(1), "R": sp.Integer(1)}
)
dense_groups = {
    str(owner): {
        c.name: float(dense_result.get_dual_value(c.name))
        for c in owner.get_interpolation_constraints(ctx)
    }
    for owner in ctx.func_to_triplets
}
dense_S = dense_result.get_gram_dual_matrix()
dense = {
    "N": 6,
    "opt_value": float(dense_result.opt_value),
    "solver_attempts": dense_attempts,
    "all_owner_duals": dense_groups,
    "S_matrix": dense_S.matrix.tolist(),
    "S_row_names": dense_S.row_names,
    "basis_vectors": [str(v) for v in ctx.basis_vectors()],
}
(sample6 / "bppm_dense.json").write_text(json.dumps(dense, indent=2))
ctx, pb, obj = get_pep_setup(6, {})
weights = candidate_weights(6, sp.Integer(1))
relaxed = [c.name for c, *_ in entries_for(ctx, pb) if c.name not in weights]
pb.set_relaxed_constraints(relaxed)
result, attempts = solve_explicit(ctx, pb, {"alpha": sp.Integer(1), "R": sp.Integer(1)})
data = capture(ctx, pb, result, attempts, b1, dense["opt_value"], hashes)
error = max(
    abs(float(weights.get(name, 0)) - float(value or 0))
    for name, value in data["named_dual_values"].items()
)
assert error < 1e-4
assert max_abs(data["S_matrix"]) < 1e-4
for key in (
    "lamb_code",
    "S_code",
    "S_decomp_type",
    "formula_status",
    "closed_form_search",
    "require_analytic_full_pep",
):
    data[key] = selected[key]
data["closed_form_search"] = {
    **data["closed_form_search"],
    "reused_from_certificate": selected["certificate_id"],
    "N6_candidate_checks": {
        "maximum_lambda_error": error,
        "S_zero_max_error": max_abs(data["S_matrix"]),
    },
}
data.update(
    numerical_certificate_verified=True,
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=False,
    proof_valid=True,
)
for rel, digest in hashes.items():
    assert hashlib.sha256((ATTEMPT / rel).read_bytes()).hexdigest() == digest
(sample6 / "bppm_b2.json").write_text(json.dumps(data, indent=2, allow_nan=False))
(sample6 / "bppm_relaxed_constraints.json").write_text(json.dumps(relaxed, indent=2))
print(
    json.dumps(
        {
            "N": 6,
            "certificate_id": data["certificate_id"],
            "dense_optimum": dense["opt_value"],
            "selected_optimum": data["opt_value"],
            "checks": data["numerical_checks"],
            "lambda_candidate_error": error,
            "S_eigenvalues": np.linalg.eigvalsh(np.asarray(data["S_matrix"])).tolist(),
        },
        indent=2,
    )
)
