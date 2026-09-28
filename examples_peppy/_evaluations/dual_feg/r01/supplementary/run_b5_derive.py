import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))

import runtime

notebook_dir = runtime.ATTEMPT
p = notebook_dir / "supplementary/run_b4_scan.py"
# Revalidation and reconstruction only; the basis scan is already verified.
code = p.read_text(encoding="utf-8-sig").split(
    "p=notebook_dir/'supplementary/b4_scan_cells.py'", 1
)[0]
exec(compile(code, str(p), "exec"))
p = notebook_dir / "supplementary/b5_derive.py"
exec(compile(p.read_text(encoding="utf-8-sig"), str(p), "exec"))
