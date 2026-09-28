import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import runpy
root=runtime.ATTEMPT
env=runpy.run_path(str(root/'supplementary/scan_b4.py'))
for filename in ('b4_basis.py','b4_extract.py'):
    exec(compile((root/'supplementary'/filename).read_text(),filename,'exec'),env)
b3=env['b3']
basis_code=(root/'supplementary/b4_basis.py').read_text()
extract=(root/'supplementary/b4_extract.py').read_text()
structure_code='function_coefficients='+repr(env['function_coefficients'])+'\n'+extract[extract.index('def V_k_structure'):extract.index('component_residuals={}')] 
unknowns=[dict(name=f'c_{i}{j}',arguments=['k','N','L'],role=f'interior.C[{i},{j}]=C[{j},{i}]',index_domain='1 <= k <= N-1') for i in range(4) for j in range(i,4)]
unknowns += [dict(name=name,arguments=['k','N','L'],role=role,index_domain='1 <= k <= N-1') for name,role in [('A','coefficient of f(x_k)-f_star'),('B','coefficient of g(x_k)-g_star')]]
unknowns += [dict(name=name,arguments=['N','L'],role=role,index_domain='k=N') for name,role in [('c_terminal','terminal squared initial-distance coefficient'),('A_terminal','terminal f-gap coefficient'),('B_terminal','terminal g-gap coefficient')]]
structure=dict(quadratic_convention='sum_ij C_ij <v_i,v_j>, symmetric C; off-diagonal entries counted twice',interior=dict(index_domain='1 <= k <= N-1; exclusions a=b=1',basis_labels=['a_star','x_0-x_star','x_k-x_star','a_k-a_star'],coefficients={f'{i},{j}':f'c_{i}{j}(k,N,L)' for i in range(4) for j in range(i,4)}),initial=dict(index_domain='k=0',basis_labels=[],coefficients={},value=0),terminal=dict(index_domain='k=N',basis_labels=['x_0-x_star'],coefficients={'0,0':'c_terminal(N,L)'}),function_terms=[dict(expression='f(x_k)-f_star',index_domain='1<=k<N',coefficient='A(k,N,L)'),dict(expression='g(x_k)-g_star',index_domain='1<=k<N',coefficient='B(k,N,L)'),dict(expression='f(x_N)-f_star',index_domain='k=N',coefficient='A_terminal(N,L)'),dict(expression='g(x_N)-g_star',index_domain='k=N',coefficient='B_terminal(N,L)')],constant_terms=[])
state={**b3,'basis_templates':dict(interior=structure['interior']['basis_labels'],initial=[],terminal=['x_0-x_star']),'basis_code':basis_code,'structure_code':structure_code,'coeff_by_k':{str(k):C.tolist() for k,C in env['coeff_by_k'].items()},'function_coefficients':env['function_coefficients'],'coeff_code':None,'coefficient_formula_status':'unresolved','expression_structure':structure,'unresolved_coefficients':unknowns,'numerical_reconstruction':dict(certificate_id=b3['certificate_id'],required_indices=env['required_indices'],quadratic_residuals=env['coefficient_residuals'],component_residuals=env['component_residuals'],tolerances=dict(indep_tol=1e-7,span_tol=1e-5,component_atol=1e-4,component_rtol=1e-5),passed=True)}
(root/'state/pgm_b4.json').write_text(json.dumps(state,indent=2,allow_nan=False))
print('B4 state saved; analytic coefficients deferred to B5.')
