# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

from bppm_setup import get_pep_setup

# local helper resolved by the notebook runtime path
from runtime import ATTEMPT  # ty: ignore[unresolved-import]

# Preserve the recorded import initialization order.
# isort: split
from bppm_setup import (  # noqa: F401 -- Required by exec of bppm_b3.json#certificate_check_code.
    f,
    h,
)

notebook_dir = ATTEMPT
b3 = json.loads((ATTEMPT / "state/bppm_b3.json").read_text())
certificate = b3
ctx, pb, obj = get_pep_setup(b3["N_verify"], {})
pb.set_relaxed_constraints(b3["relaxed_constraints"])
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(compile(b3[field], f"<B3-{field}>", "exec"), globals())
assert certificate_checked and grouping_checked
content = json.loads((ATTEMPT / "supplementary/b4_cells.json").read_text())
for i, cell in enumerate(content):
    if cell["kind"] == "code":
        exec(compile(cell["source"], f"<B4-cell-{i}>", "exec"), globals())
basis_code = content[8]["source"].split("\nfor k in range")[0]
structure_source = content[10]["source"]
structure_function = structure_source[
    structure_source.index("def V_k_structure") : structure_source.index(
        "\nfor k in range(N_int+1):\n    delta"
    )
]
structure_code = (
    "function_coefficients = " + repr(function_coefficients) + "\n" + structure_function
)
coeff_code = content[11]["source"].split("\ncoefficient_fit_errors")[0]
labels = [
    "q_k=grad h(x_0)-grad h(x_k)",
    "p_k=x_star-x_k",
    "r_k=x_k-x_0",
    "t=grad h(x_0)",
]
case = {
    "basis_labels": labels,
    "coefficients": {
        "C_01=C_10": "1/(2*alpha*N)",
        "C_23=C_32": "1/(2*alpha*N)",
        "other entries": "0",
    },
}
state = {
    **b3,
    "basis_templates": {"interior": labels, "initial": [], "terminal": labels},
    "basis_code": basis_code,
    "structure_code": structure_code,
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": coeff_code,
    "coefficient_formula_status": "candidate",
    "expression_structure": {
        "quadratic_convention": "sum_ij C_ij <v_i,v_j>; symmetric C; off-diagonal entries count twice",
        "interior": {**case, "index_domain": "1 <= k <= N-1 (a=b=1)"},
        "initial": {"index_domain": "k=0", "basis_labels": [], "coefficients": {}},
        "terminal": {**case, "index_domain": "k=N >= 1"},
        "function_terms": [
            {
                "term": "f(x_k)-f(x_star)",
                "coefficient": "k/N",
                "index_domain": "1<=k<=N",
            },
            {
                "term": "h(x_k)-h(x_0)",
                "coefficient": "-1/(alpha*N)",
                "index_domain": "1<=k<=N",
            },
        ],
        "constant_terms": [],
    },
    "unresolved_coefficients": [],
    "function_coefficients": function_coefficients,
    "candidate_fit_errors": coefficient_fit_errors,
    "basis_search": search_results,
    "numerical_reconstruction": {
        "certificate_id": b3["certificate_id"],
        "required_indices": list(range(b3["N_verify"] + 1)),
        "quadratic_residuals": coefficient_residuals,
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
exec(compile(structure_code, "<B4-structure-replay>", "exec"), globals())
for k in range(b3["N_verify"] + 1):
    delta = pm.eval_scalar(V_k_structure(k) - lyap[k])
    assert (
        max(
            max_abs(delta.inner_prod_coords),
            max_abs(delta.func_coords),
            max_abs(delta.offset),
        )
        <= 1e-4
    )
(ATTEMPT / "state/bppm_b4.json").write_text(json.dumps(state, indent=2))
print("B4 selected-sample reconstruction complete.")
