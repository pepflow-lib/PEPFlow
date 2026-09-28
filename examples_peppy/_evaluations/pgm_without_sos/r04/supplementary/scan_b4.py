from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
source=(runtime.ATTEMPT/'supplementary/explore_b4.py').read_text(encoding='utf-8-sig')
exec(compile(source[:source.index('for k in range(1,N_int):')],'b4_rebuild','exec'))
from itertools import combinations
pairs=[]
for i in range(N_int+1):
    pairs.extend([(f'e{i}',ctx[f'x_{i}']-ctx['x_star']),(f'p{i}',f.grad(ctx[f'x_{i}'])-f.grad(ctx['x_star']))])
    if i>0:
        pairs.append((f'q{i}',g.grad(ctx[f'x_{i}'])-g.grad(ctx['x_star'])))
pairs += [(str(v),v) for v in ctx.basis_vectors()]
for k in range(1,N_int):
    M=np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords,float)
    print('singular',k,np.linalg.svd(M,compute_uv=False))
    in_col=vectors_in_column_space(lyap[k],[v for _,v in pairs],pep_context=ctx,resolve_parameters=params_sp,rtol=1e-4,atol=1e-4)
    print('in_col',[(lab,str(v)) for lab,v in pairs if any(v is w for w in in_col)])
    U,s,_=np.linalg.svd(M)
    Q=np.column_stack([np.asarray(pm.eval_vector(v).coords,float) for lab,v in pairs if lab in ('e0',f'e{k}',f'p{k}')])
    u=U[:,:4]
    rem=u-Q@np.linalg.pinv(Q)@u
    r,s,_=np.linalg.svd(rem)
    print('missing direction',[(lab,round(val,5)) for lab,val in zip(basis_labels,r[:,0]) if abs(val)>1e-5])
