import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import numpy as np
from pgm_setup import get_pep_setup, f, g
NOTEBOOK_DIR=Path.cwd()
REPO_ROOT=NOTEBOOK_DIR/'supplementary/approved'
exec(compile((NOTEBOOK_DIR/'supplementary/b3_visible.py').read_text(),'b3_visible','exec'))
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix
for sample in samples:
    ctx=sample['ctx']; ctx.set_as_current()
    pm=sample['pm']; lyap=sample['lyap']; n=sample['N_int']; params=sample['params_sp']
    for k in range(1,n):
        vectors=[ctx['x_0']-ctx['x_star'],ctx[f'x_{k}']-ctx['x_star'],f.grad(ctx[f'x_{k}'])-f.grad(ctx['x_star']),g.grad(ctx[f'x_{k}'])+f.grad(ctx['x_star'])]
        try:
            C=find_symmetric_coefficient_matrix(lyap[k],vectors,pep_context=ctx,resolve_parameters=params,indep_tol=1e-7,span_tol=1e-5)
            print('N,k',n,k,'C',C)
        except ValueError as e:
            print('failed',n,k,str(e))
        pairs=[]
        for j in range(n+1):
            pairs.extend([(f'd_{j}',ctx[f'x_{j}']-ctx['x_star']),(f'p_{j}',f.grad(ctx[f'x_{j}'])-f.grad(ctx['x_star']))])
            if j>0:
                pairs.extend([(f'q_{j}',g.grad(ctx[f'x_{j}'])+f.grad(ctx['x_star'])),(f'r_{j}',g.grad(ctx[f'x_{j}'])+f.grad(ctx[f'x_{j}']))])
        inside=vectors_in_column_space(lyap[k],[v for _,v in pairs],pep_context=ctx,resolve_parameters=params,rtol=1e-4,atol=1e-4)
        print('incol',[name for name,v in pairs if any(v is w for w in inside)])
