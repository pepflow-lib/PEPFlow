"""Recompute cross-horizon B3 evidence with coverage and sign checks."""

import json
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path[:0] = [
        str(root / "supplementary/approved"),
        str(root / "supplementary/h"),
        str(root),
    ]
    # local helper resolved by the notebook runtime path
    from runtime import configure  # ty: ignore[unresolved-import]

    configure()
    # local helper resolved by the notebook runtime path
    from partial_sums import construct, rebuild_check  # ty: ignore[unresolved-import]
    from pgm_setup import get_pep_setup

    samples = []
    for path in ("state/pgm_b2.json", "supplementary/b2_n6.json"):
        state = json.loads((root / path).read_text())
        ctx, pb, _, _ = rebuild_check(root, state, get_pep_setup)
        _, _, _, record = construct(ctx, pb, state, verbose=True)
        samples.append(record)
        print(
            "Coverage / boundary:",
            record["coverage_max_abs"],
            record["boundary_max_abs"],
        )
    retained = [s["rank_profile"][1:-1] for s in samples]
    confirmed = (
        all(s["rank_credible"] for s in samples)
        and all(len(r) >= 3 and len(set(r)) == 1 for r in retained)
        and len({r[0] for r in retained}) == 1
    )
    print("Cross-horizon confirmed:", confirmed)
    (root / "supplementary/rank_search.json").write_text(
        json.dumps(
            {
                "summary": {
                    "status": "confirmed" if confirmed else "inconsistent",
                    "boundary_exclusions": {"left": 1, "right": 1},
                    "rank": retained[0][0] if confirmed else None,
                    "confirmed_horizons": [s["N"] for s in samples]
                    if confirmed
                    else [],
                    "selected_certificate_id": samples[0]["certificate_id"],
                    "recipe_id": samples[0]["recipe_id"],
                    "rank_convention": samples[0]["rank_convention"],
                    "evidence_path": "supplementary/rank_search.json",
                },
                "samples": samples,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
