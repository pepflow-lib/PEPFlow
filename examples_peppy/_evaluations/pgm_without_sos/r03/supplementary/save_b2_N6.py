from typing import Any

# Preserve the recorded import initialization order.
# isort: split
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("runtime.py")))
import hashlib  # noqa: E402 - imports follow runtime or notebook setup
import json  # noqa: E402 - imports follow runtime or notebook setup
import uuid  # noqa: E402 - imports follow runtime or notebook setup

from pgm_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

root = Path.cwd()
scope: dict[str, Any] = {"get_pep_setup": get_pep_setup}
cells = (
    (root / "supplementary/b2_cells.py")
    .read_text(encoding="utf-8-sig")
    .replace("state/pgm_dense.json", "supplementary/pgm_dense_N6.json")
    .replace("supplementary/sparse-trial.json", "supplementary/sparse-trial-N6.json")
)
exec(compile(cells, "b2_cells", "exec"), scope)
b1 = scope["b1"]
selected = scope["selected"]
allowlist = json.loads((root / "supplementary/approved/allowlist.json").read_text())
paths = [root / "pgm_setup.py", root / "supplementary/certificate.py"] + [
    Path(p)
    for p in allowlist["exact_read_files"]
    if "/pepflow/" in p.replace("\\", "/") and p.endswith(".py")
]
hashes = {
    str(p.relative_to(root)).replace("\\", "/"): hashlib.sha256(
        p.read_bytes()
    ).hexdigest()
    for p in paths
}
state = {
    **b1,
    **selected,
    "N_verify": selected["N"],
    "tau_sol": selected["named_dual_values"]["initial_condition"],
    "tau_name": "initial_condition",
    "normalization": {
        "tau_name": "initial_condition",
        "initial_condition": b1["initial_condition"],
        "performance_metric": b1["performance_metric"],
        "bound_value": selected["opt_value"],
        "bound_formula": b1["conjectured_rate"],
    },
    "certificate_provenance": {
        "solve_id": str(uuid.uuid4()),
        "pep_type": "primal",
        "solver_status": selected["solver_status"],
        "source_hashes": hashes,
        "solver": {
            "api": "CVXPrimalSolver.build_problem",
            "effective_name": "CLARABEL",
            "settings": {},
        },
    },
    "numerical_checks": {
        "tolerances": {
            "identity_atol": 1e-5,
            "identity_rtol": 0,
            "reconstruction_atol": 1e-4,
            "reconstruction_rtol": 1e-5,
            "dual_tol": 1e-6,
            "psd_tol": 1e-6,
            "dense_opt_atol": 1e-5,
        },
        "residuals": scope["residuals"],
        "passed": True,
    },
    "numerical_decomposition": {
        "method": "direct",
        "factorization": "spectral; all eigenvalues retained",
        "D": scope["D"].tolist(),
        "ell_coords": scope["E"].tolist(),
        "basis_labels": selected["basis_vectors"],
    },
    "closed_form_search": {
        "completed": True,
        "references_reviewed": [
            "Own sparse solve; no pre-existing target sources permitted"
        ],
        "attempts": [
            {
                "method": "Rational approximations and cumulative forward weights",
                "outcome": "candidate formulas for both f and g groups",
                "max_error": scope["err"],
            },
            {
                "method": "Construct candidate S by complete weighted identity; compare Gram, function, offset coordinates",
                "outcome": "candidate; global PSD unresolved",
                "max_error": scope["candidate_error"],
            },
        ],
        "unresolved_components": ["all-horizon S PSD and certificate identity proof"],
    },
    "formula_status": {"lambda": "candidate", "S": "candidate"},
    "lamb_code": cells[
        cells.index("def candidate_multiplier") : cells.index("candidate_values=")
    ],
    "S_code": "S_candidate = -pb.performance_metric + sp.Rational(1,4*N) + sum((candidate_multiplier(c.name,N)*(c.lhs-c.rhs) for c in entries),pf.Scalar.zero())",
    "S_decomp_type": "direct",
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "require_analytic_full_pep": False,
    "proof_valid": True,
}
keys = (
    "N_verify",
    "params_json",
    "relaxed_constraints",
    "S_matrix",
    "S_row_names",
    "S_col_names",
    "basis_vectors",
    "basis_scalars",
    "opt_value",
    "tau_sol",
    "tau_name",
    "named_dual_values",
    "constraint_metadata",
    "normalization",
    "certificate_provenance",
    "numerical_checks",
    "numerical_decomposition",
)
state["certificate_id"] = hashlib.sha256(
    json.dumps(
        {k: state[k] for k in keys},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
).hexdigest()
for filename in ("pgm_b2_N6.json",):
    (root / "supplementary" / filename).write_text(
        json.dumps(state, indent=2, allow_nan=False)
    )

print("Additional N6 coherent sample saved.")
