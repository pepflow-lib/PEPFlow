import hashlib
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
import candidates  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from candidates import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    sos_pieces,
)
from certificate import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    acquire,
    verify,
)

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup
from pepflow.parameter import (  # noqa: E402 - imports follow runtime or notebook setup
    eval_parameter,
)

n = 6
selected = json.loads((root / "state/pgm_b2.json").read_text())
dense, _, _, _ = acquire(n)
(root / "supplementary/b2-n6-dense.json").write_text(json.dumps(dense, indent=2))
relaxed = []
for name in dense["named_dual_values"]:
    if name == "initial_condition":
        continue
    owner, pair = name.split(":")
    left, right = pair.split(",")
    keep = left == "x_star" or (
        left != "x_star" and right != "x_star" and int(right[2:]) == int(left[2:]) + 1
    )
    if not keep:
        relaxed.append(name)
data, _, _, _ = acquire(n, relaxed)
(root / "supplementary/b2-n6-sparse-raw.json").write_text(json.dumps(data, indent=2))
checks, ctx, pb, _ = verify(data, dense["opt_value"])
pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
pieces = sos_pieces(ctx, n)
D = np.diag([float(sp.N(eval_parameter(c, {"L": sp.S.One}))) for _, _, c, _ in pieces])
E = np.asarray([pm.eval_vector(v).coords for _, _, _, v in pieces], dtype=float)
decomp = dict(
    method="direct",
    D=D.tolist(),
    ell_coords=E.tolist(),
    basis_labels=data["basis_vectors"],
    piece_labels=[f"{family}_{i}" for i, family, _, _ in pieces],
    source="Fixed supplied SOS candidate, normalization factor 1",
    reconstruction_source=inspect.getsource(candidates.sos_pieces),
    minimum_coefficient=float(np.diag(D).min()),
)
checks, _, _, _ = verify(data, dense["opt_value"], decomp)
print(
    json.dumps(
        dict(
            dense_status=dense["certificate_provenance"]["solver_status"],
            selected_status=data["certificate_provenance"]["solver_status"],
            checks=checks,
        ),
        indent=2,
    )
)
assert checks["passed"]
state = {
    **selected,
    **data,
    "numerical_decomposition": decomp,
    "numerical_checks": checks,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "fixed_sample_exact_candidate_identity": False,
    "closed_form_search": {
        **selected["closed_form_search"],
        "reuse_note": "N=4 candidate definitions reused at N=6; SOS numerical comparison repeated; no all-horizon claim",
    },
    "candidate_fit_max_abs": None,
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
(root / "supplementary/b2-n6-certificate.json").write_text(json.dumps(state, indent=2))
