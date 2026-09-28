# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("runtime.py")))
import json  # noqa: E402 - imports follow runtime or notebook setup

import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from pgm_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

NOTEBOOK_DIR = Path.cwd()
REPO_ROOT = NOTEBOOK_DIR / "supplementary/approved"
certificate = json.loads((NOTEBOOK_DIR / "supplementary/pgm_b2_N6.json").read_text())
N_int = certificate["N_verify"]
params_sp = {"L": sp.Integer(1), "R": sp.Integer(1)}
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
for name in ("certificate_check.py", "decomposition_b3.py", "grouping_b3.py"):
    exec(
        compile(
            (NOTEBOOK_DIR / "supplementary" / name).read_text(encoding="utf-8-sig"),
            name,
            "exec",
        )
    )
obs = {
    "N": N_int,
    "certificate_id": certificate["certificate_id"],
    "recipe_id": "reverse_ldl_latest_gradient_step",
    "rank_profile": ranks,
    "singular_values": singular_values,
    "rank_convention": {
        "tolerance": 1e-4,
        "scaling": "none; original Gram coordinates",
        "coordinate_order": "setup earlier iterates first",
    },
    "rank_credible": all(
        not any(1e-5 < v < 1e-3 for v in singular_values[k]) for k in range(1, N_int)
    ),
    "certificate_checked": certificate_checked,
    "grouping_checked": grouping_checked,
    "coverage_residuals": coverage_residuals,
    "constraint_assignment": term_assignment,
    "S_assignment": S_assignment,
}
(NOTEBOOK_DIR / f"supplementary/rank-N{N_int}.json").write_text(
    json.dumps(obs, indent=2)
)
(NOTEBOOK_DIR / "supplementary/rank_search_N6_intermediate.json").write_text(
    json.dumps(
        {
            "summary": {
                "status": "insufficient_evidence",
                "confirmed_horizons": [],
                "boundary_exclusions": {"left": 1, "right": 1},
                "requested_next_horizon": 6,
            },
            "samples": [obs],
        },
        indent=2,
    )
)
print("Credible rank?", obs["rank_credible"])
