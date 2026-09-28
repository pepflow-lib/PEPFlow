"""Replay the selected numerical certificate and partial-sum recipe without solving."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

notebook_dir=Path(__file__).resolve().parents[1]
REPO_ROOT=notebook_dir/'supplementary/approved'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
for key in ('TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME'):
    path=notebook_dir/'supplementary/.runtime'/key.lower()
    path.mkdir(parents=True,exist_ok=True)
    os.environ[key]=str(path)
sys.path[:0]=[str(REPO_ROOT),str(notebook_dir/'supplementary/helpers')]
import numpy as np
import pepflow as pf
import sympy as sp
from certificate_tools import certificate_id, inventory, verify_certificate, scalar_from_gram

selected=sys.argv[1] if len(sys.argv)>1 else 'state/bppm_b2.json'
certificate=json.loads((notebook_dir/selected).read_text())
N_int=certificate['N_verify']
params_sp={k:sp.S(v) for k,v in json.loads(certificate['params_json']).items()}
spec=importlib.util.spec_from_file_location('bppm_setup',notebook_dir/'bppm_setup.py')
assert spec is not None and spec.loader is not None
setup=importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
ctx,pb,obj=setup.get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
sources={}
for kind in ('certificate_check','decomposition','grouping'):
    source=(notebook_dir/f'supplementary/b3_{kind}.py').read_text()
    sources[kind+'_code']=source
    exec(compile(source,f'b3_{kind}.py','exec'))
coords=[pm.eval_scalar(v) for v in lyap]
trial={**sources,'N':N_int,'certificate_id':certificate['certificate_id'],'certificate_path':selected,
       'recipe_id':'adjacent-step-full-S-boundary-v1','rank_profile':ranks,
       'rank_convention':{'tolerance':1e-4,'scaling':'absolute, unscaled matrix','coordinate_order':'original context basis order'},
       'rank_credible':bool(rank_credible),'certificate_checked':bool(certificate_checked),'grouping_checked':bool(grouping_checked),
       'singular_values':singular_values,'coverage_residuals':coverage_residuals,
       'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in coords],
       'lyap_func_coords':[np.asarray(v.func_coords,dtype=float).tolist() for v in coords],
       'lyap_offsets':[float(v.offset) for v in coords],
       'grouping_coverage':{'constraint_assignment':term_assignment,'S_assignment':S_assignment,
           'normalization_constraint':tau_name,'boundary_constraints':boundary_names,'boundary_S':boundary_S,
           'omitted_constraints':[],'checked':bool(grouping_checked)}}
out=notebook_dir/f'supplementary/b3-trial-N{N_int}.json'
out.write_text(json.dumps(trial,indent=2))
print('Trial saved:',out)
