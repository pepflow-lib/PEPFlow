import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import NOTEBOOK_DIR, configure  # ty: ignore[unresolved-import]

configure()

import json  # noqa: E402 - imports follow runtime or notebook setup

import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from pgm_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)
from runtime import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    solve_explicit,
)

results = []
for n in range(1, 8):
    ctx, pb, _ = get_pep_setup(n, {"L": sp.S.One, "R": sp.S.One})
    result, log = solve_explicit(ctx, pb, {"L": sp.S.One, "R": sp.S.One})
    row = {"N": n, "opt_value": float(result.opt_value), **log}
    results.append(row)
    print(json.dumps(row), flush=True)
    (NOTEBOOK_DIR / "supplementary" / "_sweep_tmp.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
print("Inverse values:", [1 / row["opt_value"] for row in results])
