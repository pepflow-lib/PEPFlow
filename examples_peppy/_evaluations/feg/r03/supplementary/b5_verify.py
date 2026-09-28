# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
import sympy as sp
from feg_setup import get_pep_setup

root = runtime.ROOT
notebook_dir = root
REPO_ROOT = root / "supplementary/approved"
b4 = json.loads((root / "state/feg_b4.json").read_text())
certificate = b4
N_int = b4["N_verify"]
params_sp = {k: sp.S(v) for k, v in json.loads(b4["params_json"]).items()}
ctx, pb, obj = get_pep_setup(sp.S(N_int), params_sp)
pb.set_relaxed_constraints(b4["relaxed_constraints"])
ctx.set_as_current()
for field in (
    "certificate_check_code",
    "decomposition_code",
    "grouping_code",
    "basis_code",
):
    exec(b4[field])
coeff_by_k = {
    int(k): np.asarray(C, dtype=float).reshape((0, 0) if not C else (len(C), len(C)))
    for k, C in b4["coeff_by_k"].items()
}
exec(b4["structure_code"])
required_indices = list(range(N_int + 1))
exec((root / "supplementary/b4_components.py").read_text(encoding="utf-8-sig"))
for name in ("exact_helpers", "step", "derive", "base", "boundary"):
    exec((root / f"supplementary/b5_{name}.py").read_text(encoding="utf-8-sig"))
checks = dict(
    step=step_verified,
    base=base_verified,
    boundary=boundary_verified,
    signs=signs_verified,
    domain=domain_verified,
    normalization=normalization_verified,
)
assert all(checks.values())
(root / "supplementary/b5-exact-results.json").write_text(
    json.dumps(
        dict(
            proof_checks=checks,
            symbolic_domain="N integer >=1, k integer 1<=k<=N-1, L>0,R>=0",
            step_zero=True,
            base_zero=True,
            boundary_zero=True,
        ),
        indent=2,
    )
)
