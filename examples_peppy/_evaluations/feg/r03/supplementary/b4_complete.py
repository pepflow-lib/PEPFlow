# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
import sympy as sp
from feg_setup import get_pep_setup

ROOT = runtime.ROOT
REPO_ROOT = ROOT / "supplementary/approved"
notebook_dir = ROOT
b3 = json.loads((ROOT / "state/feg_b3.json").read_text())
certificate = b3
N_int = b3["N_verify"]
params_sp = {k: sp.S(v) for k, v in json.loads(b3["params_json"]).items()}
ctx, pb, obj = get_pep_setup(sp.S(N_int), params_sp)
pb.set_relaxed_constraints(b3["relaxed_constraints"])
ctx.set_as_current()
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(b3[field])
assert ranks == b3["rank_profile"]
evidence = json.loads((ROOT / b3["rank_search"]["evidence_path"]).read_text())
assert evidence["summary"] == b3["rank_search"]
for k, v in enumerate(lyap):
    current = pm.eval_scalar(v)
    assert np.allclose(
        current.inner_prod_coords, b3["lyap_inner_prod_coords"][k], atol=1e-4, rtol=1e-5
    )
    assert np.allclose(
        current.func_coords, b3["lyap_func_coords"][k], atol=1e-4, rtol=1e-5
    )
    assert abs(float(current.offset) - b3["lyap_offsets"][k]) < 1e-4
sources = {
    name: (ROOT / f"supplementary/b4_{name}.py").read_text(encoding="utf-8-sig")
    for name in (
        "scan",
        "search",
        "basis",
        "coefficients",
        "structure",
        "fit",
        "components",
    )
}
for name in sources:
    exec(sources[name])
expression_structure = dict(
    quadratic_convention="sum_ij C_ij <v_i,v_j>, symmetric C with cross entries counted twice",
    interior=dict(
        index_domain="1 <= k <= N-1",
        basis_labels=["g_k=A(x_k)", "x_k-x_0"],
        coefficients={
            "C00": "2*k**2/N**2 (candidate)",
            "C01=C10": "2*k*L/N**2 (candidate)",
            "C11": "0 (candidate)",
        },
    ),
    initial=dict(
        index_domain="k=0", basis_labels=[], coefficients={}, expression="V0=0"
    ),
    terminal=dict(
        index_domain="k=N",
        basis_labels=["g_N=A(x_N)", "x_N-x_0"],
        coefficients={
            "C00": "2 (candidate)",
            "C01=C10": "2*L/N (candidate)",
            "C11": "0 (candidate)",
        },
    ),
    function_terms=[],
    constant_terms=[],
)
state = {
    **b3,
    "basis_templates": {
        "initial": [],
        "interior": ["A(x_k)", "x_k-x_0"],
        "terminal": ["A(x_N)", "x_N-x_0"],
    },
    "basis_code": sources["basis"],
    "structure_code": sources["structure"],
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": sources["fit"].split("formula_residuals=")[0],
    "coefficient_formula_status": "candidate",
    "expression_structure": expression_structure,
    "unresolved_coefficients": [],
    "coefficient_formula_checks": formula_residuals,
    "numerical_reconstruction": dict(
        certificate_id=b3["certificate_id"],
        required_indices=required_indices,
        quadratic_residuals=coefficient_residuals,
        component_residuals=component_residuals,
        tolerances={
            **extraction_tolerances,
            "component_atol": 1e-4,
            "component_rtol": 1e-5,
        },
        passed=True,
    ),
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(ROOT / "state/feg_b4.json").write_text(json.dumps(state, indent=2, allow_nan=False))
(ROOT / "supplementary/b4-search.json").write_text(
    json.dumps(
        dict(
            candidate_count=len(candidates),
            search_basis={
                str(k): [label_by_id[id(v)] for v in bs]
                for k, bs in search_basis_by_k.items()
            },
            search_coefficients={
                str(k): C.tolist() for k, C in search_coeff_by_k.items()
            },
            adopted_basis_reason="Use residual g_k and anchor gap x_k-x0 consistently across all positive indices; independent reconstruction verified",
            independence=independence,
        ),
        indent=2,
    )
)
