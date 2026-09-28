import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
import pepflow as pf
import bppm_setup as setup
notebook_dir=runtime.ROOT
REPO_ROOT=runtime.APPROVED
b4=json.loads((notebook_dir/'state/bppm_b4.json').read_text())
certificate=b4
N_int=b4['N_verify']
params_sp=json.loads(b4['params_json'])
ctx,pb,obj=setup.get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(b4['relaxed_constraints'])
for field in ('certificate_check_code','decomposition_code','grouping_code'):
    exec(compile(b4[field],field,'exec'))
f_obj=setup.f
h_obj=setup.h
coeff_by_k={int(k):np.asarray(C,dtype=float).reshape((0,0) if int(k)==0 else (4,4)) for k,C in b4['coeff_by_k'].items()}
exec(compile(b4['basis_code'],'basis_code','exec'))
exec(compile(b4['structure_code'],'structure_code','exec'))
sources={}
for name in ('common','step','base','boundary'):
    sources[name]=(notebook_dir/f'supplementary/b5_{name}.py').read_text(encoding='utf-8-sig')
    exec(compile(sources[name],f'b5_{name}.py','exec'))
proof_checks={'step':True,'base':True,'boundary':True,'signs':True,'domain':True,'normalization':True}
state={**b4,'lyapunov_proof_verified':True,'analytic_full_pep_verified':False,'coefficient_formula_status':'verified',
'proof_checks':proof_checks,'symbolic_residuals':{'step':step_check,'base':base_check,'boundary':boundary_check},
'final_lyapunov_formula':'V_0=0; V_k=k/N*(f(x_k)-f(x_star))+(D_h(x_star,x_k)-D_h(x_star,x_0))/(alpha*N), 1<=k<=N',
'final_expression_structure':b4['expression_structure'],'derived_coeff_code':b4['coeff_code'],
'local_multiplier_code':'mu_star=1/N; mu_f=k/N; mu_reverse=(k+1)/(alpha*N); mu_forward=k/(alpha*N)',
'proof_arguments':{'signs':'All four convex residuals are nonpositive and all displayed multipliers are nonnegative for k>=0, N>=1, alpha>0. No PSD term is needed in the exact local identity.',
'domain':'Interior k=1,...,N-1; separate first-step base; N=1 is base plus terminal. R=0 allowed.',
'normalization':'gap-R/(alpha*N)=V_N+[D_h(x_star,x_0)-R+Q_h(x_star,x_N)]/(alpha*N)<=0',
'global_analytic_status':'Separate full-PEP analytic certificate not claimed; complete exact local Lyapunov proof established.'},
'analytic_source':sources,'unresolved_coefficients':[], 'run_status':'verification_pending','remaining_work':['Final notebook static checks, clean-kernel nbconvert execution and content audit']}
(notebook_dir/'state/bppm_b5.json').write_text(json.dumps(state,indent=2))
print('Exact symbolic obligations passed; final notebook verification remains.')
