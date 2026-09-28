# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np
import runtime
import sympy as sp
from bppm_setup import get_pep_setup

notebook_dir = runtime.ATTEMPT
certificate = json.loads((notebook_dir / "state/bppm_b3.json").read_text())
N_int = certificate["N_verify"]
params_sp = {k: sp.S(v) for k, v in json.loads(certificate["params_json"]).items()}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(compile(certificate[field], field, "exec"), globals())


def max_abs(value):
    return float(np.max(np.abs(np.asarray(value, dtype=float)), initial=0.0))


for name in (
    "b4_candidates.py",
    "b4_filter.py",
    "b4_search.py",
    "b4_basis.py",
    "b4_coefficients.py",
    "b4_structure.py",
    "b4_fit.py",
):
    exec(
        compile(
            (notebook_dir / "supplementary" / name).read_text(encoding="utf-8-sig"),
            name,
            "exec",
        ),
        globals(),
    )


def read_source(name):
    return (notebook_dir / "supplementary" / name).read_text(encoding="utf-8-sig")


basis_code = read_source("b4_basis.py")
structure_code = (
    "function_samples = "
    + repr(function_samples)
    + "\n"
    + read_source("b4_structure.py").split("\n\nfor k in required_indices:")[0]
)
coeff_code = read_source("b4_fit.py").split("\n\nfit_residuals=")[0]
expression_structure = {
    "quadratic_convention": "sum_ij C_ij <v_i,v_j>; symmetric C; off-diagonal entries counted twice",
    "interior": {
        "index_domain": "1 <= k <= N-1 (a=b=1)",
        "basis_labels": ["x_0-x_star", "grad_h(x_0)", "x_k-x_star", "grad_h(x_k)"],
        "coefficients": "candidate C01=C10=-1/(2 alpha N), C23=C32=1/(2 alpha N); all others zero",
    },
    "initial": {
        "index_domain": "k=0",
        "basis_labels": [],
        "coefficients": "empty 0x0 matrix; V_0=0",
    },
    "terminal": {
        "index_domain": "k=N",
        "basis_labels": ["x_0-x_star", "grad_h(x_0)", "x_N-x_star", "grad_h(x_N)"],
        "coefficients": "same candidate matrix as interior; applies also to N=1",
    },
    "function_terms": [
        {
            "expression": "h(x_0)-h(x_k)",
            "coefficient": "candidate 1/(alpha N)",
            "index_domain": "1 <= k <= N",
        },
        {
            "expression": "f(x_k)-f(x_star)",
            "coefficient": "candidate k/N",
            "index_domain": "1 <= k <= N",
        },
    ],
    "constant_terms": [],
}
state = {
    **b3,
    "basis_templates": {
        "interior": expression_structure["interior"],
        "initial": expression_structure["initial"],
        "terminal": expression_structure["terminal"],
    },
    "basis_code": basis_code,
    "structure_code": structure_code,
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": coeff_code,
    "coefficient_formula_status": "candidate",
    "expression_structure": expression_structure,
    "unresolved_coefficients": [],
    "function_samples": function_samples,
    "candidate_fit_residuals": fit_residuals,
    "numerical_reconstruction": {
        "certificate_id": b3["certificate_id"],
        "required_indices": required_indices,
        "quadratic_residuals": {str(k): v for k, v in coefficient_residuals.items()},
        "component_residuals": component_residuals,
        "tolerances": {
            "indep_tol": 1e-7,
            "span_tol": 1e-5,
            "component_atol": 1e-4,
            "component_rtol": 1e-5,
        },
        "passed": True,
    },
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(notebook_dir / "state/bppm_b4.json").write_text(
    json.dumps(state, indent=2, allow_nan=False)
)
(notebook_dir / "supplementary/b4_basis_search.json").write_text(
    json.dumps(search_results, indent=2)
)
print("B4 state saved")
