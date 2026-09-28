import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import numpy as np
import pepflow as pf
from pgm_setup import get_pep_setup,f,g
NOTEBOOK_DIR=Path.cwd()
REPO_ROOT=NOTEBOOK_DIR/'supplementary/approved'
exec(compile((NOTEBOOK_DIR/'supplementary/b3_visible.py').read_text(),'b3_visible','exec'))
for part in ('load','scan','search','basis','coefficients','structure'):
    exec(compile((NOTEBOOK_DIR/f'supplementary/b4_{part}.py').read_text(encoding='utf-8-sig'),part,'exec'))
