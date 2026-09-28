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
from bppm_setup import get_pep_setup

notebook_dir = runtime.ATTEMPT
certificate = json.loads((notebook_dir / "state/bppm_b2.json").read_text())
N_int = certificate["N_verify"]
params_sp = {k: sp.S(v) for k, v in json.loads(certificate["params_json"]).items()}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
ctx.set_as_current()
for file in ("b3_check.py", "b3_decomposition.py", "b3_grouping.py", "b3_coverage.py"):
    source = (notebook_dir / "supplementary" / file).read_text(encoding="utf-8-sig")
    exec(compile(source, file, "exec"), globals())
observation = {
    "N": N_int,
    "certificate_id": certificate["certificate_id"],
    "recipe_id": "consecutive_residuals_terminal_h_and_S",
    "rank_profile": ranks,
    "rank_convention": {
        "tolerance": rank_tolerance,
        "scaling": "absolute singular values, unscaled Gram coordinates",
        "coordinate_order": "setup basis order",
    },
    "rank_credible": rank_credible,
    "certificate_checked": certificate_checked,
    "grouping_checked": grouping_checked,
    "singular_values": singular_values,
    "boundary_exclusions": {"left": rank_left, "right": rank_right},
    "constraint_assignment": term_assignment,
    "S_assignment": S_assignment,
}
(notebook_dir / f"supplementary/b3_rank_N{N_int}.json").write_text(
    json.dumps(observation, indent=2)
)
print("Observation saved")

source = (notebook_dir / "supplementary/b3_assess.py").read_text()
exec(compile(source, "b3_assess.py", "exec"), globals())
rank_samples = [
    json.loads((notebook_dir / f"supplementary/b3_rank_N{n}.json").read_text())
    for n in (4, 6)
]
rank_search = assess_rank_pattern(
    rank_samples, certificate["certificate_id"], left=1, right=1
)
assert rank_search["status"] == "confirmed"
rank_search["evidence_path"] = "supplementary/rank_search.json"
(notebook_dir / "supplementary/rank_search.json").write_text(
    json.dumps({"summary": rank_search, "samples": rank_samples}, indent=2)
)


def read_source(name):
    return (notebook_dir / "supplementary" / name).read_text(encoding="utf-8-sig")


evaluated = [pm.eval_scalar(v) for v in lyap]
state = {
    **certificate,
    "rank_profile": ranks,
    "rank_search": rank_search,
    "lyap_inner_prod_coords": [
        np.asarray(v.inner_prod_coords, dtype=float).tolist() for v in evaluated
    ],
    "lyap_func_coords": [
        np.asarray(v.func_coords, dtype=float).tolist() for v in evaluated
    ],
    "lyap_offsets": [float(v.offset) for v in evaluated],
    "certificate_check_code": read_source("b3_check.py"),
    "decomposition_code": read_source("b3_decomposition.py"),
    "grouping_code": read_source("b3_grouping.py")
    + "\n"
    + read_source("b3_coverage.py"),
    "extra_duals": extra_duals,
    "rank_tolerance": rank_tolerance,
    "reconstruction_tolerance": tol["reconstruction_atol"],
    "reconstruction_rtol": tol["reconstruction_rtol"],
    "grouping_coverage": {
        "constraint_assignment": term_assignment,
        "S_assignment": S_assignment,
        "normalization_constraint": tau_name,
        "boundary_constraints": boundary_names,
        "boundary_S": boundary_S,
        "omitted_constraints": [],
        "checked": grouping_checked,
    },
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(notebook_dir / "state/bppm_b3.json").write_text(json.dumps(state, indent=2))
print("B3 state saved with cross-horizon confirmation:", rank_search)
