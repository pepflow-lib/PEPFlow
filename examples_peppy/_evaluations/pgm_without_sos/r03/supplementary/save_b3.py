import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import numpy as np
from pgm_setup import get_pep_setup
NOTEBOOK_DIR=Path.cwd()
REPO_ROOT=NOTEBOOK_DIR/'supplementary/approved'
exec(compile((NOTEBOOK_DIR/'supplementary/b3_visible.py').read_text(),'b3_visible','exec'))
selected=selected_sample
certificate=selected['certificate']
rank_samples=[]
for sample in samples:
    rank_samples.append({'N':sample['N_int'],'certificate_id':sample['certificate']['certificate_id'],'recipe_id':'reverse_ldl_latest_gradient_step','rank_profile':sample['ranks'],'rank_convention':{'tolerance':1e-4,'scaling':'none; original Gram coordinates','coordinate_order':'setup earlier iterates first'},'rank_credible':True,'certificate_checked':sample['certificate_checked'],'grouping_checked':sample['grouping_checked'],'singular_values':sample['singular_values'],'coverage_residuals':sample['coverage_residuals']})
rank_search={'status':'confirmed','boundary_exclusions':{'left':1,'right':1},'rank':4,'confirmed_horizons':[4,6],'selected_certificate_id':certificate['certificate_id'],'recipe_id':'reverse_ldl_latest_gradient_step','rank_convention':rank_samples[0]['rank_convention'],'unresolved_samples':[],'evidence_path':'supplementary/rank_search.json'}
(NOTEBOOK_DIR/'supplementary/rank_search.json').write_text(json.dumps({'summary':rank_search,'samples':rank_samples},indent=2))
values=[selected['pm'].eval_scalar(v) for v in selected['lyap']]
state={**certificate,'rank_profile':selected['ranks'],'rank_search':rank_search,'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,float).tolist() for v in values],'lyap_func_coords':[np.asarray(v.func_coords,float).tolist() for v in values],'lyap_offsets':[float(v.offset) for v in values],'certificate_check_code':(NOTEBOOK_DIR/'supplementary/certificate_check.py').read_text(encoding='utf-8-sig'),'decomposition_code':(NOTEBOOK_DIR/'supplementary/decomposition_b3.py').read_text(encoding='utf-8-sig'),'grouping_code':(NOTEBOOK_DIR/'supplementary/grouping_b3.py').read_text(encoding='utf-8-sig'),'extra_duals':selected['extra_duals'],'rank_tolerance':1e-4,'reconstruction_tolerance':1e-4,'reconstruction_rtol':1e-5,'grouping_coverage':{'constraint_assignment':selected['term_assignment'],'S_assignment':selected['S_assignment'],'normalization_constraint':selected['tau_name'],'boundary_constraints':[],'boundary_S':[],'omitted_constraints':[],'checked':True},'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
(NOTEBOOK_DIR/'state/pgm_b3.json').write_text(json.dumps(state,indent=2))
print('B3 selected state saved.')
