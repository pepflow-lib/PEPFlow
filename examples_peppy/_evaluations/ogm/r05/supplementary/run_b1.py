"""One-time B1 numerical sweep; preserve the actual solve outputs."""

import json
import sys
from pathlib import Path


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
    # local helper resolved by the notebook runtime path
    from runtime import (  # ty: ignore[unresolved-import]
        NOTEBOOK_DIR,
        configure,
        solve_pep,
    )

    configure()
    from ogm_setup import get_pep_setup, theta_sequence

    results = []
    for N in range(1, 8):
        ctx, pb, obj = get_pep_setup(N, {"L": 1, "R": 1})
        result, calls = solve_pep(ctx, pb, obj, {"L": 1, "R": 1})
        row = {
            "N": N,
            "opt_value": float(result.opt_value),
            "theta_N": theta_sequence(N)[-1],
            "solver_calls": calls,
        }
        results.append(row)
        print(json.dumps(row), flush=True)
        (NOTEBOOK_DIR / "supplementary" / "b1_sweep.json").write_text(
            json.dumps(results, indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
