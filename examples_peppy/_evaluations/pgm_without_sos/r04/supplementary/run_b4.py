from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
source=(runtime.ATTEMPT/'supplementary/explore_b4.py').read_text(encoding='utf-8-sig')
exec(compile(source[:source.index('for k in range(1,N_int):')],'b4_rebuild','exec'))
source=(runtime.ATTEMPT/'supplementary/b4_cells.py').read_text(encoding='utf-8-sig')
exec(compile(source,'b4_cells.py','exec'))
