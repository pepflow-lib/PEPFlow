# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import bppm_setup as setup

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

notebook_dir = runtime.ROOT
REPO_ROOT = runtime.APPROVED
certificate = json.loads(
    (notebook_dir / "supplementary/b2-N6-certificate.json").read_text()
)
N_int = certificate["N_verify"]
params_sp = json.loads(certificate["params_json"])
ctx, pb, obj = setup.get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
code = {}
for label in ("certificate_check", "decomposition", "grouping"):
    code[label] = (notebook_dir / f"supplementary/b3_{label}.py").read_text(
        encoding="utf-8-sig"
    )
    exec(compile(code[label], f"b3_{label}.py", "exec"))
sample = {
    "N": N_int,
    "certificate_id": certificate["certificate_id"],
    "recipe_id": "adjacent_pairs_terminal_h_and_full_S_boundary",
    "rank_profile": ranks,
    "singular_values": singular_values,
    "rank_credible": rank_credible,
    "certificate_checked": certificate_checked,
    "grouping_checked": grouping_checked,
    "rank_convention": {
        "tolerance": 1e-4,
        "scaling": "none",
        "coordinate_order": "setup creation order",
    },
    "coverage_errors": coverage_errors,
    "boundary_names": boundary_names,
    "boundary_S": boundary_S,
    "code": code,
}
(notebook_dir / f"supplementary/b3-sample-N{N_int}.json").write_text(
    json.dumps(sample, indent=2)
)
print("Saved horizon sample; cross-horizon confirmation remains pending.")
