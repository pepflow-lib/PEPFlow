import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
import pepflow as pf
from itertools import combinations
from pepflow.lyapunov_utils import vectors_in_column_space,find_basis_with_sparsest_coefficients
from pgm_setup import get_pep_setup,f,g
notebook_dir=runtime.ROOT
b3=json.loads((notebook_dir/'state/pgm_b3.json').read_text())
certificate=b3
for field in ['certificate_check_code','decomposition_code','grouping_code']:
    exec(compile(b3[field],field,'exec'))
raw=[]
for i in range(N+1):
    raw.append((f'x_{i}-x_star',ctx[f'x_{i}']-ctx['x_star']))
    raw.append((f'grad_f(x_{i})-grad_f(x_star)',f.grad(ctx[f'x_{i}'])-f.grad(ctx['x_star'])))
    if i>0:
        raw.append((f'grad_g(x_{i})+grad_f(x_star)',g.grad(ctx[f'x_{i}'])+f.grad(ctx['x_star'])))
        raw.append((f'q_{i}',f.grad(ctx[f'x_{i}'])+g.grad(ctx[f'x_{i}'])))
raw.extend((str(v),v) for v in ctx.basis_vectors())
raw.extend((f'x_{i}',ctx[f'x_{i}']) for i in range(N+1))
base=list(raw)
for (a,u),(b,v) in combinations(base,2):
    raw.append((f'({a})-({b})',u-v))
unique=[];seen=set()
for label,vector in raw:
    coords=np.asarray(pm.eval_vector(vector).coords,dtype=float)
    if np.linalg.norm(coords)<1e-10:
        continue
    key=tuple(np.round(coords,10))
    neg=tuple(np.round(-coords,10))
    if key in seen or neg in seen:
        continue
    seen.add(key);unique.append((label,vector))
labels_by_id={id(v):s for s,v in unique}
print('Candidates:',len(unique))
for k in range(1,N+1):
    incol=vectors_in_column_space(lyap[k],[v for _,v in unique],pep_context=ctx,resolve_parameters=params,atol=1e-4,rtol=1e-4)
    print('k',k,'incol',[(labels_by_id[id(v)]) for v in incol])
    bs,C=find_basis_with_sparsest_coefficients(lyap[k],incol,pep_context=ctx,resolve_parameters=params,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    print('Selected', [labels_by_id[id(v)] for v in bs]);print(C)
