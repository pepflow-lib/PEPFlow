from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
source=(runtime.ATTEMPT/'supplementary/run_b4.py').read_text(encoding='utf-8-sig')
exec(compile(source,'run_b4.py','exec'))
source=(runtime.ATTEMPT/'supplementary/b5_cells.py').read_text(encoding='utf-8-sig')
exec(compile(source,'b5_cells.py','exec'))
