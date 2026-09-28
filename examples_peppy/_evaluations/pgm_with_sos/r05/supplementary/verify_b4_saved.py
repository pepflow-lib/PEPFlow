# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
exec(
    compile(
        (ROOT / "supplementary" / "run_b1.py").read_text().split("results = []")[0],
        "bootstrap",
        "exec",
    )
)
setup = importlib.import_module("pgm_setup")
np = importlib.import_module("numpy")
notebook_dir = ROOT
get_pep_setup = setup.get_pep_setup
f, g, L = setup.f, setup.g, setup.L
certificate = json.loads((ROOT / "state" / "pgm_b4.json").read_text())
for field in (
    "certificate_check_code",
    "decomposition_code",
    "grouping_code",
    "basis_code",
):
    exec(compile(certificate[field], field, "exec"))
coeff_by_k = {
    int(k): np.asarray(v).reshape((len(V_k_basis(int(k))), len(V_k_basis(int(k)))))
    for k, v in certificate["coeff_by_k"].items()
}
exec(compile(certificate["structure_code"], "stored-structure", "exec"))
residuals = {}
for k in range(N_int + 1):
    residuals[k] = scalar_residual(V_k_structure(k) - lyap[k])
    assert max(residuals[k]) <= 1e-5
(ROOT / "supplementary" / "b4-saved-replay.json").write_text(
    json.dumps({"passed": True, "residuals": residuals}, indent=2)
)
print("Saved B4 basis and full-expression source replay passed.")
