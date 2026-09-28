import os,sys,json,hashlib
from pathlib import Path
root=Path.cwd().resolve()
for key in ('TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME'):
    p=root/'review_runtime'/key.lower();p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
sys.path[:0]=[str(root/'supplementary/approved'),str(root/'supplementary/h')]
import pepflow as pf
import sympy as sp
import numpy as np
assert Path(pf.__file__).resolve().is_relative_to(root/'supplementary/approved')
nb=json.loads((root/'pgm_example_lyap.ipynb').read_text())
notebook_dir=root
results={'executed_cells':[],'certificate_checks':{},'rank_samples':[]}
def run(i):
    print('REPLAY CELL',i,nb['cells'][i]['id'],flush=True)
    exec(compile(''.join(nb['cells'][i]['source']),f'notebook_cell_{i}','exec'),globals())
    results['executed_cells'].append(i)
for i in [7,9,14,24]:run(i)
certificate=json.loads((root/'state/pgm_b2.json').read_text())
for filename in ['state/pgm_b2.json','supplementary/b2_n6.json']:
    st=json.loads((root/filename).read_text())
    ctx,pb,obj,ck=rebuild_check(root,st,get_pep_setup)
    _,_,_,record=construct(ctx,pb,st)
    results['certificate_checks'][filename]=ck
    results['rank_samples'].append({k:record[k] for k in ['N','rank_profile','singular_values','rank_credible','coverage_max_abs','boundary_max_abs','increment_max_abs','recipe_id']})
for i in [29,31,32,34,36,38,39,42,44,45,49,52,55,58,61,63]:run(i)
results['basis_reconstruction']=component_residuals
results['coefficient_comparisons']=coefficient_comparisons
results['proof_checks']=proof_checks
results['passed']=True
(root/'replay_results.json').write_text(json.dumps(results,indent=2))
print('ALL REVIEW REPLAYS PASSED',flush=True)
