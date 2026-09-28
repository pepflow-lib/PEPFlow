# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np
import runtime
import sympy as sp
from dual_feg_setup import get_pep_setup

notebook_dir = runtime.ATTEMPT
REPO_ROOT = runtime.APPROVED
b3 = json.loads((notebook_dir / "state/dual_feg_b3.json").read_text())
certificate = b3
N_int = b3["N_verify"]
params_sp = {key: sp.S(value) for key, value in json.loads(b3["params_json"]).items()}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(b3["relaxed_constraints"])
for field in ["certificate_check_code", "decomposition_code", "grouping_code"]:
    exec(compile(b3[field], field, "exec"))
assert ranks == b3["rank_profile"]
for k, Vk in enumerate(lyap):
    value = pm.eval_scalar(Vk)
    for actual, saved in [
        (value.inner_prod_coords, b3["lyap_inner_prod_coords"][k]),
        (value.func_coords, b3["lyap_func_coords"][k]),
        (value.offset, b3["lyap_offsets"][k]),
    ]:
        assert np.allclose(
            np.asarray(actual, dtype=float),
            np.asarray(saved, dtype=float),
            atol=1e-4,
            rtol=1e-5,
        )
rank_evidence = json.loads(
    (notebook_dir / b3["rank_search"]["evidence_path"]).read_text()
)
assert rank_evidence["summary"] == b3["rank_search"]
p = notebook_dir / "supplementary/b4_scan_cells.py"
exec(compile(p.read_text(encoding="utf-8-sig"), str(p), "exec"))
scan = {
    "certificate_id": b3["certificate_id"],
    "candidate_labels": [label for label, _ in candidate_pairs],
    "column_space": {
        str(k): [candidate_labels[id(v)] for v in vals]
        for k, vals in spanning_by_k.items()
    },
    "selected_sparse": {
        str(k): [candidate_labels[id(v)] for v in vals]
        for k, vals in searched_basis.items()
    },
    "coefficients": {str(k): C.tolist() for k, C in searched_coeff.items()},
}
(notebook_dir / "supplementary/b4-scan.json").write_text(json.dumps(scan, indent=2))
