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

import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
from ogm_setup import (  # noqa: E402, F401 -- Required by exec of ogm_b4.json#certificate_check_code. Paths initialized above.
    theta_sequence,
)

b4 = json.loads((root / "state/ogm_b4.json").read_text())
certificate = b4
for field in (
    "certificate_check_code",
    "decomposition_code",
    "grouping_code",
    "basis_code",
):
    exec(compile(b4[field], field, "exec"))
coeff_by_k = {
    int(k): np.asarray(C, dtype=float).reshape(len(C), len(C))
    for k, C in b4["coeff_by_k"].items()
}
exec(compile(b4["structure_code"], "structure_code", "exec"))
for name in (
    "b5_symbolic_helpers.py",
    "b5_step.py",
    "b5_base.py",
    "b5_terminal.py",
    "b5_small_normalization.py",
):
    exec(
        compile(
            (root / "supplementary" / name).read_text(encoding="utf-8-sig"),
            name,
            "exec",
        )
    )
(root / "supplementary/b5-symbolic-results.json").write_text(
    json.dumps(symbolic_results, indent=2)
)
print("Every exact symbolic component vanished.")
