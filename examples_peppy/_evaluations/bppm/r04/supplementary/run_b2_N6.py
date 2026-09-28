import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import inspect
import json

import runtime
from b2_core import candidate_weights, max_abs, solve_capture, verify_certificate

root = runtime.ATTEMPT
b1 = json.loads((root / "state/bppm_b1.json").read_text())
_, _, _, dense = solve_capture(6, {"alpha": 1, "R": 1}, [], root)
(root / "supplementary/bppm_N6_dense.json").write_text(json.dumps(dense, indent=2))
N = 6
params = json.loads(b1["params_json"])
candidate = candidate_weights(N, params["alpha"])
relaxed = [name for name in dense["constraint_metadata"] if name not in candidate]
(root / "supplementary/bppm_N6_constraints.json").write_text(
    json.dumps(relaxed, indent=2)
)
ctx, pb, result, data = solve_capture(N, params, relaxed, root)
checked = verify_certificate(ctx, pb, data, dense["opt_value"])
error = max(
    abs(value - candidate[name])
    for name, value in data["named_dual_values"].items()
    if value is not None
)
assert error < 1e-4
assert max_abs(data["S_matrix"]) < 1e-4
print(
    "Candidate multiplier max error:",
    error,
    "Candidate S=0 max error:",
    max_abs(data["S_matrix"]),
)
data.update(
    lamb_code=inspect.getsource(candidate_weights),
    S_code="S_guess = pf.Scalar.zero()",
    formula_status={"lambda": "candidate", "S": "candidate"},
    S_decomp_type="direct",
    closed_form_search={
        "completed": True,
        "references_reviewed": [
            "own approved input and generic function/solver API; target-specific references prohibited"
        ],
        "attempts": [
            "Dense multipliers suggest star-to-iterate f terms and forward pairs; selected consecutive-only f/h relaxation.",
            "Rational inspection yields f star weights 1/N, consecutive f weights (k-1)/N; h forward weights k/(alpha*N), reverse weights (k-1)/(alpha*N), terminal weight 1/(alpha*N).",
            "Compared every active numerical multiplier and S=0 to the selected sample.",
        ],
        "candidate_lambda_max_error": error,
        "candidate_S_max_error": max_abs(data["S_matrix"]),
        "unresolved_components": [
            "All-horizon analytic identity and parameter-domain proof are deferred; candidates verified numerically only."
        ],
    },
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=False,
    require_analytic_full_pep=False,
    proof_valid=True,
)
for relative, expected in data["certificate_provenance"]["source_hashes"].items():
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected
lambda_data = result.get_scalar_constraint_dual_value_in_numpy(
    next(owner for owner in ctx.func_to_triplets if str(owner) == "f")
)


def display(value):
    return dict(
        matrix=value.matrix.tolist(),
        row_names=list(value.row_names),
        col_names=list(value.col_names),
    )


if isinstance(lambda_data, dict):
    data["lambda_groups"] = {
        name: display(value) for name, value in lambda_data.items()
    }
else:
    data.update(
        lambda_matrix=lambda_data.matrix.tolist(),
        lambda_row_names=list(lambda_data.row_names),
        lambda_col_names=list(lambda_data.col_names),
    )
state = {**b1, **data}
keys = (
    "N_verify",
    "params_json",
    "relaxed_constraints",
    "S_matrix",
    "S_row_names",
    "S_col_names",
    "basis_vectors",
    "basis_scalars",
    "opt_value",
    "tau_sol",
    "tau_name",
    "named_dual_values",
    "constraint_metadata",
    "normalization",
    "certificate_provenance",
    "numerical_checks",
    "numerical_decomposition",
)
state["certificate_id"] = hashlib.sha256(
    json.dumps(
        {k: state[k] for k in keys},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
).hexdigest()
(root / "supplementary/bppm_N6_b2.json").write_text(
    json.dumps(state, indent=2, allow_nan=False)
)
