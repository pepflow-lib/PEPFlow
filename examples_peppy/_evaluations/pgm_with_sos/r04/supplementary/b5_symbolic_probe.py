import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# Preserve the recorded import initialization order.
# isort: split
import numpy as np  # noqa: F401 -- Required by exec of b5_symbolic_cells.py.
import sympy as sp  # noqa: F401 -- Required by exec of b5_symbolic_cells.py.

import pepflow as pf  # noqa: F401 -- Required by exec of b5_symbolic_cells.py.

exec(
    (runtime.ROOT / "supplementary/b5_symbolic_cells.py").read_text(
        encoding="utf-8-sig"
    )
)
