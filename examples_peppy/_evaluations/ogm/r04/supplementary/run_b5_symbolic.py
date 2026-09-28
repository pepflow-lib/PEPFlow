import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import configure  # ty: ignore[unresolved-import]

notebook_dir, REPO_ROOT = configure()
import json  # noqa: E402 - imports follow runtime or notebook setup

import sympy as sp  # noqa: E402, F401 -- Required by exec of b5_symbolic_cells.py#FROM_L_SYM. Paths initialized above.

# Preserve the recorded import initialization order.
# isort: split
import numpy as np  # noqa: E402, F401 -- Required by exec of b5_symbolic_cells.py#FROM_L_SYM. Paths initialized above.

import pepflow as pf  # noqa: E402, F401 -- Required by exec of b5_symbolic_cells.py#FROM_L_SYM. Paths initialized above.

certificate = json.loads((notebook_dir / "state/ogm_b4.json").read_text())
# This isolated proof probe checks the symbolic identities. Full replay occurs in final notebook.
source = (notebook_dir / "supplementary/b5_symbolic_cells.py").read_text(
    encoding="utf-8-sig"
)
source = source[source.index("L_sym, t_sym") :]
exec(compile(source, "b5_symbolic_cells.py", "exec"))
