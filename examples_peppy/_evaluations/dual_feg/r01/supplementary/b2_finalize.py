import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
notebook_dir=runtime.ATTEMPT
code=(notebook_dir/'supplementary/b2_certificate_cells.py').read_text(encoding='utf-8-sig')
exec(compile(code,str(notebook_dir/'supplementary/b2_certificate_cells.py'),'exec'))
