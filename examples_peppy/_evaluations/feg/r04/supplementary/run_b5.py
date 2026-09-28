import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import numpy as np

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
import sympy as sp

import pepflow as pf

root = runtime.ATTEMPT
b4 = json.loads((root / "state/feg_b4.json").read_text())
assert b4["numerical_reconstruction"]["certificate_id"] == b4["certificate_id"]
scope = {"np": np, "pf": pf, "sp": sp}
for filename in ("b5_derivation.py", "b5_step.py", "b5_base.py", "b5_boundary.py"):
    exec(
        compile(
            (root / "supplementary" / filename).read_text(encoding="utf-8-sig"),
            filename,
            "exec",
        ),
        scope,
    )
(root / "supplementary/b5-exact-checks.json").write_text(
    json.dumps(
        {name: scope[name] for name in ("step_check", "base_check", "boundary_check")},
        indent=2,
    )
)
