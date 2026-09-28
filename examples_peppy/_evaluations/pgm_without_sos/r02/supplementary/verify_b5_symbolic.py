import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

source = (runtime.ROOT / "supplementary/b5_symbolic_cells.py").read_text(
    encoding="utf-8-sig"
)
exec(compile(source, "b5_symbolic_cells.py", "exec"))
