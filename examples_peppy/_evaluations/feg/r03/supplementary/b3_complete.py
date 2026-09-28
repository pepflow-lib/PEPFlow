import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
import sympy as sp
import pepflow as pf
from feg_setup import get_pep_setup
ROOT=runtime.ROOT
REPO_ROOT=ROOT/'supplementary/approved'
notebook_dir=ROOT
certificate_check_code=(ROOT/'supplementary/b3_certificate_check.py').read_text()
decomposition_code=(ROOT/'supplementary/b3_decomposition.py').read_text()
grouping_code=(ROOT/'supplementary/b3_grouping.py').read_text()
rank_samples=[]
for sample_path in [ROOT/'supplementary/b2-N6.json',ROOT/'state/feg_b2.json']:
    certificate=json.loads(sample_path.read_text())
    N_int=certificate['N_verify']
    N=sp.S(N_int)
    params_sp={k:sp.S(v) for k,v in json.loads(certificate['params_json']).items()}
    ctx,pb,obj=get_pep_setup(N,params_sp)
    pb.set_relaxed_constraints(certificate['relaxed_constraints'])
    ctx.set_as_current()
    exec(certificate_check_code)
    exec(decomposition_code)
    exec(grouping_code)
    profile=dict(N=N_int,certificate_id=certificate['certificate_id'],certificate_path=str(sample_path.relative_to(ROOT)).replace('\\','/'),recipe_id='consecutive_monotone_and_halfstep_lipschitz_terminal_S_v1',rank_profile=ranks,singular_values=singular_values,rank_convention=dict(tolerance=1e-4,scaling='none; absolute tolerance on original Gram coordinates',coordinate_order='setup earlier iterates first'),rank_credible=all(not (0.5e-4<=v<=2e-4) for values in singular_values for v in values),certificate_checked=certificate_checked,grouping_checked=grouping_checked,boundary_exclusions=dict(left=1,right=1),term_assignment=term_assignment,S_assignment=S_assignment)
    (ROOT/f'supplementary/b3-rank-N{N_int}.json').write_text(json.dumps(profile,indent=2))
    rank_samples.append(profile)
workflow=(ROOT/'supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text(encoding='utf-8')
assess_source='def assess_rank_pattern'+workflow.split('```python\ndef assess_rank_pattern',1)[1].split('```',1)[0]
exec(assess_source)
rank_search=assess_rank_pattern(rank_samples,certificate['certificate_id'],left=1,right=1)
assert rank_search['status']=='confirmed'
rank_search['evidence_path']='supplementary/rank_search.json'
(ROOT/'supplementary/rank_search.json').write_text(json.dumps(dict(summary=rank_search,samples=rank_samples),indent=2))
evaluated=[pm.eval_scalar(v) for v in lyap]
state={**certificate,'rank_profile':ranks,'rank_search':rank_search,'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in evaluated],'lyap_func_coords':[np.asarray(v.func_coords,dtype=float).tolist() for v in evaluated],'lyap_offsets':[float(v.offset) for v in evaluated],'certificate_check_code':certificate_check_code,'decomposition_code':decomposition_code,'grouping_code':grouping_code,'extra_duals':extra_duals,'rank_tolerance':rank_tolerance,'reconstruction_tolerance':tol['reconstruction_atol'],'reconstruction_rtol':tol['reconstruction_rtol'],'grouping_coverage':dict(constraint_assignment=term_assignment,S_assignment=S_assignment,normalization_constraint=tau_name,boundary_constraints=boundary_names,boundary_S=boundary_S,omitted_constraints=[],checked=grouping_checked),'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
(ROOT/'state/feg_b3.json').write_text(json.dumps(state,indent=2,allow_nan=False))
(ROOT/'supplementary/b3_assess_rank.py').write_text(assess_source)
print(json.dumps(rank_search,indent=2))
