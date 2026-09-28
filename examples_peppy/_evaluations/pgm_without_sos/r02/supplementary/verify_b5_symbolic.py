import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
source=(runtime.ROOT/'supplementary/b5_symbolic_cells.py').read_text(encoding='utf-8-sig')
exec(compile(source,'b5_symbolic_cells.py','exec'))
