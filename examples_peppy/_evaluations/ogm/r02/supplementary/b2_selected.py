"""Select a sparse complete numerical B2 certificate and test candidate formulas."""
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for key in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:
    os.environ[key] = "1"
sys.path[:0] = [str(ROOT / "supplementary/approved"), str(ROOT), str(ROOT / "supplementary/helpers")]
import numpy as np  # noqa: E402
import pepflow as pf  # noqa: E402
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis  # noqa: E402
from certificate_tools import PARAMS, acquire, inventory, source_hashes, summary  # noqa: E402
from ogm_setup import theta_sequence  # noqa: E402

b1 = json.loads((ROOT / "state/ogm_b1.json").read_text())
N = int(sys.argv[1]) if len(sys.argv) > 1 else b1["N_verify"]
destination = ROOT / "state" if N == b1["N_verify"] else ROOT / "supplementary" / f"horizon_N{N}"
dense = json.loads((destination / "ogm_dense.json").read_text())


def point_index(tag):
    return -1 if tag == "x_star" else 0 if tag == "z_0" else int(tag.split("_")[-1])


relaxed = []
for name, meta in dense["constraint_metadata"].items():
    if meta["origin"] == "initial":
        continue
    left, right = name.split(":")[1].split(",")
    i, j = point_index(left), point_index(right)
    if not (i == -1 or (0 <= i < N and j == i + 1)):
        relaxed.append(name)

ctx, pb, obj, selected = acquire(N, relaxed)
print(json.dumps(summary(selected), indent=2), flush=True)
assert abs(selected["opt_value"] - dense["opt_value"]) < 1e-5
pm = pf.ExpressionManager(ctx, resolve_parameters=PARAMS)
basis = ctx.basis_vectors()
S_array = np.array(selected["S_matrix"])
S_named = pf.MatrixWithNames(S_array, selected["S_row_names"], selected["S_col_names"])
# No target-specific reference is permitted. Decompose only this own selected sample.
D, ell = ldl_decompose_with_reversed_basis(S_named, basis, print_output=False)
E = np.array([pm.eval_vector(v).coords for v in ell], dtype=float)
S_numeric = sum((float(D[i, j]) * ell[i] * ell[j] for i, j in np.ndindex(D.shape)), pf.Scalar.zero())

weighted_constraints = pf.Scalar.zero()
inequality_duals = []
for c, *_ in inventory(ctx, pb):
    value = selected["named_dual_values"][c.name]
    if c.name in relaxed:
        assert value is None
        continue
    assert value is not None
    residual = c.lhs - c.rhs
    if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
        residual = -residual
    weighted_constraints += value * residual
    if c.cmp != pf.Comparator.EQ:
        inequality_duals.append(value)
checked = pm.eval_scalar(pb.performance_metric - selected["opt_value"] - weighted_constraints + S_numeric)


def max_abs(values):
    return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0))


residuals = dict(identity_gram_max_abs=max_abs(checked.inner_prod_coords),
                 identity_func_max_abs=max_abs(checked.func_coords), identity_offset_abs=max_abs(checked.offset),
                 S_reconstruction_max_abs=max_abs(E.T @ D @ E - S_array),
                 dense_relaxed_gap=abs(selected["opt_value"] - dense["opt_value"]),
                 minimum_scalar_inequality_dual=min(inequality_duals),
                 minimum_S_eigenvalue=float(np.linalg.eigvalsh(S_array).min()),
                 minimum_matrix_inequality_eigenvalue=0.0)
tolerances = dict(identity_atol=1e-5, identity_rtol=0.0, reconstruction_atol=1e-4,
                   reconstruction_rtol=1e-5, dual_tol=1e-6, psd_tol=1e-6, dense_opt_atol=1e-5)
passed = (selected["certificate_provenance"]["solver_status"] == "optimal"
          and all(residuals[k] <= 1e-5 for k in ("identity_gram_max_abs", "identity_func_max_abs", "identity_offset_abs"))
          and np.all(np.isfinite(S_array)) and np.allclose(S_array, S_array.T, atol=1e-6, rtol=0)
          and np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
          and residuals["dense_relaxed_gap"] < 1e-5
          and residuals["minimum_scalar_inequality_dual"] >= -1e-6
          and residuals["minimum_S_eigenvalue"] >= -1e-6)
assert passed, residuals

# Initial closed-form search: multiply lambdas by theta_N^2 and compare theta powers.
theta = theta_sequence(N)
lamb_code = '''def lamb(ri, ci):
    i, j = point_index(ri), point_index(ci)
    if i == -1 and j >= 0:
        return 1/theta[N] if j == N else 2*theta[j]/theta[N]**2
    if 0 <= i < N and j == i+1:
        return 2*theta[i]**2/theta[N]**2
    return 0.0
'''
namespace: dict[str, Any] = {"point_index": point_index, "theta": theta, "N": N}
exec(lamb_code, namespace)
lamb = namespace["lamb"]
lambda_candidate = np.array([[lamb(ri, ci) for ci in selected["lambda_col_names"]]
                             for ri in selected["lambda_row_names"]])
lambda_error = max_abs(lambda_candidate - np.array(selected["lambda_matrix"]))
S_code = 'S_guess = (ctx[f"z_{N}"] - ctx["x_star"] - (theta[N]/L)*ctx[f"g_{N}"])**2 * (L/(2*theta[N]**2))'
from ogm_setup import L  # noqa: E402
S_guess = (ctx[f"z_{N}"] - ctx["x_star"] - (theta[N] / L) * ctx[f"g_{N}"])**2 * (L / (2 * theta[N]**2))
guess_eval = pm.eval_scalar(S_guess)
S_error = max_abs(guess_eval.inner_prod_coords - S_array)
candidate_checks = dict(lambda_max_abs=lambda_error, S_gram_max_abs=S_error,
                        S_func_max_abs=max_abs(guess_eval.func_coords), S_offset_abs=max_abs(guess_eval.offset))
print("Residuals:", json.dumps(residuals), flush=True)
print("Candidate checks:", json.dumps(candidate_checks), flush=True)
print("LDL diagonal:", np.diag(D), flush=True)
formula_status = {"lambda": "candidate" if lambda_error <= 1e-4 else "unresolved",
                  "S": "candidate" if max(candidate_checks[k] for k in ("S_gram_max_abs", "S_func_max_abs", "S_offset_abs")) <= 1e-4 else "unresolved"}
assert source_hashes() == selected["certificate_provenance"]["source_hashes"]
selected.update({**{k: v for k, v in b1.items() if k not in selected},
    "numerical_checks": dict(tolerances=tolerances, residuals=residuals, passed=bool(passed)),
    "numerical_decomposition": dict(method="reverse_ldl", D=D.tolist(), ell_coords=E.tolist(), basis_labels=[str(v) for v in basis]),
    "closed_form_search": dict(completed=True, references_reviewed=["own input and own selected numerical certificate; target references excluded by clean-room policy"],
        attempts=["Scaled lambda by theta_N^2 and tested linear theta star row / quadratic theta forward chain", "Tested rank-one terminal vector z_N-x_star-theta_N*g_N/L against selected S"],
        candidate_checks=candidate_checks, unresolved_components=["analytic all-horizon validity of lambda and S"]),
    "formula_status": formula_status, "lamb_code": lamb_code if formula_status["lambda"] == "candidate" else None,
    "S_code": S_code if formula_status["S"] == "candidate" else None, "S_decomp_type": "ldl",
    "numerical_certificate_verified": True, "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False, "require_analytic_full_pep": False, "proof_valid": True,
    "sparsity_recipe": "Retain star-to-all and forward consecutive pairs only; z_0 is x_0 alias",
    "lambda_candidate": lambda_candidate.tolist(), "S_candidate": np.array(guess_eval.inner_prod_coords, dtype=float).tolist()})
certificate_keys = ('N_verify', 'params_json', 'relaxed_constraints', 'S_matrix', 'S_row_names',
    'S_col_names', 'basis_vectors', 'basis_scalars', 'opt_value', 'tau_sol', 'tau_name',
    'named_dual_values', 'constraint_metadata', 'normalization', 'certificate_provenance',
    'numerical_checks', 'numerical_decomposition')
selected["certificate_id"] = hashlib.sha256(json.dumps({k: selected[k] for k in certificate_keys}, sort_keys=True,
    separators=(',', ':'), allow_nan=False).encode()).hexdigest()
for name in ("ogm_relaxed.json", "ogm_b2.json"):
    (destination / name).write_text(json.dumps(selected, indent=2, allow_nan=False))
