import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import numpy as np
root=Path(__file__).resolve().parents[1]
for name in ('derivation','step','base','boundary'):
    exec((root/f'supplementary/b5_{name}_cell.py').read_text(encoding='utf-8-sig'))
