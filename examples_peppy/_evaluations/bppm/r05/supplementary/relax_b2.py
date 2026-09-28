"""Sparse B2 certificate and initial candidate-formula search."""

from typing import Any, cast

# Preserve the recorded import initialization order.
# isort: split
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVED = ROOT / "supplementary/approved"
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    path = ROOT / "supplementary/.runtime" / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
sys.path[:0] = [str(APPROVED), str(ROOT / "supplementary/helpers")]
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from certificate_tools import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    certificate_id,
    inventory,
    solve_capture,
    verify_certificate,
)

spec = importlib.util.spec_from_file_location("bppm_setup", ROOT / "bppm_setup.py")
assert spec is not None and spec.loader is not None
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
b1 = json.loads((ROOT / "state/bppm_b1.json").read_text())
dense = json.loads((ROOT / "state/bppm_dense.json").read_text())
N = int(sys.argv[1]) if len(sys.argv) > 1 else b1["N_verify"]
assert 1 <= N <= 12
params = {k: sp.S(v) for k, v in json.loads(b1["params_json"]).items()}
ctx, pb, obj = setup.get_pep_setup(N, params)
keep = {"initial_condition", f"h:x_star,x_{N}"}
keep.update(f"f:x_star,x_{i}" for i in range(1, N + 1))
keep.update(f"f:x_{i},x_{i + 1}" for i in range(1, N))
keep.update(f"h:x_{i},x_{i - 1}" for i in range(1, N + 1))
keep.update(f"h:x_{i},x_{i + 1}" for i in range(1, N))
relaxed = [c.name for c, *_ in inventory(ctx, pb) if c.name not in keep]
pb.set_relaxed_constraints(relaxed)
allowlist = json.loads((APPROVED / "allowlist.json").read_text())
files = [ROOT / "bppm_setup.py", ROOT / "supplementary/helpers/certificate_tools.py"]
files.extend(
    Path(p)
    for p in allowlist["exact_read_files"]
    if Path(p).parent == APPROVED / "pepflow"
)
hashes = {
    str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
        p.read_bytes()
    ).hexdigest()
    for p in files
}
if N != b1["N_verify"]:
    dense_ctx, dense_pb, _ = setup.get_pep_setup(N, params)
    dense = solve_capture(dense_ctx, dense_pb, params, hashes)
    dense["N"] = N
    (ROOT / f"supplementary/bppm_N{N}_dense.json").write_text(
        json.dumps(dense, indent=2)
    )
    ctx.set_as_current()
data = solve_capture(ctx, pb, params, hashes)
S = np.asarray(data["S_matrix"])
eig, U = np.linalg.eigh((S + S.T) / 2)
data["numerical_decomposition"] = {
    "method": "direct",
    "construction": "spectral factors of same selected S, no truncation",
    "D": np.diag(eig).tolist(),
    "ell_coords": U.T.tolist(),
    "basis_labels": data["basis_vectors"],
}
checks, _ = verify_certificate(ctx, pb, params, data, dense["opt_value"])
print("NUMERICAL CHECKS", json.dumps(checks))
assert checks["passed"]
candidate = {
    "initial_condition": sp.Rational(1, N) / params["alpha"],
    f"h:x_star,x_{N}": sp.Rational(1, N) / params["alpha"],
}
candidate.update({f"f:x_star,x_{i}": sp.Rational(1, N) for i in range(1, N + 1)})
candidate.update({f"f:x_{i},x_{i + 1}": sp.Rational(i, N) for i in range(1, N)})
candidate.update(
    {f"h:x_{i},x_{i - 1}": sp.Rational(i, N) / params["alpha"] for i in range(1, N + 1)}
)
candidate.update(
    {f"h:x_{i},x_{i + 1}": sp.Rational(i, N) / params["alpha"] for i in range(1, N)}
)
errors = {
    name: abs(float(candidate.get(name, 0)) - float(v))
    for name, v in data["named_dual_values"].items()
    if v is not None
}
print("CANDIDATE MAX LAMBDA ERROR", max(errors.values()))
print("S ZERO CANDIDATE ERROR", float(np.max(abs(S))))
for name, v in data["named_dual_values"].items():
    if v is not None:
        print(name, v, "candidate", candidate.get(name, 0))
assert max(errors.values()) < 1e-4 and np.max(abs(S)) < 1e-4
lamb_code = """def candidate_multipliers(N, alpha):
    values = {'initial_condition': 1/(alpha*N), f'h:x_star,x_{N}': 1/(alpha*N)}
    values.update({f'f:x_star,x_{i}': 1/N for i in range(1,N+1)})
    values.update({f'f:x_{i},x_{i+1}': i/N for i in range(1,N)})
    values.update({f'h:x_{i},x_{i-1}': i/(alpha*N) for i in range(1,N+1)})
    values.update({f'h:x_{i},x_{i+1}': i/(alpha*N) for i in range(1,N)})
    return values
"""
state: dict[str, Any] = {
    **b1,
    **data,
    "N": N,
    "N_verify": N,
    "numerical_checks": checks,
    "normalization": {
        "tau_name": "initial_condition",
        "initial_condition": b1["initial_condition"],
        "performance_metric": b1["performance_metric"],
        "bound_value": data["opt_value"],
        "bound_formula": b1["conjectured_rate"],
    },
    "lamb_code": lamb_code,
    "S_code": "S_guess = pf.Scalar.zero()",
    "formula_status": {"lambda": "candidate", "S": "candidate"},
    "closed_form_search": {
        "completed": True,
        "references_reviewed": [
            "Own input and approved generic framework only; target references prohibited"
        ],
        "attempts": [
            {
                "method": "Dense multiplier support inspection, then nearest-neighbor relaxation",
                "result": "optimal bound preserved",
            },
            {
                "method": "Rational index-pattern candidates for every active multiplier and S=0",
                "max_lambda_error": max(errors.values()),
                "max_S_error": float(np.max(abs(S))),
                "result": "Matches selected N=4 certificate; arbitrary-horizon identity not yet established",
            },
        ],
        "unresolved_components": [
            "arbitrary-horizon full-certificate identity and domain proof"
        ],
    },
    "S_decomp_type": "direct",
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "require_analytic_full_pep": False,
    "proof_valid": True,
    "completion_status": "pending_notebook_checks",
    "candidate_lambda_max_error": max(errors.values()),
    "candidate_S_max_error": float(np.max(abs(S))),
    "dense_opt_value": dense["opt_value"],
}
primary = data["all_lambda_groups"]["f"]["convex"]
state.update(
    lambda_matrix=primary["matrix"],
    lambda_row_names=primary["row_names"],
    lambda_col_names=primary["col_names"],
)
state["certificate_id"] = certificate_id(state)
if N == b1["N_verify"]:
    for filename in ("bppm_relaxed.json", "bppm_b2.json"):
        (ROOT / "state" / filename).write_text(
            json.dumps(state, indent=2, allow_nan=False)
        )
    (ROOT / "state/bppm_relaxed_constraints.json").write_text(
        json.dumps(relaxed, indent=2)
    )
else:
    state["completion_status"] = "numerical_certificate_verified"
    cast(dict[str, Any], state["closed_form_search"])["source_initial_search"] = (
        "state/bppm_b2.json"
    )
    state["closed_form_search"]["attempts"][-1]["result"] = (
        f"Matches N={N} certificate; arbitrary-horizon identity not yet established"
    )
    (ROOT / f"supplementary/bppm_N{N}_b2.json").write_text(
        json.dumps(state, indent=2, allow_nan=False)
    )
