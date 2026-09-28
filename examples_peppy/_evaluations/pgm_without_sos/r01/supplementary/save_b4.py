"""Persist numerical structure by replaying the notebook's checked definitions."""
import json
import sys
from pathlib import Path
from typing import Any


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path[:0] = [str(root / "supplementary/approved"), str(root / "supplementary/h"), str(root)]
    from runtime import configure
    configure()
    import nbformat
    import numpy as np
    import pepflow as pf
    from pepflow.lyapunov_utils import find_symmetric_coefficient_matrix
    from pgm_setup import get_pep_setup, f, g
    b3 = json.loads((root / "state/pgm_b3.json").read_text())
    ns: dict[str, Any] = dict(certificate=b3, notebook_dir=root,
                              get_pep_setup=get_pep_setup, f=f, g=g)
    for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
        exec(compile(b3[field], f"<B3-{field}>", "exec"), ns)
    assert ns["certificate_checked"] and ns["grouping_checked"]
    nb = nbformat.read(root / "pgm_example_lyap.ipynb", as_version=4)
    ns.update(b3=b3, N_int=b3["N_verify"], params_sp=json.loads(b3["params_json"]),
              find_symmetric_coefficient_matrix=find_symmetric_coefficient_matrix)
    for index in (34,36,37):
        exec(compile(nb.cells[index].source, f"<notebook-cell-{index}>", "exec"), ns)
    basis_code = nb.cells[34].source.split("\n\nfor k in range")[0]
    structure_function = nb.cells[37].source.split("\n\ncomponent_residuals")[0]
    structure_code = "function_weights = " + repr(ns["function_weights"]) + "\n" + structure_function
    exec(compile(structure_code, "<B4-structure-replay>", "exec"), ns)
    for k in range(b3["N_verify"]+1):
        difference = ns["pm"].eval_scalar(ns["V_k_structure"](k)-ns["lyap"][k])
        for coords in (difference.inner_prod_coords, difference.func_coords, difference.offset):
            assert np.max(np.abs(np.asarray(coords, dtype=float)), initial=0) < 1e-4
    unknowns = [dict(name=f"c_{i}{j}", arguments=["k","N","L"],
                    role=f"interior.C[{i},{j}]=interior.C[{j},{i}]",
                    index_domain="1 <= k < N") for i in range(4) for j in range(i,4)]
    unknowns += [dict(name=name, arguments=args, role=role, index_domain=domain)
                 for name,args,role,domain in (
                     ("a_f", ["k","N","L"], "coefficient of f(x_k)-f(x_star)", "1 <= k < N"),
                     ("a_g", ["k","N","L"], "coefficient of g(x_k)-g(x_star)", "1 <= k < N"),
                     ("c_terminal", ["N","L"], "terminal.C[0,0]", "k=N"),
                     ("af_terminal", ["N","L"], "terminal f gap coefficient", "k=N"),
                     ("ag_terminal", ["N","L"], "terminal g gap coefficient", "k=N"))]
    structure = {
        "quadratic_convention": "sum_ij C_ij <v_i,v_j>, symmetric C; off-diagonal entries count twice",
        "interior": {"index_domain": "1 <= k < N; a=b=1",
            "basis_labels": ["x0-x_star","xk-x_star","grad_f(xk)-grad_f(x_star)","grad_f(xk)"],
            "coefficients": {f"{i},{j}": f"c_{i}{j}(k,N,L)" for i in range(4) for j in range(i,4)}},
        "initial": {"index_domain": "k=0", "basis_labels": [], "coefficients": {}, "value": "0"},
        "terminal": {"index_domain": "k=N", "basis_labels": ["x0-x_star"], "coefficients": {"0,0": "c_terminal(N,L)"}},
        "function_terms": [
            {"expression": "f(x_k)-f(x_star)", "coefficient": "a_f(k,N,L)", "index_domain": "1<=k<N"},
            {"expression": "g(x_k)-g(x_star)", "coefficient": "a_g(k,N,L)", "index_domain": "1<=k<N"},
            {"expression": "f(x_N)-f(x_star)", "coefficient": "af_terminal(N,L)", "index_domain": "k=N"},
            {"expression": "g(x_N)-g(x_star)", "coefficient": "ag_terminal(N,L)", "index_domain": "k=N"}],
        "constant_terms": []}
    state = {**b3, "basis_templates": structure,
             "basis_code": basis_code, "structure_code": structure_code,
             "coeff_by_k": {str(k): C.tolist() for k,C in ns["coeff_by_k"].items()},
             "coeff_code": None, "coefficient_formula_status": "unresolved",
             "expression_structure": structure, "unresolved_coefficients": unknowns,
             "numerical_reconstruction": {
                 "certificate_id": b3["certificate_id"],
                 "required_indices": list(range(b3["N_verify"]+1)),
                 "quadratic_residuals": {str(k): v for k,v in ns["coefficient_residuals"].items()},
                 "component_residuals": ns["component_residuals"],
                 "tolerances": {"indep_tol": 1e-7, "span_tol": 1e-5,
                                "component_atol": 1e-4, "component_rtol": 1e-5},
                 "passed": True},
             "numerical_certificate_verified": True,
             "analytic_full_pep_verified": False, "lyapunov_proof_verified": False}
    assert pf.get_current_context() is ns["ctx"]
    (root / "state/pgm_b4.json").write_text(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
