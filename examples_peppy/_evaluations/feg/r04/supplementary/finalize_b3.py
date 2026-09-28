import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
source_names = ("b3_certificate_check.py", "b3_decomposition.py", "b3_grouping.py")
sources = [
    (root / "supplementary" / filename).read_text(encoding="utf-8-sig")
    for filename in source_names
]
samples = []
selected_scope = None
for certpath in ("supplementary/b2-certificate-N4.json", "state/feg_b2.json"):
    certificate = json.loads((root / certpath).read_text())
    scope = {"certificate": certificate}
    for filename, source in zip(source_names, sources):
        exec(compile(source, filename, "exec"), scope)
    sample = {
        key: scope[key]
        for key in (
            "singular_values",
            "rank_credible",
            "certificate_checked",
            "grouping_checked",
            "coverage_residuals",
            "term_assignment",
            "S_assignment",
        )
    }
    sample.update(
        N=scope["N_int"],
        rank_profile=scope["ranks"],
        certificate_id=certificate["certificate_id"],
        certificate_path=certpath,
        recipe_id="consecutive-mon-plus-own-half-lipschitz-whole-S-boundary",
        rank_convention={
            "tolerance": 1e-4,
            "scaling": "absolute singular values, no rescaling",
            "coordinates": "setup basis order",
        },
        boundary_exclusions={"left": 1, "right": 1},
    )
    samples.append(sample)
    (root / f"supplementary/b3-rank-confirmed-N{sample['N']}.json").write_text(
        json.dumps(sample, indent=2)
    )
    if certpath == "state/feg_b2.json":
        selected_scope = scope
assert selected_scope is not None
assert len({s["N"] for s in samples}) >= 2
assert len({s["recipe_id"] for s in samples}) == 1
assert all(
    s["certificate_checked"] and s["grouping_checked"] and s["rank_credible"]
    for s in samples
)
retained = [s["rank_profile"][1 : s["N"]] for s in samples]
assert all(len(r) >= 3 and len(set(r)) == 1 for r in retained)
assert len({r[0] for r in retained}) == 1
certificate = selected_scope["certificate"]
rank_search = {
    "status": "confirmed",
    "boundary_exclusions": {"left": 1, "right": 1},
    "rank": retained[0][0],
    "confirmed_horizons": sorted(s["N"] for s in samples),
    "selected_certificate_id": certificate["certificate_id"],
    "recipe_id": samples[0]["recipe_id"],
    "rank_convention": samples[0]["rank_convention"],
    "unresolved_samples": [],
    "evidence_path": "supplementary/rank_search.json",
}
(root / "supplementary/rank_search.json").write_text(
    json.dumps({"summary": rank_search, "samples": samples}, indent=2)
)
vals = [selected_scope["pm"].eval_scalar(v) for v in selected_scope["lyap"]]
b3 = {
    **certificate,
    "rank_profile": selected_scope["ranks"],
    "rank_search": rank_search,
    "lyap_inner_prod_coords": [
        np.asarray(v.inner_prod_coords, dtype=float).tolist() for v in vals
    ],
    "lyap_func_coords": [np.asarray(v.func_coords, dtype=float).tolist() for v in vals],
    "lyap_offsets": [float(v.offset) for v in vals],
    "certificate_check_code": sources[0],
    "decomposition_code": sources[1],
    "grouping_code": sources[2],
    "extra_duals": selected_scope["extra_duals"],
    "rank_tolerance": 1e-4,
    "reconstruction_tolerance": 1e-4,
    "reconstruction_rtol": 1e-5,
    "grouping_coverage": {
        "constraint_assignment": selected_scope["term_assignment"],
        "S_assignment": selected_scope["S_assignment"],
        "normalization_constraint": "initial_condition",
        "boundary_constraints": selected_scope["boundary_names"],
        "boundary_S": selected_scope["boundary_S"],
        "omitted_constraints": [],
        "checked": True,
    },
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
}
(root / "state/feg_b3.json").write_text(json.dumps(b3, indent=2, allow_nan=False))
print("Confirmed rank summary", rank_search)
