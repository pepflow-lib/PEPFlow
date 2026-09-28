import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import sympy as sp
import pepflow as pf
from feg_setup import get_pep_setup
notebook_dir=Path(__file__).resolve().parents[1]
REPO_ROOT=notebook_dir/'supplementary/approved'
certificate=json.loads((notebook_dir/'state/feg_b3.json').read_text())
N_int=certificate['N_verify']
params_sp={'L':sp.Integer(1),'R':sp.Integer(1)}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
for field in ('certificate_check_code','decomposition_code','grouping_code'):
    exec(certificate[field])
for name in ('sanity','candidates','filter','search','basis','coefficients','structure'):
    exec((notebook_dir/f'supplementary/b4_{name}.py').read_text(encoding='utf-8-sig'))
