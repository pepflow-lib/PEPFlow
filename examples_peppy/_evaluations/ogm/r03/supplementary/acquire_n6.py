"""B2 additional coherent certificate for the B3 rank comparison."""

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
for key in ("TEMP", "TMP", "MPLCONFIGDIR"):
    directory = ROOT / "supplementary" / ".runtime" / key.lower()
    directory.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(directory)
sys.path[:0] = [
    str(ROOT / "supplementary" / "approved"),
    str(ROOT),
    str(ROOT / "supplementary" / "helpers"),
]
import numpy as np  # noqa: E402

# local helper resolved by the notebook runtime path
from certificates import (  # noqa: E402  # ty: ignore[unresolved-import]
    certificate_digest,
    revalidate,
    solve_certificate,
)
from ogm_setup import theta_sequence  # noqa: E402

previous = json.loads((ROOT / "state" / "ogm_b2.json").read_text())
hashes = previous["certificate_provenance"]["source_hashes"]
assert all(
    hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == expected
    for p, expected in hashes.items()
)
n = 6
dense = solve_certificate(n)
forward = [f"f:{'z_0' if k == 0 else f'x_{k}'},x_{k + 1}" for k in range(n)]
relaxed = [
    name
    for name, meta in dense["constraint_metadata"].items()
    if meta["origin"] == "interpolation"
    and not (name.startswith("f:x_star,") or name in forward)
]
selected = solve_certificate(n, relaxed)
ctx, pb, obj, pm, checked, residuals = revalidate(selected)
S = np.asarray(selected["S_matrix"])
ev, U = np.linalg.eigh(S)
D, E = np.diag(ev), U.T
residuals["S_reconstruction_max_abs"] = float(np.max(np.abs(E.T @ D @ E - S)))
residuals["dense_relaxed_gap"] = abs(dense["opt_value"] - selected["opt_value"])
assert residuals["dense_relaxed_gap"] < 1e-5
assert np.allclose(E.T @ D @ E, S, atol=1e-4, rtol=1e-5)
theta = theta_sequence(n)
expected = {
    f"f:x_star,{'z_0' if k == 0 else f'x_{k}'}": 2 * theta[k] / theta[n] ** 2
    for k in range(n)
}
expected[f"f:x_star,x_{n}"] = 1 / theta[n]
expected.update(
    {name: 2 * theta[k] ** 2 / theta[n] ** 2 for k, name in enumerate(forward)}
)
lambda_error = max(
    abs(selected["named_dual_values"][name] - value) for name, value in expected.items()
)
q = ctx[f"z_{n}"] - ctx["x_star"] - theta[n] * obj.grad(ctx[f"x_{n}"])
qcoords = np.asarray(pm.eval_vector(q).coords, dtype=float)
S_error = float(np.max(np.abs(np.outer(qcoords, qcoords) / (2 * theta[n] ** 2) - S)))
assert lambda_error < 1e-4 and S_error < 1e-4
data = {**previous, **selected}
data["normalization"] = {
    **previous["normalization"],
    "bound_value": selected["opt_value"],
}
data["certificate_provenance"]["source_hashes"] = hashes
data["numerical_checks"] = {
    "tolerances": previous["numerical_checks"]["tolerances"],
    "residuals": residuals,
    "passed": True,
}
data["numerical_decomposition"] = dict(
    method="direct",
    construction="Full spectral decomposition; no truncation",
    D=D.tolist(),
    ell_coords=E.tolist(),
    basis_labels=selected["basis_vectors"],
)
data["closed_form_search"] = {
    **previous["closed_form_search"],
    "reused_from_certificate": previous["certificate_id"],
    "additional_horizon_candidate_checks": {
        "N": n,
        "lambda_error": lambda_error,
        "S_error": S_error,
    },
}
assert all(
    hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == expected
    for p, expected in hashes.items()
)
data["certificate_id"] = certificate_digest(data)
(ROOT / "supplementary" / "b2-N6-dense.json").write_text(json.dumps(dense, indent=2))
(ROOT / "supplementary" / "b2-N6-certificate.json").write_text(
    json.dumps(data, indent=2)
)
print(
    json.dumps(
        {
            "N": n,
            "checks": residuals,
            "lambda_candidate_error": lambda_error,
            "S_candidate_error": S_error,
            "certificate_id": data["certificate_id"],
        }
    )
)
