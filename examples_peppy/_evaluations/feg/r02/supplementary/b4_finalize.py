import runpy
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ns = runpy.run_path(str(root / "supplementary/b4_trial.py"))
import json  # noqa: E402 - imports follow runtime or notebook setup

b3 = ns["b3"]
case = lambda domain, names: dict(  # noqa: E731 - retain the archived notebook helper
    index_domain=domain,
    basis_labels=["A(x_k)", "x_k-x_0"],
    quadratic_coefficients={
        "C[0,0]": names[0] + "(k,N,L)",
        "C[0,1]=C[1,0]": names[1] + "(k,N,L)",
        "C[1,1]": names[2] + "(k,N,L)",
    },
)
structure = dict(
    quadratic_convention="V_quadratic = sum_{i,j} C_ij * <v_i,v_j>; symmetric C, off-diagonal terms counted twice",
    interior=case("1 <= k <= N-1; a=b=1", ("c00", "c01", "c11")),
    initial=dict(
        index_domain="k=0", basis_labels=[], quadratic_coefficients={}, formula="V_0=0"
    ),
    terminal=case("k=N", ("d00", "d01", "d11")),
    function_terms=[],
    constant_terms=[],
)
unknowns = [
    dict(
        name=prefix + suffix,
        arguments=["k", "N", "L"],
        role=role + ".C" + entry,
        index_domain=domain,
    )
    for prefix, role, domain in [
        ("c", "interior", "1 <= k <= N-1"),
        ("d", "terminal", "k=N"),
    ]
    for suffix, entry in [("00", "[0,0]"), ("01", "[0,1] = C[1,0]"), ("11", "[1,1]")]
]
basis_source = (
    (root / "supplementary/b4_basis.py")
    .read_text(encoding="utf-8-sig")
    .split("\nfor k in range(N_int+1):")[0]
)
state = {
    **b3,
    "basis_templates": dict(
        initial=[], interior=["A(x_k)", "x_k-x_0"], terminal=["A(x_N)", "x_N-x_0"]
    ),
    "basis_code": basis_source,
    "structure_code": (root / "supplementary/b4_structure.py").read_text(
        encoding="utf-8-sig"
    ),
    "coeff_by_k": {str(k): C.tolist() for k, C in ns["coeff_by_k"].items()},
    "coeff_code": None,
    "coefficient_formula_status": "unresolved",
    "expression_structure": structure,
    "unresolved_coefficients": unknowns,
    "numerical_reconstruction": dict(
        certificate_id=b3["certificate_id"],
        required_indices=ns["required_indices"],
        quadratic_residuals={str(k): v for k, v in ns["coefficient_residuals"].items()},
        component_residuals=ns["component_residuals"],
        tolerances=dict(
            indep_tol=1e-7, span_tol=1e-5, component_atol=1e-4, component_rtol=1e-5
        ),
        passed=True,
    ),
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(root / "state/feg_b4.json").write_text(json.dumps(state, indent=2))
(root / "supplementary/b4-search-results.json").write_text(
    json.dumps(ns["search_results"], indent=2)
)
print("B4 state saved")
