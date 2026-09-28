# Archived Block 3 loader; notebook execution uses the guarded visible cell.
# ty: ignore[unresolved-attribute]

"""Load/revalidate one complete certificate, with no optimization solve."""

import importlib.util
import json
import sys
from pathlib import Path

import sympy as sp

if "EXAMPLE" not in globals():
    EXAMPLE = Path(__file__).resolve().parent.parent
REPO_ROOT = EXAMPLE.parent.parent
HERE = EXAMPLE / "supplementary"
sys.path.insert(0, str(REPO_ROOT))
sys.dont_write_bytecode = True

if "certificate" not in globals():
    certificate = json.loads(
        (EXAMPLE / "state" / "ogm_conjecture_4_b2.json").read_text()
    )
N_int = int(certificate["N_verify"])
N = sp.S(N_int)
params_sp = {
    key: sp.sympify(value)
    for key, value in json.loads(certificate["params_json"]).items()
}
spec = importlib.util.spec_from_file_location(
    "b3_current_setup", EXAMPLE / "ogm_conjecture4_setup.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ctx, pb, obj = mod.get_pep_setup(N, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
ctx.set_as_current()
assert certificate["normalization"]["initial_condition"] == "||x_0 - x_star||^2 <= R^2"
assert certificate["normalization"]["performance_metric"] == "f(y_N) - f(x_star)"
assert certificate["certificate_provenance"]["solver_status"] == "optimal"
