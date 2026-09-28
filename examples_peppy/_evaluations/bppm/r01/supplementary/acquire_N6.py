# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import runtime

import pepflow as pf  # noqa: F401 -- Required by exec of b2_verification.py.

# Preserve the recorded import initialization order.
# isort: split
from bppm_setup import (  # noqa: F401 -- Required by exec of b2_verification.py.
    get_pep_setup,
)

# local helper resolved by the notebook runtime path
from certificate import solve_capture  # ty: ignore[unresolved-import]

notebook_dir = runtime.ROOT
folder = notebook_dir / "supplementary/N6"
folder.mkdir(exist_ok=True)
N = 6
_, _, _, _, dense = solve_capture(N)
(folder / "dense.json").write_text(json.dumps(dense, indent=2))
keep = {"initial_condition", f"h:x_star,x_{N}"}
keep.update(f"f:x_star,x_{k}" for k in range(1, N + 1))
keep.update(f"f:x_{k - 1},x_{k}" for k in range(2, N + 1))
keep.update(f"h:x_{k},x_{k - 1}" for k in range(1, N + 1))
keep.update(f"h:x_{k - 1},x_{k}" for k in range(2, N + 1))
relaxed = [name for name in dense["named_dual_values"] if name not in keep]
_, _, _, _, certificate = solve_capture(N, relaxed)
(folder / "relaxed-raw.json").write_text(json.dumps(certificate, indent=2))
source = (notebook_dir / "supplementary/b2_verification.py").read_text(
    encoding="utf-8-sig"
)
source = source.replace(
    "dense = json.loads((notebook_dir / 'state/bppm_dense.json').read_text())",
    "dense = json.loads((notebook_dir / 'supplementary/N6/dense.json').read_text())",
)
source = source.replace(
    "certificate = json.loads((notebook_dir / 'state/bppm_relaxed.json').read_text())",
    "certificate = json.loads((notebook_dir / 'supplementary/N6/relaxed-raw.json').read_text())",
)
source = source.replace(
    "Exact candidate identity at N=4, alpha=R=1",
    "Exact candidate identity at N=6, alpha=R=1",
)
(folder / "verification.py").write_text(source)
exec(compile(source, "N6/verification.py", "exec"))
saver = (notebook_dir / "supplementary/save_b2.py").read_text(encoding="utf-8-sig")
saver = saver[
    saver.index("state={**b1,**certificate}") : saver.index(
        "for filename in ('bppm_b2.json'"
    )
]
exec(compile(saver, "N6/state_capture", "exec"))
state["notebook_selected_horizon"] = 4
state["closed_form_search"]["reused_from"] = (
    "state/bppm_b2.json; candidate formulas rechecked at N=6"
)
(folder / "certificate.json").write_text(json.dumps(state, indent=2, allow_nan=False))
print("Additional complete certificate saved:", state["certificate_id"])
print("Numerical checks:", state["numerical_checks"])
