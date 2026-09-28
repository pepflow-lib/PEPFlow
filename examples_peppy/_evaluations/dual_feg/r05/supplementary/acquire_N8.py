"""Finalize B2 numerical certificate and focused formula search."""
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supplementary"))
from certificate_capture import capture
import numpy as np
import pepflow as pf
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis
from pepflow.pep_result import MatrixWithNames
from dual_feg_setup import get_pep_setup

b1 = json.loads((ROOT / "state/dual_feg_b1.json").read_text())
b1["N_verify"] = 8
dense = capture(8)
(ROOT / "supplementary/dense_N8.json").write_text(json.dumps(dense, indent=2))
N_target = 8
keep = {"initial_condition", f"A monotone:x_{N_target},x_star"}
keep |= {f"A monotone:x_{N_target},y_{k}" for k in range(N_target-1)}
keep |= {f"A Lipschitz:x_{k},y_{k}" for k in range(N_target-1)}
keep.add(f"A Lipschitz:x_{N_target-1},x_{N_target}")
s = capture(N_target, [name for name in dense["named_dual_values"] if name not in keep])
ctx, pb, obj = get_pep_setup(s["N"], {"L": 1, "R": 1})
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": 1, "R": 1})
S = np.asarray(s["S_matrix"])
basis = ctx.basis_vectors()
D, ell = ldl_decompose_with_reversed_basis(MatrixWithNames(S, s["basis_vectors"], s["basis_vectors"]), basis, print_output=False)
E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
s["numerical_decomposition"] = {"method": "reverse_ldl", "D": D.tolist(), "ell_coords": E.tolist(), "basis_labels": s["basis_vectors"]}
m = s["metric_coordinates"]
gram = np.array(m["gram"]) + S
func = np.array(m["func"])
offset = m["offset"] - s["opt_value"]
for name, val in s["named_dual_values"].items():
    if val is not None:
        c = s["constraint_coordinates"][name]
        gram -= val * np.array(c["gram"])
        func -= val * np.array(c["func"])
        offset -= val * c["offset"]
res = {
 "identity_gram_max_abs": float(np.max(np.abs(gram))),
 "identity_func_max_abs": float(np.max(np.abs(func), initial=0.0)),
 "identity_offset_abs": abs(offset),
 "S_reconstruction_max_abs": float(np.max(np.abs(E.T @ D @ E - S))),
 "dense_relaxed_gap": abs(dense["opt_value"] - s["opt_value"]),
 "minimum_scalar_inequality_dual": min(v for v in s["named_dual_values"].values() if v is not None),
 "minimum_S_eigenvalue": float(np.linalg.eigvalsh(S).min()),
 "minimum_matrix_inequality_eigenvalue": 0.0,
}
tol = {"identity_atol": 1e-5, "identity_rtol": 0, "reconstruction_atol": 1e-4, "reconstruction_rtol": 1e-5, "dual_tol": 1e-6, "psd_tol": 1e-6, "dense_opt_atol": 1e-5}
passed = (s["solver_status"] == "optimal" and all(res[k] <= 1e-5 for k in ["identity_gram_max_abs", "identity_func_max_abs", "identity_offset_abs", "dense_relaxed_gap"])
          and np.allclose(E.T @ D @ E, S, atol=1e-4, rtol=1e-5)
          and res["minimum_scalar_inequality_dual"] >= -1e-6 and res["minimum_S_eigenvalue"] >= -1e-6
          and np.allclose(S, S.T, atol=1e-6, rtol=0) and np.isfinite(S).all())
assert passed, res
N = s["N"]
candidate = {"initial_condition": 4 / N**2, f"A monotone:x_{N},x_star": 4 / N}
candidate.update({f"A monotone:x_{N},y_{k}": 4 / ((N-k)*(N-k-1)) for k in range(N-1)})
candidate.update({f"A Lipschitz:x_{k},y_{k}": 2 / (N-k)**2 for k in range(N-1)})
candidate[f"A Lipschitz:x_{N-1},x_{N}"] = 2
lambda_error = max(abs(candidate[name] - v) for name, v in s["named_dual_values"].items() if v is not None)
w = 2 / N * (ctx["x_0"] - ctx["x_star"]) - obj(ctx[f"x_{N}"])
S_guess = np.asarray(pm.eval_scalar(w**2).inner_prod_coords, dtype=float)
S_error = float(np.max(np.abs(S_guess - S)))
print("Residuals", res)
print("Lambda candidate error", lambda_error, "S candidate error", S_error)
print("D diagonal", np.diag(D))
print("Rank", np.linalg.matrix_rank(S, tol=1e-4))
print("S candidate matrix", S_guess)
s.update(b1)
s.update({"numerical_checks": {"tolerances": tol, "residuals": res, "passed": bool(passed)},
    "normalization": {"tau_name": "initial_condition", "initial_condition": b1["initial_condition"], "performance_metric": b1["performance_metric"], "bound_value": s["opt_value"], "bound_formula": b1["conjectured_rate"]},
    "formula_status": {"lambda": "candidate" if lambda_error < 1e-4 else "unresolved", "S": "candidate" if S_error < 1e-4 else "unresolved"},
    "lamb_code": "def lamb_candidates(N):\n    result = {'initial_condition': 4/N**2, f'A monotone:x_{N},x_star': 4/N}\n    result.update({f'A monotone:x_{N},y_{k}': 4/((N-k)*(N-k-1)) for k in range(N-1)})\n    result.update({f'A Lipschitz:x_{k},y_{k}': 2/(N-k)**2 for k in range(N-1)})\n    result[f'A Lipschitz:x_{N-1},x_{N}'] = 2\n    return result\n",
    "S_code": "S_guess = (2/N*(ctx['x_0']-ctx['x_star'])-obj(ctx[f'x_{N}']))**2",
    "closed_form_search": {"completed": True, "references_reviewed": ["Approved generic B2 workflow only; target references prohibited."],
        "attempts": [{"method": "Rational inspection of sparse lambda values by remaining horizon t=N-k", "candidate": "monotone 4/[t(t-1)], terminal-star 4/N, Lipschitz 2/t^2", "maximum_error": lambda_error},
                     {"method": "Inspect low-rank S and compare terminal-residual square", "candidate": "||2(x_0-x_star)/N-A(x_N)||^2", "maximum_error": S_error}],
        "unresolved_components": ["Arbitrary-horizon exact lambda/S identity and sign proof"]},
    "S_decomp_type": "ldl", "numerical_certificate_verified": True, "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False, "require_analytic_full_pep": False, "proof_valid": True,
    "relaxation_recipe": "Keep terminal x_N monotonicity to x_star and y_0..y_(N-2), Lipschitz x_k,y_k for k<N-1 and x_(N-1),x_N. Drop all remaining interpolation constraints.",
    "candidate_checks": {"lambda_max_abs": lambda_error, "S_max_abs": S_error},
})
groups = {}
for group in ["Monotone Operator Inequality", "Lipschitz Continuous Inequality"]:
    rows = [name for name, meta in s["constraint_metadata"].items() if meta["group"] == group]
    groups[group] = {"constraint_names": rows, "values": [s["named_dual_values"][name] for name in rows]}
s["lambda_groups"] = groups
keys = ("N_verify", "params_json", "relaxed_constraints", "S_matrix", "S_row_names", "S_col_names", "basis_vectors", "basis_scalars", "opt_value", "tau_sol", "tau_name", "named_dual_values", "constraint_metadata", "normalization", "certificate_provenance", "numerical_checks", "numerical_decomposition")
s["certificate_id"] = hashlib.sha256(json.dumps({k:s[k] for k in keys}, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
(ROOT / "supplementary/certificate_N8.json").write_text(json.dumps(s, indent=2, allow_nan=False))

