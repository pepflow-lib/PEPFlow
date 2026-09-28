import runpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ns=runpy.run_path(str(root/'supplementary/b3_trial.py'))
import json
import re
import numpy as np
workflow=(root/'supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text(encoding='utf-8')
assess=next(b for b in re.findall(r'```python\n(.*?)```',workflow,re.S) if 'def assess_rank_pattern' in b)
exec(assess)
samples=[json.loads((root/f'supplementary/b3-observation-N{n}.json').read_text()) for n in (6,8)]
certificate=ns['certificate']
rank_search=assess_rank_pattern(samples,certificate['certificate_id'],left=1,right=1)
assert rank_search['status']=='confirmed'
rank_search['evidence_path']='supplementary/rank_search.json'
(root/'supplementary/rank_search.json').write_text(json.dumps(dict(summary=rank_search,samples=samples),indent=2))
values=[ns['pm'].eval_scalar(v) for v in ns['lyap']]
state={**certificate,'rank_profile':ns['ranks'],'rank_search':rank_search,'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in values],'lyap_func_coords':[np.asarray(v.func_coords,dtype=float).tolist() for v in values],'lyap_offsets':[float(v.offset) for v in values],'certificate_check_code':(root/'supplementary/b3_certificate_check.py').read_text(encoding='utf-8-sig'),'decomposition_code':(root/'supplementary/b3_decomposition.py').read_text(encoding='utf-8-sig'),'grouping_code':(root/'supplementary/b3_grouping.py').read_text(encoding='utf-8-sig'),'extra_duals':ns['extra_duals'],'rank_tolerance':1e-4,'reconstruction_tolerance':1e-4,'reconstruction_rtol':1e-5,'grouping_coverage':dict(constraint_assignment=ns['term_assignment'],S_assignment=ns['S_assignment'],normalization_constraint=ns['tau_name'],boundary_constraints=ns['boundary_names'],boundary_S=ns['boundary_S'],omitted_constraints=[],checked=True),'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
(root/'state/feg_b3.json').write_text(json.dumps(state,indent=2))
(root/'supplementary/b3_assess.py').write_text(assess)
print('Cross-horizon rank confirmed:',rank_search)
