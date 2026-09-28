import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
import cvxpy as cp
root=runtime.ATTEMPT
certificate_path=sys.argv[1] if len(sys.argv)>1 else 'state/pgm_b2.json'
certificate=json.loads((root/certificate_path).read_text())
exec(compile((root/'supplementary/b3_certificate_check.py').read_text(),'check','exec'))
exec(compile((root/'supplementary/b3_decomposition_original.py').read_text(),'decomp','exec'))
exec(compile((root/'supplementary/b3_grouping.py').read_text(),'group','exec'))
dim=len(basis)
V_mats=[np.zeros((dim,dim))]
Cvars=[]
Crefs=[]
for k in range(1,N):
    vectors=[f.grad(ctx_b2['x_star']),ctx_b2['x_0']-ctx_b2['x_star'],ctx_b2[f'x_{k}']-ctx_b2['x_star'],f.grad(ctx_b2[f'x_{k}'])-f.grad(ctx_b2['x_star'])]
    B=np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
    M=np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords,dtype=float)
    Cref=np.linalg.pinv(B)@M@np.linalg.pinv(B).T
    C=cp.Variable((4,4),symmetric=True)
    Cvars.append(C);Crefs.append(Cref)
    V_mats.append(B@C@B.T)
G_mats=[]
for k in range(N):
    assigned={-1,0} if k==0 else {k}
    G=sum((group_terms[name] for name,target in term_assignment.items() if target in assigned),pf.Scalar.zero())
    G_mats.append(np.asarray(pm.eval_scalar(G).inner_prod_coords,dtype=float))
V_mats.append(sum(G_mats)-S_saved)
Q=[G_mats[k]-V_mats[k+1]+V_mats[k] for k in range(N)]
t=cp.Variable(nonneg=True)
constraints=[q+t*np.eye(dim)>>0 for q in Q]+[t<=1e-8]
problem=cp.Problem(cp.Minimize(1e8*sum(cp.sum_squares(C-Cref) for C,Cref in zip(Cvars,Crefs))),constraints)
problem.solve(solver='CLARABEL')
arrays=[np.asarray(q.value,dtype=float) for q in Q]
minimum=min(float(np.linalg.eigvalsh((a+a.T)/2).min()) for a in arrays)
print('PSD allocation optimization',problem.status,'t',t.value,'minimum eigenvalue',minimum)
data=dict(N=N,certificate_id=certificate['certificate_id'],status=problem.status,t=float(t.value),minimum_eigenvalue=minimum,Q=[a.tolist() for a in arrays],solver='CLARABEL',options={},reconstruction=maxabs(sum(arrays)-S_saved))
(root/f'supplementary/b3-psd-allocation-N{N}.json').write_text(json.dumps(data,indent=2))

