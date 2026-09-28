"""B2 dense acquisition and compact structural output."""

import json
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "supplementary/helpers"))
    # local helper resolved by the notebook runtime path
    from runtime import configure  # ty: ignore[unresolved-import]

    configure()
    import numpy as np

    # local helper resolved by the notebook runtime path
    from certificate import capture  # ty: ignore[unresolved-import]

    data = capture(4)
    (root / "state/ogm_dense.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )
    print("Dense bound:", data["opt_value"])
    print("Basis:", data["basis_vectors"])
    print("S eigenvalues:", np.linalg.eigvalsh(data["S_matrix"]))
    print("Nonzero dual entries:")
    for name, value in data["named_dual_values"].items():
        if value is not None and abs(value) > 1e-6:
            print(name, value)
    print("Checks:", data["numerical_checks"])


if __name__ == "__main__":
    main()
