import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from runtime import configure
notebook_dir,REPO_ROOT = configure()
import json
import numpy as np
import sympy as sp
import pepflow as pf
from ogm_setup import get_pep_setup,theta_sequence
certificate = json.loads((notebook_dir/'state/ogm_b3.json').read_text())
N_int=certificate['N_verify']
params_sp={k:sp.S(v) for k,v in json.loads(certificate['params_json']).items()}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
for field in ('certificate_check_code','decomposition_code','grouping_code'):
    exec(compile(certificate[field],field,'exec'))
source=(notebook_dir/'supplementary/b4_cells.py').read_text(encoding='utf-8-sig')
exec(compile(source,'b4_cells.py','exec'))
