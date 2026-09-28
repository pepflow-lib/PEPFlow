import json
import os
import runpy
import sys
from pathlib import Path

root = Path.cwd().resolve()
sys.path.insert(0, str(root / "supplementary/helpers"))
from runtime import (  # ty: ignore[unresolved-import]  # Runtime bootstrap adds the archived helper directory to sys.path.  # noqa: E402 -- Initialize paths and runtime environment before importing.
    configure,
)

configure()
os.environ["MPLBACKEND"] = "Agg"
from certificate import (  # ty: ignore[unresolved-import]  # Runtime bootstrap adds the archived helper directory to sys.path.  # noqa: E402 -- Initialize paths and runtime environment before importing.
    verify_certificate,
)
from partial_sums import (  # ty: ignore[unresolved-import]  # Runtime bootstrap adds the archived helper directory to sys.path.  # noqa: E402 -- Initialize paths and runtime environment before importing.
    construct,
    rebuild,
)

out = {}
for n, cpath, dpath in [
    (4, "state/ogm_b2.json", "state/ogm_dense.json"),
    (6, "supplementary/b2-certificate-N6.json", "supplementary/b2-dense-N6.json"),
]:
    c = json.loads((root / cpath).read_text())
    d = json.loads((root / dpath).read_text())
    ctx, pb, obj, pm = rebuild(c)
    checks, residual = verify_certificate(ctx, pb, c, d["opt_value"])
    assert checks["passed"]
    ob = construct(c, False)
    out[str(n)] = {
        "certificate": checks,
        "ranks": ob["rank_profile"],
        "coverage": ob["coverage_max_abs"],
        "increments": ob["increment_errors"],
        "rank_credible": ob["rank_credible"],
    }
b4 = runpy.run_path(str(root / "supplementary/b4_math.py"))
out["B4"] = {
    "quadratic": b4["quadratic_residuals"],
    "components": b4["component_residuals"],
    "search": b4["search_results"],
}
b5 = runpy.run_path(str(root / "supplementary/b5_math.py"))
out["B5"] = b5["proof_results"]
(root / "review-replay.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
