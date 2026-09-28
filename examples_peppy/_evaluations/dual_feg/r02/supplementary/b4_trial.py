# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime", root / "supplementary/helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import dual_feg_setup as setup  # noqa: E402 - imports follow runtime or notebook setup
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup

notebook_dir = root
REPO_ROOT = runtime.REPO_ROOT
certificate = json.loads((root / "state/dual_feg_b3.json").read_text())
N_int = certificate["N_verify"]
N = sp.Integer(N_int)
params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.Integer(1), "R": sp.Integer(1)}
ctx, pb, obj = setup.get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(certificate[field])
for filename in ("b4_scan.py", "b4_search.py", "b4_basis.py", "b4_coefficients.py"):
    exec((root / "supplementary" / filename).read_text(encoding="utf-8-sig"))
print({k: np.round(C, 7).tolist() for k, C in coeff_by_k.items()})
(root / "supplementary/b4-search-results.json").write_text(
    json.dumps(
        {
            "search_results": search_results,
            "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
            "residuals": coefficient_residuals,
        },
        indent=2,
    )
)

for filename in ("b4_formula.py", "b4_structure.py"):
    exec((root / "supplementary" / filename).read_text(encoding="utf-8-sig"))
expression_structure = {
    "quadratic_convention": "V_quadratic = sum_{i,j} C_ij <v_i,v_j>; C symmetric, off-diagonal counted twice",
    "interior": {
        "index_domain": "1 <= k <= N-1; exclusions a=b=1",
        "basis_labels": ["g_N", "z_k", "x_k-x_0", "x_N-x_0"],
        "coefficients": {
            "C00": "0",
            "C01": "-2",
            "C02": "2/(N-k)",
            "C03": "-2*k/(N*(N-k))",
            "C11": "-2",
            "C12": "2/(N-k)",
            "C13": "-2/(N-k)",
            "C22": "0",
            "C23": "0",
            "C33": "0",
        },
        "status": "candidate at L=1",
    },
    "initial": {
        "index_domain": "k=0",
        "basis_labels": [],
        "coefficients": {},
        "status": "V0=0 by definition",
    },
    "terminal": {
        "index_domain": "k=N",
        "basis_labels": ["g_N", "x_N-x_0"],
        "coefficients": {"C00": "2", "C01": "2/N", "C11": "0"},
        "status": "candidate at L=1; N=1 remains for B5 boundary proof",
    },
    "function_terms": [],
    "constant_terms": [],
}
state = {
    **b3,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "basis_templates": {
        "interior": ["g_N", "z_k", "x_k-x_0", "x_N-x_0"],
        "initial": [],
        "terminal": ["g_N", "x_N-x_0"],
    },
    "basis_code": (root / "supplementary/b4_basis.py").read_text(encoding="utf-8-sig"),
    "structure_code": (root / "supplementary/b4_structure.py")
    .read_text(encoding="utf-8-sig")
    .split("component_residuals=")[0],
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": (root / "supplementary/b4_formula.py")
    .read_text(encoding="utf-8-sig")
    .split("coefficient_formula_errors=")[0],
    "coefficient_formula_status": "candidate",
    "coefficient_formula_errors": coefficient_formula_errors,
    "expression_structure": expression_structure,
    "unresolved_coefficients": [],
    "numerical_reconstruction": {
        "certificate_id": b3["certificate_id"],
        "required_indices": required_indices,
        "quadratic_residuals": {str(k): v for k, v in coefficient_residuals.items()},
        "component_residuals": component_residuals,
        "tolerances": {
            **extraction_tolerances,
            "component_atol": 1e-4,
            "component_rtol": 1e-5,
        },
        "passed": True,
    },
    "basis_search": search_results,
}
(root / "state/dual_feg_b4.json").write_text(
    json.dumps(state, indent=2, allow_nan=False)
)
