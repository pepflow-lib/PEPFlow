"""Validate structure at both available horizons and save the selected B4 state."""

import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "supplementary"), str(ROOT / "supplementary/helpers")]
import numpy as np  # noqa: E402
import run_b1  # noqa: E402,F401
from basis_structure import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    basis_for,
    basis_labels_for,
    coeff_pattern,
    numerical_structure,
    reconstruct_all,
)
from dual_feg_setup import get_pep_setup  # noqa: E402
from grouping import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    build_partial_sums,
    full_psd_piece,
    replay_certificate,
)

import pepflow as pf  # noqa: E402

b3 = json.loads((ROOT / "state/dual_feg_b3.json").read_text())
discovery = json.loads((ROOT / "supplementary/b4-discovery.json").read_text())
fit_samples = []
main_coefficients = main_checks = None
for cert_path, dense_path in [
    ("state/dual_feg_b3.json", "state/dual_feg_dense.json"),
    ("supplementary/b2-N6.json", "supplementary/b2-N6-dense.json"),
]:
    cert = json.loads((ROOT / cert_path).read_text())
    dense = json.loads((ROOT / dense_path).read_text())
    replay_certificate(cert, get_pep_setup, ROOT, dense["opt_value"])
    ctx, pb, _ = get_pep_setup(cert["N_verify"], json.loads(cert["params_json"]))
    pm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(cert["params_json"]))
    S_scalar, pieces = full_psd_piece(cert, ctx, pm)
    lyap, observation = build_partial_sums(cert, ctx, pb, pm, S_scalar, pieces)
    cached = (
        {
            int(k): np.asarray(v["adopted_coefficients"], dtype=float).reshape(
                (0, 0) if int(k) == 0 else (2, 2) if int(k) == 4 else (4, 4)
            )
            for k, v in discovery.items()
        }
        if cert["N_verify"] == 4
        else None
    )
    coefficients, checks, errors = reconstruct_all(cert, ctx, pm, lyap, cached)
    fit_samples.append(
        dict(
            N=cert["N_verify"],
            certificate_id=cert["certificate_id"],
            checks=checks,
            formula_errors=errors,
            coefficients={str(k): c.tolist() for k, c in coefficients.items()},
        )
    )
    if cert["N_verify"] == b3["N_verify"]:
        main_coefficients, main_checks = coefficients, checks
assert main_coefficients is not None and main_checks is not None
basis_code = inspect.getsource(basis_for) + "\n" + inspect.getsource(basis_labels_for)
basis_code += "\ndef V_k_basis(k):\n    return basis_for(ctx, k, N_int)\ndef V_k_basis_labels(k):\n    return basis_labels_for(k, N_int)\n"
structure_code = (
    inspect.getsource(numerical_structure)
    + "\ndef V_k_structure(k):\n    return numerical_structure(ctx, k, N_int, coeff_by_k)\n"
)
state = {
    **b3,
    "basis_templates": {
        "initial": [],
        "interior": ["A(x_N)", "x_0-x_N", "x_k-x_N", "z_k"],
        "terminal": ["A(x_N)", "x_0-x_N"],
    },
    "basis_code": basis_code,
    "structure_code": structure_code,
    "coeff_by_k": {str(k): C.tolist() for k, C in main_coefficients.items()},
    "coeff_code": inspect.getsource(coeff_pattern),
    "coefficient_formula_status": "candidate",
    "expression_structure": {
        "quadratic_convention": "sum_ij C_ij <v_i,v_j>, symmetric C, off-diagonal counted twice",
        "interior": {
            "index_domain": "1 <= k <= N-1",
            "basis_labels": ["A(x_N)", "x_0-x_N", "x_k-x_N", "z_k"],
            "coefficient_candidate": "C01=-2L/N; C02=2L/(N-k); C03=-2; C23=2L/(N-k); C33=-2; all other independent entries zero",
        },
        "initial": {
            "index_domain": "k=0",
            "basis_labels": [],
            "coefficient_candidate": "V_0=0",
        },
        "terminal": {
            "index_domain": "k=N",
            "basis_labels": ["A(x_N)", "x_0-x_N"],
            "coefficient_candidate": "C00=2; C01=-2L/N; C11=0",
        },
        "function_terms": [],
        "constant_terms": [],
    },
    "unresolved_coefficients": [],
    "remaining_analytic_obligations": [
        "Prove candidate coefficient identities for arbitrary horizons and positive L; verify step, base, terminal and rate normalization"
    ],
    "numerical_reconstruction": main_checks,
    "coefficient_fit_evidence": "supplementary/b4-two-horizon-reconstruction.json",
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(ROOT / "supplementary/b4-two-horizon-reconstruction.json").write_text(
    json.dumps(fit_samples, indent=2)
)
(ROOT / "state/dual_feg_b4.json").write_text(
    json.dumps(state, indent=2, allow_nan=False)
)
print("B4 complete numerical structure saved; analytic formulas remain candidates")
