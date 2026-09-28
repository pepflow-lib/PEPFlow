from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
import sympy as sp
import pepflow as pf
from pgm_setup import get_pep_setup, f, g
from pepflow.lyapunov_utils import vectors_in_column_space,find_basis_with_sparsest_coefficients
notebook_dir=runtime.ATTEMPT
REPO_ROOT=runtime.APPROVED
b3=json.loads((notebook_dir/'state/pgm_b3.json').read_text())
certificate=b3
N_int=b3['N_verify']
params_sp:dict[str,pf.NUMERICAL_TYPE]={'L':sp.S.One,'R':sp.S.One}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
for field in ('certificate_check_code','decomposition_code','grouping_code'):
    exec(compile(b3[field],field,'exec'))
for k in range(1,N_int):
    candidate_pairs=[('e0',ctx['x_0']-ctx['x_star']),('ek',ctx[f'x_{k}']-ctx['x_star']),
                     ('pk',f.grad(ctx[f'x_{k}'])-f.grad(ctx['x_star'])),
                     ('qk',g.grad(ctx[f'x_{k}'])-g.grad(ctx['x_star'])),
                     ('p_prev',f.grad(ctx[f'x_{k-1}'])-f.grad(ctx['x_star']))]
    in_col=vectors_in_column_space(lyap[k],[v for _,v in candidate_pairs],pep_context=ctx,resolve_parameters=params_sp,rtol=1e-4,atol=1e-4)
    print('k',k,'in_col',[label for label,v in candidate_pairs if any(v is w for w in in_col)])
    for label,v in candidate_pairs:
        M=np.asarray(pm.eval_scalar(lyap[k]).inner_prod_coords,float)
        U,s,_=np.linalg.svd(M)
        B=U[:,:4]
        coords=np.asarray(pm.eval_vector(v).coords,float)
        print(label,np.linalg.norm(coords-B@B.T@coords))
    try:
        selected,C=find_basis_with_sparsest_coefficients(lyap[k],in_col,pep_context=ctx,resolve_parameters=params_sp,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
        print('basis',[label for v in selected for label,w in candidate_pairs if v is w])
        print(C)
    except ValueError as exc:
        print('search failed',exc)
