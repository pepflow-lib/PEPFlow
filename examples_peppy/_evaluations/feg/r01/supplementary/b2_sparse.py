"""Sparsity selection, candidate formulas, and complete certificate checks."""
import fractions
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pepflow as pf
import sympy as sp
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

from certificate_tools import capture, check_saved, source_hashes
from feg_setup import get_pep_setup

root = Path.cwd()
b1 = json.loads((root / "state/feg_b1.json").read_text())
n = int(sys.argv[1]) if len(sys.argv) > 1 else b1["N_verify"]
b1["N_verify"] = n
out_dir = root / "supplementary" / f"sample-N{n}" if len(sys.argv) > 1 else root / "state"
out_dir.mkdir(exist_ok=True)
params: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.S(1), "R": sp.S(1)}
hashes = source_hashes(root)
if len(sys.argv) > 1:
    dense_ctx, dense_pb, dense_obj = get_pep_setup(n, params)
    dense, _, _ = capture(dense_ctx, dense_pb, dense_obj, params)
    dense["N"] = n
    dense["certificate_provenance"]["source_hashes"] = hashes
    (out_dir / "feg_dense.json").write_text(json.dumps(dense, indent=2))
else:
    dense = json.loads((root / "state/feg_dense.json").read_text())
ctx, pb, obj = get_pep_setup(n, params)
support = {"initial_condition", f"A monotone:x_{n},x_star", "A Lipschitz:x_0,x_1"}
support.update(f"A monotone:x_{k},x_{k+1}" for k in range(1,n))
support.update(f"A Lipschitz:x_{k},x_{2*k-1}/2" for k in range(2,n+1))
relaxed = [name for name in dense["named_dual_values"] if name not in support]
pb.set_relaxed_constraints(relaxed)
state, result, sm = capture(ctx, pb, obj, params)
state.update({**b1, **state})
state["N"] = n
state["certificate_provenance"]["source_hashes"] = hashes
checks, residual = check_saved(ctx, pb, state, params, dense["opt_value"])
pm = pf.ExpressionManager(ctx, resolve_parameters=params)
basis = ctx.basis_vectors()
D, ell = ldl_decompose_with_reversed_basis(sm, basis, print_output=False)
E = np.asarray([pm.eval_vector(v).coords for v in ell], float)
s = np.asarray(sm.matrix, float)
checks["residuals"]["S_reconstruction_max_abs"] = float(np.max(np.abs(E.T @ D @ E - s)))
checks["tolerances"] = dict(identity_atol=1e-5, identity_rtol=0, reconstruction_atol=1e-4,
                             reconstruction_rtol=1e-5, dual_tol=1e-6, psd_tol=1e-6, dense_opt_atol=1e-5)
checks["passed"] &= bool(np.allclose(E.T @ D @ E, s, atol=1e-4, rtol=1e-5))
state["numerical_decomposition"] = dict(method="reverse_ldl", D=D.tolist(), ell_coords=E.tolist(), basis_labels=state["basis_vectors"])
candidate = {name: 0.0 for name in state["named_dual_values"]}
candidate["initial_condition"] = 4/n**2
for k in range(1, n):
    candidate[f"A monotone:x_{k},x_{k+1}"] = 4*k*(k+1)/n**2
candidate[f"A monotone:x_{n},x_star"] = 4/n
candidate["A Lipschitz:x_0,x_1"] = 2/n**2
for k in range(2, n+1):
    candidate[f"A Lipschitz:x_{k},x_{2*k-1}/2"] = 2*k*k/n**2
lambda_error = max(abs(candidate[name] - (value or 0)) for name, value in state["named_dual_values"].items())
guess_vector = obj(ctx[f"x_{n}"]) - 2/n * (ctx["x_0"]-ctx["x_star"])
guess = pm.eval_scalar(guess_vector**2)
s_error = float(np.max(np.abs(np.asarray(guess.inner_prod_coords, float)-s)))
state["candidate_named_dual_values"] = candidate
state["candidate_checks"] = {"lambda_max_abs": lambda_error, "lambda_passed": lambda_error <= 1e-4,
                              "S_gram_max_abs": s_error, "S_func_max_abs": float(np.max(np.abs(guess.func_coords), initial=0)),
                              "S_offset_abs": float(abs(guess.offset)), "S_passed": s_error <= 1e-4}
state["lamb_code"] = "def lamb_candidate(n):\n    values = {'initial_condition': 4/n**2, f'A monotone:x_{n},x_star': 4/n}\n    values.update({f'A monotone:x_{k},x_{k+1}': 4*k*(k+1)/n**2 for k in range(1,n)})\n    values['A Lipschitz:x_0,x_1'] = 2/n**2\n    values.update({f'A Lipschitz:x_{k},x_{2*k-1}/2': 2*k*k/n**2 for k in range(2,n+1)})\n    return values"
state["S_code"] = "S_guess = (obj(ctx[f'x_{N_int}']) - 2/N_int*(ctx['x_0']-ctx['x_star']))**2"
state["formula_status"] = {"lambda": "candidate" if lambda_error <= 1e-4 else "unresolved", "S": "candidate" if s_error <= 1e-4 else "unresolved"}
state["closed_form_search"] = {
    "completed": True, "references_reviewed": ["Approved generic framework and B2 workflow; target references prohibited by clean-room policy"],
    "attempts": ["Dense lambda threshold 1e-6 identifies adjacent monotonicity and per-step Lipschitz support; fresh sparse solve.",
                 "Rationalized active sparse multipliers; tested quadratic index formulas and terminal coefficient.",
                 "Rank-one dominant S suggested ||A(x_N)-2(x_0-x_star)/N||²; compared all components to same sparse S; retained full reverse LDL including numerical small components."],
    "candidate_checks": state["candidate_checks"],
    "unresolved_components": ["Arbitrary-horizon and general-L analytic validity of candidate formulas"]}
state["normalization"] = dict(tau_name="initial_condition", initial_condition=b1["initial_condition"],
                             performance_metric=b1["performance_metric"], bound_value=state["opt_value"], bound_formula=b1["conjectured_rate"])
state["numerical_checks"] = checks
state["S_decomp_type"] = "ldl"
state["numerical_certificate_verified"] = checks["passed"]
state["analytic_full_pep_verified"] = False
state["lyapunov_proof_verified"] = False
state["require_analytic_full_pep"] = False
state["proof_valid"] = checks["passed"]
assert checks["passed"], checks
assert abs(state["opt_value"] - 4/n**2) < 1e-5
assert hashes == source_hashes(root)
certificate_keys = ('N_verify', 'params_json', 'relaxed_constraints', 'S_matrix', 'S_row_names',
    'S_col_names', 'basis_vectors', 'basis_scalars', 'opt_value', 'tau_sol', 'tau_name',
    'named_dual_values', 'constraint_metadata', 'normalization', 'certificate_provenance',
    'numerical_checks', 'numerical_decomposition')
state["certificate_id"] = hashlib.sha256(json.dumps({key: state[key] for key in certificate_keys}, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
for filename in ("feg_b2.json", "feg_relaxed.json"):
    (out_dir / filename).write_text(json.dumps(state, indent=2, allow_nan=False))
print("Checks", json.dumps(checks))
print("Candidates", json.dumps(state["candidate_checks"]))
print("LDL diagonal", np.diag(D))
for name, value in state["named_dual_values"].items():
    if value is not None:
        print(name, value, fractions.Fraction(value).limit_denominator(1000))
