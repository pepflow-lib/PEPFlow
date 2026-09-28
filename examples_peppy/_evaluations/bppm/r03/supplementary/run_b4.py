# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import bppm_setup as setup

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

notebook_dir = runtime.ROOT
REPO_ROOT = runtime.APPROVED
b3 = json.loads((notebook_dir / "state/bppm_b3.json").read_text())
certificate = b3
N_int = b3["N_verify"]
params_sp = json.loads(b3["params_json"])
ctx, pb, obj = setup.get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(b3["relaxed_constraints"])
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(compile(b3[field], field, "exec"))
assert ranks == b3["rank_profile"]
evidence = json.loads((notebook_dir / b3["rank_search"]["evidence_path"]).read_text())
assert evidence["summary"] == b3["rank_search"]
for k, Vk in enumerate(lyap):
    actual = pm.eval_scalar(Vk)
    for component, saved in (
        (actual.inner_prod_coords, b3["lyap_inner_prod_coords"][k]),
        (actual.func_coords, b3["lyap_func_coords"][k]),
        (actual.offset, b3["lyap_offsets"][k]),
    ):
        assert np.allclose(
            np.asarray(component, dtype=float),
            np.asarray(saved, dtype=float),
            atol=1e-4,
            rtol=1e-5,
        )
sources = {}
for label in ("scan", "search", "basis", "coefficients", "structure"):
    sources[label] = (notebook_dir / f"supplementary/b4_{label}.py").read_text(
        encoding="utf-8-sig"
    )
    exec(compile(sources[label], f"b4_{label}.py", "exec"))
state = {
    **b3,
    "basis_templates": {
        "interior": ["x_k-x_star", "grad_h(x_k)", "x_0-x_star", "grad_h(x_0)"],
        "initial": [],
        "terminal": "same template at k=N",
    },
    "basis_code": sources["basis"],
    "structure_code": sources["structure"],
    "coeff_by_k": {str(k): C.tolist() for k, C in coeff_by_k.items()},
    "coeff_code": sources["coefficients"][
        sources["coefficients"].index("def coeff_pattern") : sources[
            "coefficients"
        ].index("\n\nfit_errors")
    ],
    "coefficient_formula_status": "candidate",
    "unresolved_coefficients": [],
    "expression_structure": {
        "quadratic_convention": "sum_ij C_ij <v_i,v_j>; symmetric C, off diagonals counted twice",
        "interior": {
            "index_domain": "1<=k<=N-1",
            "basis_labels": ["x_k-x_star", "grad_h(x_k)", "x_0-x_star", "grad_h(x_0)"],
            "coefficients": "C01=C10=1/(2 alpha N); C23=C32=-1/(2 alpha N); all others zero",
        },
        "initial": {
            "index_domain": "k=0",
            "basis_labels": [],
            "coefficients": "empty; V0=0",
        },
        "terminal": {
            "index_domain": "k=N",
            "basis_labels": ["x_N-x_star", "grad_h(x_N)", "x_0-x_star", "grad_h(x_0)"],
            "coefficients": "same as interior",
        },
        "function_terms": [
            {
                "index_domain": "1<=k<=N",
                "term": "f(x_k)-f(x_star)",
                "coefficient": "k/N",
            },
            {
                "index_domain": "1<=k<=N",
                "term": "h(x_0)-h(x_k)",
                "coefficient": "1/(alpha N)",
            },
        ],
        "constant_terms": [],
    },
    "numerical_reconstruction": {
        "certificate_id": b3["certificate_id"],
        "required_indices": required_indices,
        "quadratic_residuals": coefficient_residuals,
        "component_residuals": component_residuals,
        "tolerances": {
            "indep_tol": 1e-7,
            "span_tol": 1e-5,
            "component_atol": 1e-5,
            "component_rtol": 1e-5,
        },
        "passed": True,
    },
    "sparse_search_results": sparse_search_results,
    "coefficient_candidate_errors": fit_errors,
    "lyapunov_proof_verified": False,
}
(notebook_dir / "state/bppm_b4.json").write_text(json.dumps(state, indent=2))
print("B4 state saved.")
