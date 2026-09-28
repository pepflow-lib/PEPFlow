# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

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
