import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
root=runtime.ATTEMPT
for file in ('b5_common.py','b5_step.py','b5_base.py','b5_boundary.py','b5_small.py'):
    exec(compile((root/'supplementary'/file).read_text(),file,'exec'))
