"""Confirm the partial-sum recipe at N=4 and N=6 and prepare B3 state."""

import inspect
import json
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "supplementary/helpers"))
    # local helper resolved by the notebook runtime path
    from runtime import configure  # ty: ignore[unresolved-import]

    configure()
    # local helper resolved by the notebook runtime path
    from partial_sums import construct, rebuild  # ty: ignore[unresolved-import]

    selected = json.loads((root / "state/ogm_b2.json").read_text())
    additional = json.loads((root / "supplementary/b2-certificate-N6.json").read_text())
    samples = [construct(c) for c in (selected, additional)]
    for sample in samples:
        assert (
            sample["rank_credible"]
            and sample["certificate_checked"]
            and sample["grouping_checked"]
        )
        retained = sample["rank_profile"][1:-1]
        assert len(retained) >= 3 and len(set(retained)) == 1
    assert samples[0]["rank_profile"][1] == samples[1]["rank_profile"][1]
    assert samples[0]["recipe_id"] == samples[1]["recipe_id"]
    assert samples[0]["rank_convention"] == samples[1]["rank_convention"]
    rank_search = {
        "status": "confirmed",
        "boundary_exclusions": {"left": 1, "right": 1},
        "rank": samples[0]["rank_profile"][1],
        "confirmed_horizons": [4, 6],
        "selected_certificate_id": selected["certificate_id"],
        "recipe_id": samples[0]["recipe_id"],
        "rank_convention": samples[0]["rank_convention"],
        "unresolved_samples": [],
        "evidence_path": "supplementary/rank_search.json",
    }
    (root / "supplementary/rank_search.json").write_text(
        json.dumps(
            {"summary": rank_search, "samples": samples}, indent=2, allow_nan=False
        ),
        encoding="utf-8",
    )
    for sample in samples:
        (root / f"supplementary/b3-observation-N{sample['N']}.json").write_text(
            json.dumps(sample, indent=2, allow_nan=False), encoding="utf-8"
        )
    observation = samples[0]
    construct_source = inspect.getsource(construct)
    decomposition_source = construct_source[
        construct_source.index("    S = np.asarray") : construct_source.index(
            "    lyap ="
        )
    ]
    state = {
        **selected,
        "rank_profile": observation["rank_profile"],
        "rank_search": rank_search,
        "lyap_inner_prod_coords": [c["gram"] for c in observation["lyap_coordinates"]],
        "lyap_func_coords": [c["func"] for c in observation["lyap_coordinates"]],
        "lyap_offsets": [c["offset"] for c in observation["lyap_coordinates"]],
        "certificate_check_code": inspect.getsource(rebuild),
        "decomposition_code": decomposition_source,
        "grouping_code": construct_source,
        "replay_dependencies": [
            "supplementary/helpers/certificate.py",
            "supplementary/helpers/partial_sums.py",
        ],
        "extra_duals": {},
        "rank_tolerance": 1e-4,
        "reconstruction_tolerance": 1e-4,
        "reconstruction_rtol": 1e-5,
        "grouping_coverage": {
            "constraint_assignment": observation["constraint_assignment"],
            "S_assignment": observation["S_assignment"],
            "normalization_constraint": "initial_condition",
            "boundary_constraints": [],
            "boundary_S": [],
            "omitted_constraints": [],
            "checked": True,
        },
        "grouping_checks": {
            "coverage_max_abs": observation["coverage_max_abs"],
            "increment_errors": observation["increment_errors"],
            "sign_convention": observation["sign_convention"],
        },
        "numerical_certificate_verified": True,
        "analytic_full_pep_verified": False,
        "lyapunov_proof_verified": False,
    }
    (root / "state/ogm_b3.json").write_text(
        json.dumps(state, indent=2, allow_nan=False), encoding="utf-8"
    )
    print("Cross-horizon confirmation:", rank_search)


if __name__ == "__main__":
    main()
