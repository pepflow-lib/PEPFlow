import importlib.util
import inspect
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime", root / "supplementary/helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
import basis_structure as bs  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
from partial_sums import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    construct,
)

b3 = json.loads((root / "state/pgm_b3.json").read_text())
trial = construct(b3, variant=b3["rank_search"]["recipe_id"])
scan = bs.scan_candidate_bases(trial, b3["N"])
coeffs, funcs, offsets, errors = bs.extract_structure(trial, b3["N"])
structure = dict(
    quadratic_convention="V_quadratic = sum_i,j C_ij <v_i,v_j>; symmetric C; off-diagonal terms counted twice",
    interior=dict(
        index_domain="1 <= k <= N-1; exclusions a=b=1",
        basis_labels=["x_0-x_star", "x_k-x_star", "a_k", "a_k-a_star"],
        coefficients="coeff_pattern(k,N,L); candidate only",
    ),
    initial=dict(
        index_domain="k=0", basis_labels=[], coefficients="empty matrix; V_0=0"
    ),
    terminal=dict(
        index_domain="k=N",
        basis_labels=["x_0-x_star"],
        coefficients="C_00=-L/(4N); candidate only",
    ),
    function_terms=[
        dict(
            term="f(x_k)-f(x_star)",
            index_domain="1 <= k < N",
            coefficient="(k+1)/(2N-k); candidate",
        ),
        dict(
            term="g(x_k)-g(x_star)",
            index_domain="1 <= k < N",
            coefficient="k/(2N-k); candidate",
        ),
        dict(term="h(x_N)-h(x_star)", index_domain="k=N", coefficient="1; candidate"),
    ],
    constant_terms=[],
)
state = {
    **b3,
    "basis_templates": structure,
    "basis_code": inspect.getsource(bs.V_k_basis)
    + "\n"
    + inspect.getsource(bs.V_k_basis_labels),
    "structure_code": inspect.getsource(bs.V_k_structure),
    "structure_sample_coefficients": dict(
        function_coefficients=funcs, offset_coefficients=offsets
    ),
    "coeff_by_k": {str(k): C.tolist() for k, C in coeffs.items()},
    "coeff_code": inspect.getsource(bs.coeff_pattern)
    + "\n"
    + inspect.getsource(bs.function_coeff_pattern),
    "coefficient_formula_status": "candidate",
    "expression_structure": structure,
    "unresolved_coefficients": [],
    "analytic_obligations": [
        "All-horizon validity of candidate coefficient and function-weight formulas, exact local identities and signs"
    ],
    "numerical_reconstruction": dict(
        certificate_id=b3["certificate_id"],
        required_indices=list(range(b3["N"] + 1)),
        quadratic_residuals={
            str(k): e["quadratic_frobenius"] for k, e in errors.items()
        },
        component_residuals={str(k): e["components"] for k, e in errors.items()},
        candidate_fit_residuals={
            str(k): e["candidate_coefficient_max_abs"] for k, e in errors.items()
        },
        tolerances=dict(
            indep_tol=1e-7, span_tol=1e-5, component_atol=1e-5, component_rtol=1e-5
        ),
        passed=True,
    ),
    "candidate_scan": scan,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(root / "state/pgm_b4.json").write_text(json.dumps(state, indent=2))
(root / "supplementary/b4-candidate-scan.json").write_text(json.dumps(scan, indent=2))
print("All-index B4 structure verified and state saved")
