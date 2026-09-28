import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("runtime.py")))
import hashlib  # noqa: E402 - imports follow runtime or notebook setup
import json  # noqa: E402 - imports follow runtime or notebook setup

from certificate_solver import (  # noqa: E402 - imports follow runtime or notebook setup
    ROOT,
    solve_capture,
)

folder = ROOT / "supplementary/N8"
folder.mkdir(exist_ok=True)
allowlist = json.loads((ROOT / "supplementary/approved/allowlist.json").read_text())
paths = [
    Path(p)
    for p in allowlist["exact_read_files"]
    if Path(p).parent == ROOT / "supplementary/approved/pepflow"
] + [ROOT / "feg_setup.py", ROOT / "supplementary/certificate_solver.py"]
hashes = {
    p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in paths
}
ctx, pb, op, result, dense = solve_capture(8)
(folder / "feg_dense.json").write_text(json.dumps(dense, indent=2))
keep = {"initial_condition", "A monotone:x_8,x_star", "A Lipschitz:x_1,x_1/2"}
for k in range(1, 8):
    keep.add(f"A monotone:x_{k},x_{k + 1}")
    keep.add(f"A Lipschitz:x_{k}+1/2,x_{k + 1}")
relaxed = [name for name in dense["named_dual_values"] if name not in keep]
ctx, pb, op, result, selected = solve_capture(8, relaxed)
assert hashes == {
    p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in paths
}
selected["source_hashes_before_and_after_solve"] = hashes
(folder / "selected-raw.json").write_text(json.dumps(selected, indent=2))
print(
    "N8 dense:",
    dense["opt_value"],
    dense["solver_status"],
    "selected:",
    selected["opt_value"],
    selected["solver_status"],
)
