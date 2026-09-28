"""Confirm rank consistency and preserve exact replay sources."""

import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supplementary"))
import group_b3  # noqa: E402 - imports follow runtime or notebook setup

selected = json.loads((ROOT / "state/dual_feg_b2.json").read_text())
other = json.loads((ROOT / "supplementary/certificate_N8.json").read_text())
samples = [group_b3.group(s) for s in [selected, other]]
for sample in samples:
    print(sample["N"], sample["rank_profile"], sample["rank_credible"], flush=True)
    (ROOT / f"supplementary/rank_N{sample['N']}.json").write_text(
        json.dumps(sample, indent=2)
    )
left = right = 1
retained = [s["rank_profile"][left : s["N"] + 1 - right] for s in samples]
assert all(len(r) >= 3 and len(set(r)) == 1 for r in retained)
assert len({r[0] for r in retained}) == 1
assert all(
    s["rank_credible"] and s["certificate_checked"] and s["grouping_checked"]
    for s in samples
)
assert samples[0]["rank_convention"] == samples[1]["rank_convention"]
summary = {
    "status": "confirmed",
    "boundary_exclusions": {"left": left, "right": right},
    "rank": retained[0][0],
    "confirmed_horizons": [s["N"] for s in samples],
    "selected_certificate_id": selected["certificate_id"],
    "recipe_id": samples[0]["recipe_id"],
    "rank_convention": samples[0]["rank_convention"],
    "unresolved_samples": [],
    "evidence_path": "supplementary/rank_search.json",
}
(ROOT / "supplementary/rank_search.json").write_text(
    json.dumps({"summary": summary, "samples": samples}, indent=2)
)
check_source = (
    "import hashlib\nimport json\nfrom pathlib import Path\nimport numpy as np\nimport pepflow as pf\nimport sympy as sp\nROOT = NOTEBOOK_DIR\nCERTIFICATE_KEYS = "
    + repr(group_b3.CERTIFICATE_KEYS)
    + "\n"
    + inspect.getsource(group_b3.recheck)
    + "\nctx,pb,obj,pm,weighted_terms,S_scalar,certificate_residuals = recheck(certificate)\ncertificate_checked = True\nN_int = certificate['N_verify']\n"
)
decomposition_source = """S_piece_terms = {"whole_S": S_scalar}
S_assignment = {"whole_S": "boundary"}
S_check = pm.eval_scalar(S_scalar)
assert np.max(np.abs(S_check.func_coords), initial=0) == 0
assert S_check.offset == 0
assert np.linalg.eigvalsh(np.asarray(S_check.inner_prod_coords, dtype=float)).min() >= -1e-6
"""
grouping_source = inspect.getsource(group_b3.group)
grouping_source += """
observation = group(certificate)
grouping_checked = observation["grouping_checked"]
ranks = observation["rank_profile"]
lyap = []
for coords, fcoords, offset in zip(observation["lyap_inner_prod_coords"], observation["lyap_func_coords"], observation["lyap_offsets"]):
    value = sum((float(coords[i][j])*ctx.basis_vectors()[i]*ctx.basis_vectors()[j] for i,j in np.ndindex(np.shape(coords))), pf.Scalar.zero())
    assert len(fcoords) == 0
    lyap.append(value + offset)
"""
state = {
    **selected,
    **{
        k: samples[0][k]
        for k in [
            "rank_profile",
            "lyap_inner_prod_coords",
            "lyap_func_coords",
            "lyap_offsets",
        ]
    },
    "rank_search": summary,
    "certificate_check_code": check_source,
    "decomposition_code": decomposition_source,
    "grouping_code": grouping_source,
    "extra_duals": {},
    "rank_tolerance": 1e-4,
    "reconstruction_tolerance": 1e-4,
    "reconstruction_rtol": 1e-5,
    "grouping_coverage": {
        "constraint_assignment": samples[0]["constraint_assignment"],
        "S_assignment": samples[0]["S_assignment"],
        "normalization_constraint": "initial_condition",
        "boundary_constraints": [f"A monotone:x_{selected['N']},x_star"],
        "boundary_S": ["whole_S"],
        "omitted_constraints": [],
        "checked": True,
    },
}
(ROOT / "state/dual_feg_b3.json").write_text(json.dumps(state, indent=2))
(ROOT / "supplementary/b3_check_source.py").write_text(check_source)
(ROOT / "supplementary/b3_decomposition_source.py").write_text(decomposition_source)
(ROOT / "supplementary/b3_grouping_source.py").write_text(grouping_source)
print("Confirmed", summary)
