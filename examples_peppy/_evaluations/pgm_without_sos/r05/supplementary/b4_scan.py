import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from owned_runtime import configure, ROOT
configure()
import json
import numpy as np
import sympy as sp
import pepflow as pf
from pgm_setup import get_pep_setup, f, g
from pepflow.lyapunov_utils import vectors_in_column_space, select_independent_subset

b3=json.loads((ROOT/'state/pgm_b3.json').read_text())
certificate=b3
REPO_ROOT=ROOT
N_int=b3['N_verify']
params_sp={'L':sp.Integer(1),'R':sp.Integer(1)}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
for field in ('certificate_check_code','decomposition_code','grouping_code'):
    exec(compile(b3[field],field,'exec'),globals())
base=[(str(v),v) for v in ctx.basis_vectors()]
for k in range(N_int+1):
    base.append((f'd_{k}',ctx[f'x_{k}']-ctx['x_star']))
    base.append((f'F_{k}',f.grad(ctx[f'x_{k}'])-f.grad(ctx['x_star'])))
    if k:
        base.append((f'G_{k}',g.grad(ctx[f'x_{k}'])+f.grad(ctx['x_star'])))
pairs=base.copy()
for i,(li,vi) in enumerate(base):
    for lj,vj in base[:i]:
        pairs.append((f'{li}-{lj}',vi-vj))
unique=[]
seen=[]
for label,v in pairs:
    coordinates=np.asarray(pm.eval_vector(v).coords,dtype=float)
    if np.linalg.norm(coordinates)<1e-7 or any(np.allclose(coordinates,s,atol=1e-10,rtol=0) or np.allclose(coordinates,-s,atol=1e-10,rtol=0) for s in seen):
        continue
    unique.append((label,v));seen.append(coordinates)
labels_by_id={id(v):label for label,v in unique}
for k in range(1,N_int):
    in_col=vectors_in_column_space(lyap[k],[v for _,v in unique],pep_context=ctx,resolve_parameters=params_sp,rtol=1e-4,atol=1e-4)
    independent,_=select_independent_subset(in_col,pep_context=ctx,resolve_parameters=params_sp,tol=1e-7)
    print('k',k,'span rank',len(independent),'in column',[labels_by_id[id(v)] for v in in_col],flush=True)
from pepflow.lyapunov_utils import find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix
pairs=[]
for k in range(N_int+1):
    pairs.append((f'd_{k}',ctx[f'x_{k}']-ctx['x_star']))
    pairs.append((f'f_{k}',f.grad(ctx[f'x_{k}'])))
    if k:
        pairs.append((f'g_{k}',g.grad(ctx[f'x_{k}'])))
pairs.append(('f_star',f.grad(ctx['x_star'])))
for k in range(1,N_int):
    in_col=vectors_in_column_space(lyap[k],[v for _,v in pairs],pep_context=ctx,resolve_parameters=params_sp,rtol=1e-4,atol=1e-4)
    sparse,C=find_basis_with_sparsest_coefficients(lyap[k],in_col,pep_context=ctx,resolve_parameters=params_sp,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    print('sparse',k,[str(v) for v in sparse],flush=True)
    chosen=[ctx['x_0']-ctx['x_star'],ctx[f'x_{k}']-ctx['x_star'],f.grad(ctx['x_star']),f.grad(ctx[f'x_{k}']),g.grad(ctx[f'x_{k+1}'])]
    C=find_symmetric_coefficient_matrix(lyap[k],chosen,pep_context=ctx,resolve_parameters=params_sp,indep_tol=1e-7,span_tol=1e-5)
    print('adopted C',k,C,flush=True)
    val=pm.eval_scalar(lyap[k])
    print('func',list(zip([str(v) for v in ctx.basis_scalars()],np.asarray(val.func_coords,dtype=float))),flush=True)
