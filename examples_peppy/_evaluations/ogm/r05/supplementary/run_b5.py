"""Run exact proof calculations independently and preserve component evidence."""

import json
import runpy
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "supplementary/helpers"))
    # local helper resolved by the notebook runtime path
    from runtime import configure  # ty: ignore[unresolved-import]

    configure()
    data = runpy.run_path(str(root / "supplementary/b5_math.py"))
    (root / "supplementary/b5-symbolic-evidence.json").write_text(
        json.dumps(data["proof_results"], indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
