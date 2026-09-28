import importlib.util
import json
from pathlib import Path
spec = importlib.util.spec_from_file_location('runtime',Path(__file__).parent/'helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import b4_math as m

source=(runtime.ROOT/'supplementary/helpers/b4_math.py').read_text(encoding='utf-8-sig')
basis_code=source[source.index('def V_k_basis(k):'):source.index('for k in range(n+1):',source.index('def V_k_basis(k):'))]
structure_code=source[source.index('def V_k_structure(k):'):source.index('for k in range(n+1):',source.index('def V_k_structure(k):'))]
unknowns=[dict(name=name,arguments=['k','N','L'],role=role,index_domain='1 <= k <= N') for name,role in [('c_gg','C[0,0]'),('c_gq','C[0,1]=C[1,0]'),('c_qq','C[1,1]')]]
case=dict(index_domain='1 <= k <= N-1; a=b=1',basis_labels=['A(x_k)','x_k-x_0'],quadratic_coefficients={'00':'c_gg(k,N,L)','01':'c_gq(k,N,L)','11':'c_qq(k,N,L)'})
structure=dict(quadratic_convention='sum_ij C_ij <v_i,v_j>; C symmetric and offdiagonal counted twice',interior=case,initial=dict(index_domain='k=0',basis_labels=[],quadratic_coefficients={}),terminal=dict(case,index_domain='k=N',basis_labels=['A(x_N)','x_N-x_0']),function_terms=[],constant_terms=[])
b4=dict(m.b3,basis_templates={'interior':['A(x_k)','x_k-x_0'],'initial':[],'terminal':['A(x_N)','x_N-x_0']},basis_code=basis_code,structure_code=structure_code,coeff_by_k={str(k):C.tolist() for k,C in m.coeff_by_k.items()},coeff_code=None,coefficient_formula_status='unresolved',expression_structure=structure,unresolved_coefficients=unknowns,numerical_reconstruction=dict(certificate_id=m.b3['certificate_id'],required_indices=list(range(m.n+1)),quadratic_residuals=m.quadratic_residuals,component_residuals=m.component_residuals,tolerances=dict(indep_tol=1e-7,span_tol=1e-5,component_atol=1e-4,component_rtol=1e-5),passed=True))
(runtime.ROOT/'state/feg_b4.json').write_text(json.dumps(b4,indent=2))
(runtime.ROOT/'supplementary/b4_search.json').write_text(json.dumps(m.searched,indent=2))
print('B4 numerical state saved.')
