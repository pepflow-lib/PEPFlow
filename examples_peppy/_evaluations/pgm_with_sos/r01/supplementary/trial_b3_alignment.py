import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
root=runtime.ATTEMPT
certificate_path=sys.argv[1] if len(sys.argv)>1 else 'state/pgm_b2.json'
certificate=json.loads((root/certificate_path).read_text())
exec(compile((root/'supplementary/b3_certificate_check.py').read_text(),'check','exec'))
exec(compile((root/'supplementary/b3_decomposition_aligned.py').read_text(),'aligned','exec'))
exec(compile((root/'supplementary/b3_grouping.py').read_text(),'grouping','exec'))
projection_errors=[]
for k in range(1,N+1):
    vectors=[ctx_b2['x_0']-ctx_b2['x_star']] if k==N else [f.grad(ctx_b2['x_star']),ctx_b2['x_0']-ctx_b2['x_star'],ctx_b2[f'x_{k}']-ctx_b2['x_star'],f.grad(ctx_b2[f'x_{k}'])-f.grad(ctx_b2['x_star'])]
    B=np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
    M=np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords,dtype=float)
    error=float(np.linalg.norm(M-B@np.linalg.lstsq(B,M,rcond=None)[0]))
    projection_errors.append(error)
print('Known-support diagnostic residuals',projection_errors)
(root/f'supplementary/b3-alignment-trial-N{N}.json').write_text(json.dumps(dict(rank_profile=ranks,projection_errors=projection_errors,coverage_residual=coverage_residual,factor_reconstruction_error=maxabs(F_aligned.T@F_aligned-S_saved)),indent=2))
# Diagnostic only: project interior quadratic matrices onto the observed support.
projected=[]
for k in range(N+1):
    M=np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords,dtype=float)
    if k in (0,N):
        projected.append(M)
    else:
        vecs=[f.grad(ctx_b2['x_star']),ctx_b2['x_0']-ctx_b2['x_star'],ctx_b2[f'x_{k}']-ctx_b2['x_star'],f.grad(ctx_b2[f'x_{k}'])-f.grad(ctx_b2['x_star'])]
        B=np.column_stack([pm.eval_vector(v).coords for v in vecs]).astype(float)
        P=B@np.linalg.pinv(B)
        projected.append(P@M@P.T)
mins=[]
for k in range(N):
    assigned={-1,0} if k==0 else {k}
    G=sum((group_terms[name] for name,target in term_assignment.items() if target in assigned),pf.Scalar.zero())
    Gm=np.asarray(pm.eval_scalar(G).inner_prod_coords,dtype=float)
    Q=Gm-projected[k+1]+projected[k]
    mins.append(float(np.linalg.eigvalsh((Q+Q.T)/2).min()))
print('Projected direct-piece minimum eigenvalues:',mins)

# Alternative allocation: retain original per-step aid blocks and assign the
# small reconstruction correction to the final block, checking its PSD sign.
original_blocks={j:sum((c*u**2 for i,_,c,u in pieces if i==j),pf.Scalar.zero()) for j in range(1,N+1)}
correction=S_scalar-sum(original_blocks.values(),pf.Scalar.zero())
last=pm.eval_scalar(original_blocks[N]+correction)
print('Final-block correction minimum eigenvalue:',np.linalg.eigvalsh(np.asarray(last.inner_prod_coords,dtype=float)).min())
