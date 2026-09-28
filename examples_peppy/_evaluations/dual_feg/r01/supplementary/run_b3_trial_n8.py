import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import sympy as sp
import pepflow as pf
from dual_feg_setup import get_pep_setup
notebook_dir=runtime.ATTEMPT
REPO_ROOT=runtime.APPROVED
certificate=json.loads((notebook_dir/'supplementary/n8-dual_feg_b2.json').read_text())
N_int=certificate['N_verify']
params_sp={k:sp.S(v) for k,v in json.loads(certificate['params_json']).items()}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
for file in ['b3_certificate_check.py','b3_decomposition.py','b3_grouping.py']:
    p=notebook_dir/'supplementary'/file
    exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'))
observation={'N':N_int,'certificate_id':certificate['certificate_id'],'recipe_id':'forward_lip_mon_terminal_gram','rank_profile':ranks,'rank_convention':{'tolerance':rank_tolerance,'scaling':'absolute singular values in original earlier-iterates-first coordinates'},'rank_credible':all(not any(rank_tolerance/2<=s<=2*rank_tolerance for s in row) for row in singular_values),'certificate_checked':certificate_checked,'grouping_checked':grouping_checked,'singular_values':singular_values,'coverage_residuals':coverage_residuals,'boundary_exclusions':{'left':rank_left,'right':rank_right},'source_files':['supplementary/b3_certificate_check.py','supplementary/b3_decomposition.py','supplementary/b3_grouping.py']}
(notebook_dir/'supplementary/b3-trial-n8.json').write_text(json.dumps(observation,indent=2))

