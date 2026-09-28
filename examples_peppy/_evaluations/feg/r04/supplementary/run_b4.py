import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
root=runtime.ATTEMPT
b3=json.loads((root/'state/feg_b3.json').read_text())
scope={'certificate':b3}
for key in ('certificate_check_code','decomposition_code','grouping_code'):
    exec(compile(b3[key],key,'exec'),scope)
for k,v in enumerate(scope['lyap']):
    ev=scope['pm'].eval_scalar(v)
    for actual,saved in [(ev.inner_prod_coords,b3['lyap_inner_prod_coords'][k]),(ev.func_coords,b3['lyap_func_coords'][k]),(ev.offset,b3['lyap_offsets'][k])]:
        assert np.allclose(actual,saved,atol=1e-4,rtol=1e-5)
assert scope['ranks']==b3['rank_profile']
rank_evidence=json.loads((root/b3['rank_search']['evidence_path']).read_text())
assert rank_evidence['summary']==b3['rank_search']
assert b3['rank_search']['status']=='confirmed'
files=['b4_candidates.py','b4_filter.py','b4_search.py','b4_basis.py','b4_coefficients.py','b4_structure.py','b4_reconstruction.py']
for filename in files:
    exec(compile((root/'supplementary'/filename).read_text(encoding='utf-8-sig'),filename,'exec'),scope)
coeffs=scope['coeff_by_k']
unknowns=[dict(name=name,arguments=['k','N','L'],role=role,index_domain='1 <= k <= N') for name,role in [('c_00','C[0,0]'),('c_01','C[0,1]=C[1,0]'),('c_11','C[1,1]')]]
case=dict(basis_labels=['A(x_k)','x_k-x_0'],quadratic_coefficients={'C00':'c_00(k,N,L)','C01=C10':'c_01(k,N,L)','C11':'c_11(k,N,L)'})
structure=dict(quadratic_convention='V_quadratic=sum_ij Cij <vi,vj>, symmetric C; off-diagonal counted twice',interior={**case,'index_domain':'1 <= k <= N-1; a=b=1'},initial={'index_domain':'k=0','basis_labels':[],'quadratic_coefficients':{},'value':0},terminal={**case,'index_domain':'k=N'},function_terms=[],constant_terms=[])
b4={**b3,'basis_templates':{'initial':[],'interior':['A(x_k)','x_k-x_0'],'terminal':['A(x_N)','x_N-x_0']},'basis_code':(root/'supplementary/b4_basis.py').read_text(encoding='utf-8-sig'),'structure_code':(root/'supplementary/b4_structure.py').read_text(encoding='utf-8-sig'),'coeff_by_k':{str(k):C.tolist() for k,C in coeffs.items()},'coeff_code':None,'coefficient_formula_status':'unresolved','expression_structure':structure,'unresolved_coefficients':unknowns,'numerical_reconstruction':{'certificate_id':b3['certificate_id'],'required_indices':list(range(b3['N_verify']+1)),'quadratic_residuals':scope['coefficient_residuals'],'component_residuals':scope['component_residuals'],'tolerances':{'indep_tol':1e-7,'span_tol':1e-5,'component_atol':1e-4,'component_rtol':1e-5},'passed':True}}
(root/'state/feg_b4.json').write_text(json.dumps(b4,indent=2,allow_nan=False))
(root/'supplementary/b4-search-evidence.json').write_text(json.dumps({'candidate_count':len(scope['candidates']),'spanning':{str(k):[scope['labels_by_id'][id(v)] for v in vs] for k,vs in scope['spanning_by_k'].items()},'searched_bases':{str(k):[scope['labels_by_id'][id(v)] for v in vs] for k,vs in scope['searched_bases'].items()},'searched_coefficients':{str(k):C.tolist() for k,C in scope['searched_coeffs'].items()},'adopted_basis_reason':'Use the same interpretable operator/anchor-gap basis at every nonzero index; independently reconstructed after search.','independence':scope['independence']},indent=2))
print('B4 state saved')
