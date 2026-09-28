"""Block 2 dense and threshold-sparsified certificate acquisition."""

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supplementary"))
import run_b1  # noqa: E402,F401

sys.path.insert(0, str(ROOT / "supplementary/helpers"))
import numpy as np  # noqa: E402

# local helper resolved by the notebook runtime path
from certificate import (  # noqa: E402  # ty: ignore[unresolved-import]
    capture,
    certificate_id,
    verify_certificate,
)
from dual_feg_setup import get_pep_setup  # noqa: E402

b1 = json.loads((ROOT / "state/dual_feg_b1.json").read_text(encoding="utf-8-sig"))
allowed = json.loads((ROOT / "supplementary/approved/allowlist.json").read_text())
source_paths = [
    ROOT / "dual_feg_setup.py",
    ROOT / "supplementary/helpers/certificate.py",
]
source_paths += [
    Path(p) for p in allowed["exact_read_files"] if "approved\\pepflow\\" in p
]
hashes = {
    str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
        p.read_bytes()
    ).hexdigest()
    for p in source_paths
}
n = b1["N_verify"]
params = json.loads(b1["params_json"])
dense = capture(get_pep_setup, n, params, [], hashes)
(ROOT / "state/dual_feg_dense.json").write_text(json.dumps(dense, indent=2))
print(
    "Dense",
    dense["opt_value"],
    dense["certificate_provenance"]["solver_status"],
    flush=True,
)
for name, value in dense["named_dual_values"].items():
    if abs(value) > 1e-5:
        print(name, round(value, 8), flush=True)
print("S eigenvalues", np.linalg.eigvalsh(dense["S_matrix"]), flush=True)
print("Basis", dense["basis_vectors"], flush=True)
drop = [
    name
    for name, value in dense["named_dual_values"].items()
    if name != "initial_condition" and abs(value) < 1e-6
]
print("Dropping", len(drop), "of", len(dense["named_dual_values"]) - 1, flush=True)
selected = capture(get_pep_setup, n, params, drop, hashes)
checks, ctx, pm, residual = verify_certificate(
    selected, get_pep_setup, dense["opt_value"]
)
selected["numerical_checks"] = checks
(ROOT / "supplementary/b2-selected-candidate.json").write_text(
    json.dumps(selected, indent=2)
)
print("Selected", selected["opt_value"], checks, flush=True)
for name, value in selected["named_dual_values"].items():
    if value is not None and abs(value) > 1e-6:
        print(name, value, str(Fraction(value).limit_denominator(1000)), flush=True)
print("LDL D", np.diag(selected["numerical_decomposition"]["D"]), flush=True)
print(
    "LDL factors",
    np.array(selected["numerical_decomposition"]["ell_coords"]),
    flush=True,
)
if checks["passed"]:
    selected["certificate_id"] = certificate_id(selected)
