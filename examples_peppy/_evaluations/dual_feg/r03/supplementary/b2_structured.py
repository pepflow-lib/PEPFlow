"""Test the pattern suggested by this attempt's dense multipliers."""
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "supplementary"), str(ROOT / "supplementary/helpers")]
import run_b1  # noqa: E402,F401
import numpy as np  # noqa: E402
from certificate import capture, verify_certificate  # noqa: E402
from dual_feg_setup import get_pep_setup  # noqa: E402

dense = json.loads((ROOT / "state/dual_feg_dense.json").read_text())
n = dense["N_verify"]
keep = {"initial_condition", f"A monotone:x_{n},x_star", f"A Lipschitz:x_{n-1},x_{n}"}
for k in range(n - 1):
    keep.add(f"A monotone:x_{n},x_half_{k}")
    keep.add(f"A Lipschitz:x_{k},x_half_{k}")
assert keep <= set(dense["constraint_metadata"])
dropped = [name for name in dense["constraint_metadata"] if name not in keep]
hashes = dict(dense["certificate_provenance"]["source_hashes"])
hashes["supplementary/helpers/certificate.py"] = hashlib.sha256((ROOT / "supplementary/helpers/certificate.py").read_bytes()).hexdigest()
hashes["supplementary/b2_structured.py"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
selected = capture(get_pep_setup, n, json.loads(dense["params_json"]), dropped, hashes)
checks, ctx, pm, checked = verify_certificate(selected, get_pep_setup, dense["opt_value"])
selected["numerical_checks"] = checks
(ROOT / "supplementary/b2-structured-candidate.json").write_text(json.dumps(selected, indent=2))
print(checks)
for name, value in selected["named_dual_values"].items():
    if value is not None:
        print(name, value, Fraction(value).limit_denominator(1000))
print("S eigenvalues", np.linalg.eigvalsh(selected["S_matrix"]))
guess = (2 / n * (ctx["x_0"] - ctx["x_star"]) - ctx[f"g_{n}"])**2
S_guess = pm.eval_scalar(guess)
print("square guess gram residual", np.max(np.abs(np.asarray(S_guess.inner_prod_coords, dtype=float) - selected["S_matrix"])))
