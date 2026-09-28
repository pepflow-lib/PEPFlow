import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import runtime

# local helper resolved by the notebook runtime path
from certificate import acquire  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
n = 8
dense = acquire(n, [], root)
(root / "supplementary/b2-n8-dense.json").write_text(json.dumps(dense, indent=2))
print(
    "N8 dense",
    dense["opt_value"],
    dense["certificate_provenance"]["solver_status"],
    flush=True,
)
keep = {f"A monotone:x_{n},x_star"}
keep.update(f"A monotone:x_{n},y_{k}" for k in range(n - 1))
keep.update(f"A Lipschitz:x_{k},y_{k}" for k in range(n - 1))
keep.add(f"A Lipschitz:x_{n - 1},x_{n}")
relaxed = [
    name
    for name, meta in dense["constraint_metadata"].items()
    if meta["origin"] == "interpolation" and name not in keep
]
selected = acquire(n, relaxed, root)
(root / "supplementary/b2-n8-sparse.json").write_text(json.dumps(selected, indent=2))
print(
    "N8 sparse",
    selected["opt_value"],
    selected["certificate_provenance"]["solver_status"],
    flush=True,
)
notebook_dir = root
p = root / "supplementary/b2_certificate_cells.py"
code = p.read_text(encoding="utf-8-sig")
code = (
    code.replace("state/dual_feg_dense.json", "supplementary/b2-n8-dense.json")
    .replace(
        "supplementary/b2_sparse_candidate.json", "supplementary/b2-n8-sparse.json"
    )
    .replace(
        "(notebook_dir/'state'/filename)",
        "(notebook_dir/'supplementary'/('n8-'+filename))",
    )
)
(root / "supplementary/b2-n8-verification-source.py").write_text(code, encoding="utf-8")
exec(compile(code, str(root / "supplementary/b2-n8-verification-source.py"), "exec"))
