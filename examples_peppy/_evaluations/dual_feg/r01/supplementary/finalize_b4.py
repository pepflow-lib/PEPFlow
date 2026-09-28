# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import runtime

notebook_dir = runtime.ATTEMPT
p = notebook_dir / "supplementary/run_b4_scan.py"
exec(compile(p.read_text(encoding="utf-8-sig"), str(p), "exec"))
for file in ["b4_basis.py", "b4_coefficients.py", "b4_structure.py"]:
    p = notebook_dir / "supplementary" / file
    exec(compile(p.read_text(encoding="utf-8-sig"), str(p), "exec"))
component_residuals = {}
for k in required_indices:
    diff = pm.eval_scalar(V_k_structure(k) - lyap[k])
    target = pm.eval_scalar(lyap[k])
    errors = {}
    for name, value, target_value in [
        ("gram", diff.inner_prod_coords, target.inner_prod_coords),
        ("function", diff.func_coords, target.func_coords),
        ("offset", diff.offset, target.offset),
    ]:
        a = np.asarray(value, dtype=float)
        error = float(np.max(np.abs(a), initial=0))
        scale = float(np.max(np.abs(np.asarray(target_value, dtype=float)), initial=0))
        assert error <= 1e-4 + 1e-5 * scale
        errors[name] = error
    component_residuals[str(k)] = errors
unknowns = [
    {
        "name": f"c_{i}{j}",
        "arguments": ["k", "N", "L"],
        "role": f"interior.C[{i},{j}] = interior.C[{j},{i}]",
        "index_domain": "1 <= k <= N-1",
    }
    for i in range(4)
    for j in range(i, 4)
]
unknowns += [
    {
        "name": f"t_{i}{j}",
        "arguments": ["N", "L"],
        "role": f"terminal.C[{i},{j}] = terminal.C[{j},{i}]",
        "index_domain": "k=N",
    }
    for i in range(2)
    for j in range(i, 2)
]
structure = {
    "quadratic_convention": "V_quadratic=sum_ij C_ij <v_i,v_j>, symmetric C; off-diagonal terms counted twice",
    "interior": {
        "index_domain": "1 <= k <= N-1; a=b=1",
        "basis_labels": ["x_0-x_N", "z_k", "x_k-x_N", "A(x_N)"],
        "coefficients": {
            f"{i},{j}": f"c_{i}{j}(k,N,L)" for i in range(4) for j in range(i, 4)
        },
    },
    "initial": {
        "index_domain": "k=0",
        "basis_labels": [],
        "coefficients": {},
        "expression": "0",
    },
    "terminal": {
        "index_domain": "k=N",
        "basis_labels": ["x_0-x_N", "A(x_N)"],
        "coefficients": {
            f"{i},{j}": f"t_{i}{j}(N,L)" for i in range(2) for j in range(i, 2)
        },
    },
    "function_terms": [],
    "constant_terms": [],
}
state = {
    **b3,
    "basis_templates": {
        "interior": structure["interior"]["basis_labels"],
        "initial": [],
        "terminal": structure["terminal"]["basis_labels"],
    },
    "basis_code": (notebook_dir / "supplementary/b4_basis.py").read_text(
        encoding="utf-8-sig"
    ),
    "structure_code": (notebook_dir / "supplementary/b4_structure.py").read_text(
        encoding="utf-8-sig"
    ),
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": None,
    "coefficient_formula_status": "unresolved",
    "expression_structure": structure,
    "unresolved_coefficients": unknowns,
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
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(notebook_dir / "state/dual_feg_b4.json").write_text(json.dumps(state, indent=2))
print("All-index full-coordinate reconstruction:", component_residuals)
