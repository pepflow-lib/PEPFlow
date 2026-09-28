import importlib.util
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',root/'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
import numpy as np
import sympy as sp
import pgm_setup as setup
from partial_sums import construct
from pepflow.lyapunov_utils import vectors_in_column_space, find_symmetric_coefficient_matrix,find_basis_with_sparsest_coefficients
b3=json.loads((root/'state/pgm_b3.json').read_text())
trial=construct(b3, variant="polar-aligned")
ctx,pm,lyap=trial['ctx'],trial['pm'],trial['lyap']
params={'L':sp.S.One,'R':sp.S.One}
for k in range(1,5):
    x=ctx[f'x_{k}'];star=ctx['x_star'];x0=ctx['x_0']
    a=setup.f.grad(x);astar=setup.f.grad(star);s=setup.g.grad(x)
    pairs=[('x0-star',x0-star),('xk-star',x-star),('a_k',a),('a_star',astar),('s_k',s),('a_k-a_star',a-astar),('s_k+a_star',s+astar),('a_k+s_k',a+s)]
    good=vectors_in_column_space(lyap[k],[v for _,v in pairs],pep_context=ctx,resolve_parameters=params,rtol=1e-4,atol=1e-4)
    print('k',k,'incol',[name for name,v in pairs if any(v is w for w in good)],flush=True)
    try:
        basis,C=find_basis_with_sparsest_coefficients(lyap[k],good,pep_context=ctx,resolve_parameters=params,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
        print('basis',[name for v in basis for name,w in pairs if w is v],'C',C,flush=True)
    except ValueError as exc:
        print('failure',exc,flush=True)
    proposed=[x0-star] if k==4 else [x0-star,x-star,a,a-astar]
    try:
        C=find_symmetric_coefficient_matrix(lyap[k],proposed,pep_context=ctx,resolve_parameters=params,indep_tol=1e-7,span_tol=1e-5)
        print('proposed C',C,flush=True)
    except ValueError as exc:
        print('proposed failure',exc,flush=True)

