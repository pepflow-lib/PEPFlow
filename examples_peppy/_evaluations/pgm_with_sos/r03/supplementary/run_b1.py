import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
from runtime import configure, NOTEBOOK_DIR
configure()

import json
import sympy as sp
from pgm_setup import get_pep_setup
from runtime import solve_explicit

results = []
for n in range(1, 8):
    ctx, pb, _ = get_pep_setup(n, {"L": sp.S.One, "R": sp.S.One})
    result, log = solve_explicit(ctx, pb, {"L": sp.S.One, "R": sp.S.One})
    row = {"N": n, "opt_value": float(result.opt_value), **log}
    results.append(row)
    print(json.dumps(row), flush=True)
    (NOTEBOOK_DIR / "supplementary" / "_sweep_tmp.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8")
print("Inverse values:", [1 / row["opt_value"] for row in results])

