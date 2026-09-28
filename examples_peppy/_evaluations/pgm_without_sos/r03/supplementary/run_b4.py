import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("runtime.py")))
import json  # noqa: E402, F401 -- Required by exec of b3_visible.py. Paths initialized above.

from pgm_setup import (  # noqa: E402, F401 -- Required by exec of b3_visible.py. Paths initialized above.
    get_pep_setup,
)

NOTEBOOK_DIR = Path.cwd()
REPO_ROOT = NOTEBOOK_DIR / "supplementary/approved"
exec(
    compile(
        (NOTEBOOK_DIR / "supplementary/b3_visible.py").read_text(), "b3_visible", "exec"
    )
)
for part in ("load", "scan", "search", "basis", "coefficients", "structure"):
    exec(
        compile(
            (NOTEBOOK_DIR / f"supplementary/b4_{part}.py").read_text(
                encoding="utf-8-sig"
            ),
            part,
            "exec",
        )
    )
