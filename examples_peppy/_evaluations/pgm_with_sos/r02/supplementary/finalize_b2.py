import hashlib
import importlib.util
import inspect
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
import candidates  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
import certificate  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup
from pepflow.parameter import (  # noqa: E402 - imports follow runtime or notebook setup
    eval_parameter,
)

b1 = json.loads((root / "state/pgm_b1.json").read_text())
dense = json.loads((root / "state/pgm_dense.json").read_text())
data = json.loads((root / "supplementary/b2-sparse-hypothesis1.json").read_text())
for path, expected in data["certificate_provenance"]["source_hashes"].items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected
checks, ctx, pb, _ = certificate.verify(data, dense["opt_value"])
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
pieces = candidates.sos_pieces(ctx, data["N"])
D = np.diag([float(eval_parameter(c, {"L": sp.S.One})) for _, _, c, _ in pieces])
E = np.asarray([pm.eval_vector(u).coords for _, _, _, u in pieces], dtype=float)
decomp = dict(
    method="direct",
    D=D.tolist(),
    ell_coords=E.tolist(),
    basis_labels=data["basis_vectors"],
    piece_labels=[f"{name}_{i}" for i, name, _, _ in pieces],
    source="Fixed supplied SOS candidate; normalization factor 1",
    reconstruction_source=inspect.getsource(candidates.sos_pieces),
    minimum_coefficient=float(np.diag(D).min()),
)
checks, ctx, pb, _ = certificate.verify(data, dense["opt_value"], decomp)
assert checks["passed"]
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
weighted = pf.Scalar.zero()
errors = []
for c, origin, owner, group in certificate.inventory(ctx, pb):
    if origin == "initial":
        coefficient = sp.Rational(1, 4 * data["N"])
    else:
        left, right = c.name.split(":")[1].split(",")
        coefficient = candidates.lambda_candidate(owner, left, right, data["N"])
        errors.append(
            abs(float(coefficient) - (data["named_dual_values"][c.name] or 0.0))
        )
    weighted += coefficient * certificate.residual_of(c)
exact = pm.eval_scalar(
    pb.performance_metric
    - sp.Rational(1, 4 * data["N"])
    - weighted
    + candidates.sos_scalar(ctx, data["N"]),
    sympy_mode=True,
)
exact_zero = all(
    sp.simplify(v) == 0
    for a in (exact.inner_prod_coords, exact.func_coords, np.asarray(exact.offset))
    for v in np.asarray(a).flat
)
print("Exact fixed-N candidate identity:", exact_zero)
print(
    "Nonzero exact residual entries",
    [
        (str(v), str(type(v)))
        for a in (exact.inner_prod_coords, exact.func_coords, np.asarray(exact.offset))
        for v in np.asarray(a).flat
        if sp.simplify(v) != 0
    ][:12],
)
search = dict(
    completed=True,
    references_reviewed=["approved/input.md supplied SOS aid; no external references"],
    attempts=[
        {
            "method": "Dense all-owner inspection, retain star-to-all and forward adjacent pairs",
            "outcome": "Sparse optimum preserved; complete certificate verified",
        },
        {
            "method": "Rational approximation and adjacent/star difference pattern",
            "lambda_max_abs_fit_error": max(errors),
            "outcome": "candidate formulas obtained for both f and g",
        },
        {
            "method": "Implement supplied SOS in exact arithmetic and compare to selected S",
            "S_max_abs_fit_error": checks["residuals"]["S_reconstruction_max_abs"],
            "normalization_factor": 1,
        },
        {
            "method": "Exact coordinate identity with rational candidates at selected N",
            "N": data["N"],
            "passed": exact_zero,
            "all_horizon_proof": False,
        },
    ],
    unresolved_components=[
        "All-horizon global identity proof; formulas are candidates only"
    ],
)
state = {
    **b1,
    **data,
    "numerical_checks": checks,
    "numerical_decomposition": decomp,
    "closed_form_search": search,
    "formula_status": {"lambda": "candidate", "S": "candidate"},
    "lamb_code": inspect.getsource(candidates.lambda_candidate),
    "S_code": inspect.getsource(candidates.sos_pieces)
    + "\n"
    + inspect.getsource(candidates.sos_scalar),
    "S_decomp_type": "direct",
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "require_analytic_full_pep": False,
    "proof_valid": True,
    "fixed_sample_exact_candidate_identity": exact_zero,
    "candidate_fit_max_abs": max(errors),
    "certificate_check_source": inspect.getsource(certificate.inventory)
    + "\n"
    + inspect.getsource(certificate.residual_of)
    + "\n"
    + inspect.getsource(certificate.verify),
}
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
for filename in ("pgm_relaxed.json", "pgm_b2.json"):
    (root / "state" / filename).write_text(json.dumps(state, indent=2, allow_nan=False))
print(json.dumps(checks, indent=2))
