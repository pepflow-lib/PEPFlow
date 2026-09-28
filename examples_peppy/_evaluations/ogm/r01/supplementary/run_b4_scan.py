import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "supplementary/helpers"))
import runtime  # noqa: E402, F401 -- Initialize approved paths and runtime settings before exec fragments. Paths initialized above.

# Preserve the recorded import initialization order.
# isort: split
import json  # noqa: E402 - imports follow runtime or notebook setup

certificate = json.loads((root / "state/ogm_b3.json").read_text())
for field in ("certificate_check_code", "decomposition_code", "grouping_code"):
    exec(compile(certificate[field], field, "exec"))
exec(
    compile(
        (root / "supplementary/b4_scan.py").read_text(encoding="utf-8-sig"),
        "b4_scan.py",
        "exec",
    )
)
