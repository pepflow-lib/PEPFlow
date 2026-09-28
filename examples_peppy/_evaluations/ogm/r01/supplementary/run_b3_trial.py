# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "supplementary/helpers"))
import runtime  # noqa: E402, F401 -- Initialize approved paths and runtime settings before exec fragments. Paths initialized above.

# Preserve the recorded import initialization order.
# isort: split
import json  # noqa: E402 - imports follow runtime or notebook setup

certificate = json.loads((root / "state/ogm_b2.json").read_text())
for filename in ("b3_certificate_check.py", "b3_decomposition.py", "b3_grouping.py"):
    exec(
        compile(
            (root / "supplementary" / filename).read_text(encoding="utf-8-sig"),
            filename,
            "exec",
        )
    )
sample = dict(
    N=N_int,
    certificate_id=certificate["certificate_id"],
    recipe_id="star-through-k-consecutive-through-k-terminal-square-boundary",
    rank_profile=ranks,
    rank_convention=dict(
        tolerance=rank_tolerance,
        scaling="unscaled Gram coordinates",
        coordinate_order="x0,xstar,g0,...,gN",
    ),
    rank_credible=rank_credible,
    certificate_checked=certificate_checked,
    grouping_checked=grouping_checked,
    singular_values=singular_values,
    coverage_residual=coverage_residual,
)
(root / "supplementary/b3-rank-N4.json").write_text(json.dumps(sample, indent=2))
print(json.dumps(sample, indent=2))
