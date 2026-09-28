import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
import bppm_setup as setup
notebook_dir=runtime.ROOT
REPO_ROOT=runtime.APPROVED
samples=[json.loads((notebook_dir/f'supplementary/b3-sample-N{n}.json').read_text()) for n in (4,6)]
for sample in samples:
    assert sample['certificate_checked'] and sample['grouping_checked'] and sample['rank_credible']
    assert len(sample['rank_profile'][1:-1])>=3 and set(sample['rank_profile'][1:-1])=={4}
    assert sample['recipe_id']==samples[0]['recipe_id'] and sample['rank_convention']==samples[0]['rank_convention']
certificate=json.loads((notebook_dir/'state/bppm_b2.json').read_text())
N_int=certificate['N_verify']
params_sp=json.loads(certificate['params_json'])
ctx,pb,obj=setup.get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
code=samples[0]['code']
for label in ('certificate_check','decomposition','grouping'):
    exec(compile(code[label],f'b3_{label}.py','exec'))
summary={'status':'confirmed','boundary_exclusions':{'left':1,'right':1},'rank':4,'confirmed_horizons':[4,6],
'selected_certificate_id':certificate['certificate_id'],'recipe_id':samples[0]['recipe_id'],'rank_convention':samples[0]['rank_convention'],'unresolved_samples':[],'evidence_path':'supplementary/rank_search.json'}
(notebook_dir/'supplementary/rank_search.json').write_text(json.dumps({'summary':summary,'samples':samples},indent=2))
evaluated=[pm.eval_scalar(v) for v in lyap]
state={**certificate,'rank_profile':ranks,'rank_search':summary,
'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in evaluated],
'lyap_func_coords':[np.asarray(v.func_coords,dtype=float).tolist() for v in evaluated],
'lyap_offsets':[float(v.offset) for v in evaluated],
'certificate_check_code':code['certificate_check'],'decomposition_code':code['decomposition'],'grouping_code':code['grouping'],
'extra_duals':extra_duals,'rank_tolerance':1e-4,'reconstruction_tolerance':1e-4,'reconstruction_rtol':1e-5,
'grouping_coverage':{'constraint_assignment':term_assignment,'S_assignment':S_assignment,'normalization_constraint':'initial_condition','boundary_constraints':boundary_names,'boundary_S':boundary_S,'omitted_constraints':[],'checked':grouping_checked},
'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
(notebook_dir/'state/bppm_b3.json').write_text(json.dumps(state,indent=2))
print('Confirmed rank 4 at N=4 and N=6; saved B3 state.')
