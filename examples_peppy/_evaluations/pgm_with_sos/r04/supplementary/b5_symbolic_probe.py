from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import numpy as np
import sympy as sp
import pepflow as pf

exec((runtime.ROOT/'supplementary/b5_symbolic_cells.py').read_text(encoding='utf-8-sig'))
