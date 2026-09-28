import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import runpy
import json
import numpy as np
root=runtime.ATTEMPT
env=runpy.run_path(str(root/'supplementary/run_b3.py'))
certificate=env['certificate']
samples=[json.loads((root/f'supplementary/rank_N{n}.json').read_text()) for n in (4,6)]
for s in samples:
    assert s['certificate_checked'] and s['grouping_checked'] and s['rank_credible']
    assert s['recipe_id']==samples[0]['recipe_id'] and s['rank_convention']==samples[0]['rank_convention']
    retained=s['rank_profile'][1:s['N']]
    assert len(retained)>=3 and set(retained)=={4}
summary=dict(status='confirmed',boundary_exclusions=dict(left=1,right=1),rank=4,confirmed_horizons=[4,6],selected_certificate_id=certificate['certificate_id'],recipe_id=samples[0]['recipe_id'],rank_convention=samples[0]['rank_convention'],unresolved_samples=[],evidence_path='supplementary/rank_search.json')
(root/'supplementary/rank_search.json').write_text(json.dumps(dict(summary=summary,samples=samples),indent=2))
evaluated=[env['pm'].eval_scalar(v) for v in env['lyap']]
state={**certificate,'rank_profile':env['ranks'],'rank_search':summary,'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in evaluated],'lyap_func_coords':[np.asarray(v.func_coords,dtype=float).tolist() for v in evaluated],'lyap_offsets':[float(v.offset) for v in evaluated],'certificate_check_code':(root/'supplementary/b3_certificate_check.py').read_text(),'decomposition_code':(root/'supplementary/b3_decomposition.py').read_text(),'grouping_code':(root/'supplementary/b3_grouping.py').read_text(),'extra_duals':{},'rank_tolerance':1e-4,'reconstruction_tolerance':1e-4,'reconstruction_rtol':1e-5,'grouping_coverage':dict(constraint_assignment=env['term_assignment'],S_assignment=env['S_assignment'],normalization_constraint='initial_condition',boundary_constraints=[],boundary_S=[],omitted_constraints=[],checked=True,coverage_residual=env['coverage_residual']),'lyapunov_proof_verified':False}
(root/'state/pgm_b3.json').write_text(json.dumps(state,indent=2,allow_nan=False))
print('B3 saved with confirmed rank 4 at N=4 and N=6.')
