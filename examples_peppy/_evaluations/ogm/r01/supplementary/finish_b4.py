# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "supplementary/helpers"))
import runtime  # noqa: E402, F401 -- Initialize approved paths and runtime settings before exec fragments. Paths initialized above.

# Preserve the recorded import initialization order.
# isort: split
import json  # noqa: E402 - imports follow runtime or notebook setup

certificate = json.loads((root / "state/ogm_b3.json").read_text())
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(compile(certificate[field], field, "exec"))
sources = {
    name: (root / "supplementary" / name).read_text(encoding="utf-8-sig")
    for name in (
        "b4_basis.py",
        "b4_coefficients.py",
        "b4_structure.py",
        "b4_coeff_candidate.py",
    )
}
for name, source in sources.items():
    exec(compile(source, name, "exec"))
structure_code = (
    "function_sample_coefficients = "
    + repr(function_sample_coefficients)
    + "\n"
    + sources["b4_structure.py"]
)
expression_structure = dict(
    quadratic_convention="sum_ij C_ij <v_i,v_j>, C symmetric and off-diagonal counted twice",
    interior=dict(
        index_domain="1 <= k <= N-1",
        basis_labels=["x_0-x_star", "g_k", "z_{k+1}-x_star"],
        coefficients="candidate diag(-1/(2 theta_N^2), -theta_k^2/theta_N^2, 1/(2 theta_N^2)), L=1",
    ),
    initial=dict(
        index_domain="k=0", basis_labels=[], coefficients="empty matrix; V_0=0"
    ),
    terminal=dict(
        index_domain="k=N",
        basis_labels=["x_0-x_star", "z_N-x_star-theta_N*g_N"],
        coefficients="candidate diag(-1/(2 theta_N^2), 1/(2 theta_N^2)), L=1",
    ),
    function_terms=[
        dict(
            index_domain="1 <= k < N",
            expression="f(x_k)-f_star",
            coefficient="candidate 2 theta_k^2/theta_N^2",
        ),
        dict(index_domain="k=N", expression="f(x_N)-f_star", coefficient="candidate 1"),
    ],
    constant_terms=[],
)
state = {
    **certificate,
    "basis_templates": {
        "interior": expression_structure["interior"],
        "initial": expression_structure["initial"],
        "terminal": expression_structure["terminal"],
    },
    "basis_code": sources["b4_basis.py"],
    "structure_code": structure_code,
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": sources["b4_coeff_candidate.py"],
    "coefficient_formula_status": "candidate",
    "expression_structure": expression_structure,
    "unresolved_coefficients": [],
    "numerical_reconstruction": dict(
        certificate_id=certificate["certificate_id"],
        required_indices=required_indices,
        quadratic_residuals={str(k): v for k, v in coefficient_residuals.items()},
        component_residuals=component_residuals,
        tolerances=dict(
            indep_tol=1e-7, span_tol=1e-5, component_atol=1e-4, component_rtol=1e-5
        ),
        passed=True,
    ),
    "formula_residuals": formula_residuals,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(root / "state/ogm_b4.json").write_text(json.dumps(state, indent=2, allow_nan=False))
print("B4 state saved; formulas remain candidates.")
