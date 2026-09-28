import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("runtime.py")))
from pgm_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

scope = {"get_pep_setup": get_pep_setup}
exec(
    compile(
        Path("supplementary/b2_cells.py").read_text(encoding="utf-8-sig"),
        "b2_cells",
        "exec",
    ),
    scope,
)
