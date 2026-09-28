import importlib.util
import json
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',root/'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import numpy as np
import sympy as sp
import pepflow as pf
import dual_feg_setup as setup
notebook_dir=root
REPO_ROOT=runtime.REPO_ROOT
certificate=json.loads((root/'state/dual_feg_b2.json').read_text())
N_int=certificate['N_verify']
N=sp.Integer(N_int)
params_sp: dict[str,pf.NUMERICAL_TYPE] = {'L':sp.Integer(1),'R':sp.Integer(1)}
ctx,pb,obj=setup.get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
sources={}
for name in ['b3_certificate_check.py','b3_decomposition.py','b3_grouping.py']:
    sources[name]=(root/'supplementary'/name).read_text(encoding='utf-8-sig')
    exec(sources[name])
workflow=(root/'supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text(encoding='utf-8')
assess=next(b for b in re.findall(r'```python\n(.*?)```',workflow,re.S) if b.startswith('def assess_rank_pattern'))
exec(assess)
samples=[json.loads((root/f'supplementary/b3-rank-N{n}.json').read_text()) for n in (4,6)]
rank_search=assess_rank_pattern(samples,certificate['certificate_id'],left=1,right=1)
assert rank_search['status']=='confirmed'
rank_search['evidence_path']='supplementary/rank_search.json'
(root/'supplementary/rank_search.json').write_text(json.dumps({'summary':rank_search,'samples':samples},indent=2))
evaluated=[pm.eval_scalar(v) for v in lyap]
state={**certificate,'rank_profile':ranks,'rank_search':rank_search,
'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in evaluated],
'lyap_func_coords':[np.asarray(v.func_coords,dtype=float).tolist() for v in evaluated],
'lyap_offsets':[float(v.offset) for v in evaluated],
'certificate_check_code':sources['b3_certificate_check.py'],'decomposition_code':sources['b3_decomposition.py'],'grouping_code':sources['b3_grouping.py'],
'extra_duals':extra_duals,'rank_tolerance':rank_tolerance,'reconstruction_tolerance':tol['reconstruction_atol'],'reconstruction_rtol':tol['reconstruction_rtol'],
'grouping_coverage':{'constraint_assignment':term_assignment,'S_assignment':S_assignment,'normalization_constraint':tau_name,'boundary_constraints':boundary_names,'boundary_S':boundary_S,'omitted_constraints':[],'checked':grouping_checked},
'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
(root/'state/dual_feg_b3.json').write_text(json.dumps(state,indent=2,allow_nan=False))
(root/'supplementary/b3_rank_assess.py').write_text(assess)
print(rank_search)
