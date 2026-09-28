# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from owned_runtime import ROOT, configure  # ty: ignore[unresolved-import]

configure()
import json  # noqa: E402 - imports follow runtime or notebook setup

import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from pgm_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

# Preserve the recorded import initialization order.
# isort: split
from pgm_setup import (  # noqa: E402, F401 -- Required by exec of pgm_b4.json#certificate_check_code. Paths initialized above.
    f,
    g,
)

b4 = json.loads((ROOT / "state/pgm_b4.json").read_text())
certificate = b4
REPO_ROOT = ROOT
N_int = b4["N_verify"]
params_sp = {"L": sp.Integer(1), "R": sp.Integer(1)}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(b4["relaxed_constraints"])
for field in (
    "certificate_check_code",
    "decomposition_code",
    "grouping_code",
    "basis_code",
):
    exec(compile(b4[field], field, "exec"), globals())
coeff_by_k = {
    int(k): np.asarray(C, dtype=float).reshape((len(V_k_basis(int(k))),) * 2)
    for k, C in b4["coeff_by_k"].items()
}
exec(compile(b4["structure_code"], "structure_code", "exec"), globals())
residuals = {}
for k in range(N_int + 1):
    v = pm.eval_scalar(V_k_structure(k) - lyap[k])
    residuals[k] = [
        float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0))
        for a in (v.inner_prod_coords, v.func_coords, v.offset)
    ]
    assert max(residuals[k]) < 1e-4
(ROOT / "supplementary/b4-replay.json").write_text(
    json.dumps({"passed": True, "component_residuals": residuals}, indent=2)
)
print("Saved basis and structure source replay passed:", residuals)
