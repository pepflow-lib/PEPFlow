"""Dense and threshold-relaxed certificate acquisition in B2."""

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
    from certificate import capture  # ty: ignore[unresolved-import]
    from pgm_setup import get_pep_setup

    params = {"L": 1, "R": 1}
    ctx, pb, obj = get_pep_setup(4, params)
    dense = capture(ctx, pb, obj, params)
    (root / "state/pgm_dense.json").write_text(json.dumps(dense, indent=2))
    print("Dense", dense["opt_value"], dense["numerical_checks"], flush=True)
    for name, value in dense["named_dual_values"].items():
        if value is not None and abs(value) > 1e-5:
            print(name, round(value, 8))
    dropped = [
        name
        for name, value in dense["named_dual_values"].items()
        if value is not None
        and abs(value) < 1e-6
        and dense["constraint_metadata"][name]["origin"] == "interpolation"
    ]
    ctx, pb, obj = get_pep_setup(4, params)
    pb.set_relaxed_constraints(dropped)
    relaxed = capture(ctx, pb, obj, params, dense["opt_value"])
    (root / "supplementary/b2-threshold.json").write_text(json.dumps(relaxed, indent=2))
    print("Dropped", dropped)
    print("Relaxed", relaxed["opt_value"], relaxed["numerical_checks"], flush=True)


if __name__ == "__main__":
    main()
