import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from owned_runtime import configure, ROOT, APPROVED
configure()
import json
import numpy as np
import sympy as sp
import pepflow as pf
from pgm_setup import get_pep_setup,f,g

notebook_dir=ROOT
repo_root=APPROVED
REPO_ROOT=ROOT
b3=json.loads((ROOT/'state/pgm_b3.json').read_text())
certificate=b3
N_int=b3['N_verify']
params_sp={'L':sp.Integer(1),'R':sp.Integer(1)}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(b3['relaxed_constraints'])
for field in ('certificate_check_code','decomposition_code','grouping_code'):
    exec(compile(b3[field],field,'exec'),globals())
source=(ROOT/'supplementary/b4_cells.py').read_text(encoding='utf-8-sig')
exec(compile(source,'b4_cells.py','exec'),globals())
sections=source.split('# CELL\n')[1:]
basis_code=sections[4].split('for k in range(N_int+1):')[0]
structure_code='function_weights = '+repr(function_weights)+'\n'+sections[6].split('component_residuals={}')[0]
unknowns=[{'name':f'c_{i}{j}','arguments':['k','N','L'],'role':f'interior.C[{i},{j}] = interior.C[{j},{i}]','index_domain':'1 <= k <= N-1'} for i in range(5) for j in range(i,5)]
expression_structure={
    'quadratic_convention':'V_quadratic = sum_{i,j} C_ij * <v_i,v_j>, symmetric C; off-diagonal entries count twice',
    'interior':{'index_domain':'1 <= k <= N-1','basis_labels':['d_0','grad_f(x_k)','x_{k+1}-x_star','s_g(x_{k+1})','grad_f(x_star)'],
        'quadratic_coefficients':{f'{i},{j}':f'c_{i}{j}(k,N,L)' for i in range(5) for j in range(i,5)}},
    'initial':{'index_domain':'k=0','basis_labels':[],'quadratic_coefficients':{},'expression':'0'},
    'terminal':{'index_domain':'k=N','basis_labels':['d_0'],'quadratic_coefficients':{'0,0':'-L/(4*N), candidate'}},
    'function_terms':[
        {'index_domain':'1 <= k <= N-1','expression':'f(x_k)-f(x_star)','coefficient':'(k+1)/(2*N-k), candidate'},
        {'index_domain':'1 <= k <= N-1','expression':'g(x_k)-g(x_star)','coefficient':'k/(2*N-k), candidate'},
        {'index_domain':'k=N','expression':'h(x_N)-h(x_star)','coefficient':'1'}],
    'constant_terms':[]}
state={**b3,'basis_templates':expression_structure,'basis_code':basis_code,'structure_code':structure_code,
    'coeff_by_k':{str(k):C.tolist() for k,C in coeff_by_k.items()},'coeff_code':None,
    'coefficient_formula_status':'unresolved','expression_structure':expression_structure,
    'unresolved_coefficients':unknowns,'numerical_reconstruction':{
        'certificate_id':b3['certificate_id'],'required_indices':required_indices,
        'quadratic_residuals':{str(k):v for k,v in coefficient_residuals.items()},
        'component_residuals':component_residuals,'tolerances':{'indep_tol':1e-7,'span_tol':1e-5,'component_atol':1e-4,'component_rtol':1e-5},'passed':True},
    'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
(ROOT/'state/pgm_b4.json').write_text(json.dumps(state,indent=2,allow_nan=False))
print('B4 state saved; all indices reconstructed.')
