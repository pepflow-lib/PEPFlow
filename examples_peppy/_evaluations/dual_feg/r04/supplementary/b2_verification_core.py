# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

# B2 mathematical checks, also embedded verbatim in the notebook.
import hashlib
import json
from fractions import Fraction

import numpy as np

# local helper resolved by the notebook runtime path
from certificate_tools import source_hashes  # ty: ignore[unresolved-import]

import pepflow as pf
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

b1 = json.loads((notebook_dir / "state" / "dual_feg_b1.json").read_text())
dense = json.loads((notebook_dir / "state" / "dual_feg_dense.json").read_text())
selected = json.loads(
    (notebook_dir / "supplementary" / "b2-selected-structural.json").read_text()
)
N = selected["N"]
ctx, pb, obj = get_pep_setup(N, {"L": 1, "R": 1})
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
groups = ctx.get_constraint_data(obj)
entries = [(c, "initial", None, None) for c in pb.init_conditions]
entries.extend(
    (c, "interpolation", str(obj), str(group))
    for group, constraints in groups.sc_dict.items()
    for c in constraints
)
assert not groups.psd_dict and not ctx.func_to_triplets
assert set(selected["named_dual_values"]) == {c.name for c, *_ in entries}
assert selected["certificate_provenance"]["source_hashes"] == source_hashes(
    notebook_dir
)
basis = ctx.basis_vectors()
labels = [str(v) for v in basis]
assert (
    labels
    == selected["basis_vectors"]
    == selected["S_row_names"]
    == selected["S_col_names"]
)
assert [str(v) for v in ctx.basis_scalars()] == selected["basis_scalars"]
assert selected["tau_name"] == "initial_condition"
S_array = np.asarray(selected["S_matrix"], dtype=float)
S_sol = pf.MatrixWithNames(S_array, labels, labels)
D, ell = ldl_decompose_with_reversed_basis(S_sol, basis, print_output=False)
E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
S_numeric = sum(
    (float(D[i, j]) * ell[i] * ell[j] for i, j in np.ndindex(D.shape)), pf.Scalar.zero()
)
weighted = pf.Scalar.zero()
inequality_values = []
for c, origin, owner, group in entries:
    meta = selected["constraint_metadata"][c.name]
    assert (
        meta["origin"] == origin and meta["owner"] == owner and meta["group"] == group
    )
    assert (
        meta["comparator"] == c.cmp.value
        and meta["kind"] == "scalar"
        and meta["shape"] == []
    )
    value = selected["named_dual_values"][c.name]
    if meta["relaxed"]:
        assert c.name in selected["relaxed_constraints"] and value is None
        continue
    assert value is not None and np.isfinite(value)
    assert c.cmp.value == "LE"
    weighted += value * (c.lhs - c.rhs)
    inequality_values.append(value)
checked = pm.eval_scalar(
    pb.performance_metric - selected["opt_value"] - weighted + S_numeric
)


def max_abs(value):
    return float(np.max(np.abs(np.asarray(value, dtype=float)), initial=0.0))


residuals = {
    "identity_gram_max_abs": max_abs(checked.inner_prod_coords),
    "identity_func_max_abs": max_abs(checked.func_coords),
    "identity_offset_abs": max_abs(checked.offset),
    "S_reconstruction_max_abs": max_abs(E.T @ D @ E - S_array),
    "dense_relaxed_gap": abs(dense["opt_value"] - selected["opt_value"]),
    "minimum_scalar_inequality_dual": min(inequality_values),
    "minimum_S_eigenvalue": float(np.linalg.eigvalsh(S_array).min()),
    "minimum_matrix_inequality_eigenvalue": 0.0,
    "conjecture_gap": abs(selected["opt_value"] - 4 / N**2),
}
tolerances = dict(
    identity_atol=1e-5,
    identity_rtol=0,
    reconstruction_atol=1e-4,
    reconstruction_rtol=1e-5,
    dual_tol=1e-6,
    psd_tol=1e-6,
    dense_opt_atol=1e-5,
)
assert selected["certificate_provenance"]["solver_status"] == "optimal"
assert np.isfinite(S_array).all() and np.allclose(S_array, S_array.T, atol=1e-6, rtol=0)
assert all(
    residuals[key] <= 1e-5
    for key in ("identity_gram_max_abs", "identity_func_max_abs", "identity_offset_abs")
)
assert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
assert residuals["dense_relaxed_gap"] < 1e-5 and residuals["conjecture_gap"] < 1e-5
assert residuals["minimum_scalar_inequality_dual"] >= -1e-6
assert residuals["minimum_S_eigenvalue"] >= -1e-6
print("Numerical certificate checks:", json.dumps(residuals, indent=2))
pf.pprint_labeled_matrix(
    pf.MatrixWithNames(
        np.asarray(checked.inner_prod_coords, dtype=float), labels, labels
    )
)
print("Reverse LDL diagonal:", np.diag(D))
pf.pprint_labeled_matrix(pf.MatrixWithNames(E.T @ D @ E, labels, labels))

# Initial closed-form attempt: terminal-star monotonicity and within-step Lipschitz.
# These are candidate formulas, verified here only at the selected fixed horizon.
candidate = {"initial_condition": 4 / N**2, f"A monotone:x_{N},x_star": 4 / N}
for k in range(N - 1):
    t = N - k
    candidate[f"A monotone:x_{k}_half,x_{N}"] = 4 / (t * (t - 1))
    candidate[f"A Lipschitz:x_{k},x_{k}_half"] = 2 / t**2
candidate[f"A Lipschitz:x_{N - 1},x_{N}"] = 2
lambda_error = max(
    abs(selected["named_dual_values"][name] - value)
    for name, value in candidate.items()
)
assert set(candidate) == {
    name
    for name, meta in selected["constraint_metadata"].items()
    if not meta["relaxed"]
}
assert lambda_error < 1e-4
square = (2 / N * (ctx["x_0"] - ctx["x_star"]) - obj(ctx[f"x_{N}"])) ** 2
square_eval = pm.eval_scalar(square)
S_error = max_abs(square_eval.inner_prod_coords - S_array)
assert (
    S_error < 1e-4
    and max_abs(square_eval.func_coords) == 0
    and max_abs(square_eval.offset) == 0
)
candidate_weighted = sum(
    (candidate.get(c.name, 0.0) * (c.lhs - c.rhs) for c, *_ in entries),
    pf.Scalar.zero(),
)
candidate_identity = pm.eval_scalar(
    pb.performance_metric - 4 / N**2 - candidate_weighted + square
)
candidate_residual = max(
    max_abs(candidate_identity.inner_prod_coords),
    max_abs(candidate_identity.func_coords),
    max_abs(candidate_identity.offset),
)
assert candidate_residual < 1e-5
for name, value in candidate.items():
    print(
        name,
        "numerical",
        selected["named_dual_values"][name],
        "candidate",
        Fraction(value).limit_denominator(1000),
    )
print(
    "Candidate lambda error:",
    lambda_error,
    "Candidate S error:",
    S_error,
    "Fixed-N identity residual:",
    candidate_residual,
)
pf.pprint_labeled_matrix(
    pf.MatrixWithNames(
        np.asarray(square_eval.inner_prod_coords, dtype=float), labels, labels
    )
)

state_b2 = {
    **b1,
    **selected,
    "normalization": {
        "tau_name": "initial_condition",
        "initial_condition": b1["initial_condition"],
        "performance_metric": b1["performance_metric"],
        "bound_value": selected["opt_value"],
        "bound_formula": b1["conjectured_rate"],
    },
    "numerical_checks": {
        "tolerances": tolerances,
        "residuals": residuals,
        "passed": True,
    },
    "numerical_decomposition": {
        "method": "reverse_ldl",
        "D": D.tolist(),
        "ell_coords": E.tolist(),
        "basis_labels": labels,
    },
    "formula_status": {"lambda": "candidate", "S": "candidate"},
    "closed_form_search": {
        "completed": True,
        "references_reviewed": [
            "Own B1 and dense/threshold/structural B2 results; external/reference examples excluded by clean-room policy"
        ],
        "attempts": [
            {
                "method": "Threshold lambda at 1e-6",
                "outcome": "Preserved bound; terminal duplicate evaluations obscure formulas",
            },
            {
                "method": "Terminal-star monotonicity and within-step Lipschitz constraint pattern",
                "outcome": "Preserved bound with 12 interpolation constraints",
            },
            {
                "method": "Rational reconstruction in t=N-k",
                "outcome": "lambda candidates 4/[t(t-1)], 2/t^2, terminal-root 4/N for L=R=1",
                "max_error": lambda_error,
            },
            {
                "method": "Rank-one eigenvector inspection and direct square candidate",
                "outcome": "S=((2/N)(x0-xstar)-A(xN))^2 for L=1",
                "max_error": S_error,
                "identity_residual": candidate_residual,
            },
        ],
        "unresolved_components": [
            "Arbitrary-horizon and parameter-domain proof of lambda and S formulas"
        ],
    },
    "lamb_code": "candidate = {'initial_condition': 4/N**2, f'A monotone:x_{N},x_star': 4/N}\nfor k in range(N-1):\n    t=N-k\n    candidate[f'A monotone:x_{k}_half,x_{N}']=4/(t*(t-1))\n    candidate[f'A Lipschitz:x_{k},x_{k}_half']=2/t**2\ncandidate[f'A Lipschitz:x_{N-1},x_{N}']=2",
    "S_code": "S_guess=(2/N*(ctx['x_0']-ctx['x_star'])-obj(ctx[f'x_{N}']))**2",
    "candidate_formula_domain": "L=R=1; formulas currently checked only at N=6",
    "S_decomp_type": "ldl",
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "require_analytic_full_pep": False,
    "proof_valid": True,
}
certificate_keys = (
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
state_b2["certificate_id"] = hashlib.sha256(
    json.dumps(
        {key: state_b2[key] for key in certificate_keys},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
).hexdigest()
for filename in ("dual_feg_relaxed.json", "dual_feg_b2.json"):
    (notebook_dir / "state" / filename).write_text(
        json.dumps(state_b2, indent=2, allow_nan=False)
    )
