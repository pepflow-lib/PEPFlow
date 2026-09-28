import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from owned_runtime import ROOT, configure  # ty: ignore[unresolved-import]

configure()
exec((ROOT / "supplementary/replay_b4.py").read_text(encoding="utf-8-sig"))
notebook_dir = ROOT
exec(
    compile(
        (ROOT / "supplementary/b5_cells.py").read_text(encoding="utf-8-sig"),
        "b5_cells",
        "exec",
    )
)
