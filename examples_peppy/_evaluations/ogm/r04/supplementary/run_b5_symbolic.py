import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from runtime import configure
notebook_dir,REPO_ROOT=configure()
import json
import sympy as sp
import numpy as np
import pepflow as pf
certificate=json.loads((notebook_dir/'state/ogm_b4.json').read_text())
# This isolated proof probe checks the symbolic identities. Full replay occurs in final notebook.
source=(notebook_dir/'supplementary/b5_symbolic_cells.py').read_text(encoding='utf-8-sig')
source=source[source.index('L_sym, t_sym'):]
exec(compile(source,'b5_symbolic_cells.py','exec'))
