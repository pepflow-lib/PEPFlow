import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import re
notebook_dir=runtime.ATTEMPT
workflow=(runtime.APPROVED/'plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text(encoding='utf-8')
blocks=re.findall(r'```python\n(.*?)\n```',workflow,re.S)
assess=next(code for code in blocks if code.startswith('def assess_rank_pattern'))
(notebook_dir/'supplementary/b3_assess.py').write_text(assess,encoding='utf-8')
# Recompute the selected horizon in this process; this executes all saved-number checks.
p=notebook_dir/'supplementary/run_b3_trial.py'
exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'))
exec(compile(assess,str(notebook_dir/'supplementary/b3_assess.py'),'exec'))
samples=[json.loads((notebook_dir/f'supplementary/b3-trial-n{n}.json').read_text()) for n in [6,8]]
rank_search=assess_rank_pattern(samples,certificate['certificate_id'],left=1,right=1)
assert rank_search['status']=='confirmed'
rank_search['evidence_path']='supplementary/rank_search.json'
(notebook_dir/'supplementary/rank_search.json').write_text(json.dumps({'summary':rank_search,'samples':samples},indent=2))
evaluated=[pm.eval_scalar(v) for v in lyap]
state={**certificate,'rank_profile':ranks,'rank_search':rank_search,'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in evaluated],'lyap_func_coords':[np.asarray(v.func_coords,dtype=float).tolist() for v in evaluated],'lyap_offsets':[float(v.offset) for v in evaluated],'certificate_check_code':(notebook_dir/'supplementary/b3_certificate_check.py').read_text(encoding='utf-8-sig'),'decomposition_code':(notebook_dir/'supplementary/b3_decomposition.py').read_text(encoding='utf-8-sig'),'grouping_code':(notebook_dir/'supplementary/b3_grouping.py').read_text(encoding='utf-8-sig'),'extra_duals':extra_duals,'rank_tolerance':rank_tolerance,'reconstruction_tolerance':tol['reconstruction_atol'],'reconstruction_rtol':tol['reconstruction_rtol'],'grouping_coverage':{'constraint_assignment':term_assignment,'S_assignment':S_assignment,'normalization_constraint':tau_name,'boundary_constraints':boundary_names,'boundary_S':boundary_S,'omitted_constraints':[],'checked':grouping_checked},'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
(notebook_dir/'state/dual_feg_b3.json').write_text(json.dumps(state,indent=2))
print('Cross-horizon confirmation:',rank_search)
