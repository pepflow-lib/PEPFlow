import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import sympy as sp
import numpy as np
import scipy.linalg
import pepflow as pf
from pgm_setup import get_pep_setup
ROOT=Path.cwd()
certificate=json.loads((ROOT/'state/pgm_b2.json').read_text())
N_int=certificate['N_verify']
params_sp={'L':sp.Integer(1),'R':sp.Integer(1)}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
REPO_ROOT=ROOT
exec(compile((ROOT/'supplementary/certificate_check.py').read_text(),'certificate_check','exec'))
# Reuse spectral factors first: all assigned to terminal step.
terms={name:term for name,term in weighted_terms.items() if name!=tau_name}
term_steps={name:int(name.split(',')[1][2:])-1 for name in terms}
G=[np.zeros_like(S_array)]
partial=np.zeros_like(S_array)
for k in range(N_int):
    for name,term in terms.items():
        if term_steps[name]==k or (k==0 and term_steps[name]==-1):
            partial+=np.asarray(pm.eval_scalar(term).inner_prod_coords,float)
    G.append(partial.copy()-(S_array if k==N_int-1 else 0))
print('Spectral terminal allocation ranks',[np.linalg.matrix_rank(m,tol=1e-4) for m in G])
# Reverse LDL eliminates the latest iterate gradients first.
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis
D,ell=ldl_decompose_with_reversed_basis(S_sol,basis,print_output=False)
E=np.asarray([pm.eval_vector(v).coords for v in ell],float)
assert np.allclose(E.T@D@E,S_array,atol=1e-4,rtol=1e-5)
print('D diagonal',np.diag(D))
print('D offdiag',np.max(np.abs(D-np.diag(np.diag(D)))))
for i,row in enumerate(E):
    print(i,[(basis_labels[j],round(v,6)) for j,v in enumerate(row) if abs(v)>1e-5])
pieces={i: D[i,i]*np.outer(E[i],E[i]) for i in range(len(D))}
for shift in (-1,0,1):
    assignment={}
    for i,row in enumerate(E):
        active=[j for j,v in enumerate(row) if abs(v)>1e-5]
        j=max(active)
        tag=basis_labels[j]
        step=int(tag.split('x_')[1].split(')')[0]) if 'x_' in tag and 'star' not in tag else 0
        assignment[i]=min(N_int-1,max(-1,step+shift))
    partial=np.zeros_like(S_array)
    mats=[partial.copy()]
    for k in range(N_int):
        for name,term in terms.items():
            if term_steps[name]==k or (k==0 and term_steps[name]==-1):
                partial+=np.asarray(pm.eval_scalar(term).inner_prod_coords,float)
        for i,piece in pieces.items():
            if assignment[i]==k or (k==0 and assignment[i]==-1):
                partial-=piece
        mats.append(partial.copy())
    print('shift',shift,'assignment',assignment,'ranks',[np.linalg.matrix_rank(m,tol=1e-4) for m in mats])
(ROOT/'supplementary/b3-initial-trials.json').write_text(json.dumps({'certificate_id':certificate['certificate_id'],'D':D.tolist(),'E':E.tolist(),'spectral_terminal_ranks':[int(np.linalg.matrix_rank(m,tol=1e-4)) for m in G]},indent=2))
