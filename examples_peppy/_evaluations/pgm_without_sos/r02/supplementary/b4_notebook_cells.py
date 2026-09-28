# %% Candidate-vector scan: iterates, gradient gaps, proximal residuals and differences.
from itertools import combinations
from pepflow.lyapunov_utils import vectors_in_column_space,find_basis_with_sparsest_coefficients,find_symmetric_coefficient_matrix

raw_candidates=[]
for i in range(N+1):
    raw_candidates.append((f'x_{i}-x_star',ctx[f'x_{i}']-ctx['x_star']))
    raw_candidates.append((f'grad_f(x_{i})-grad_f(x_star)',f.grad(ctx[f'x_{i}'])-f.grad(ctx['x_star'])))
    if i>0:
        raw_candidates.append((f'grad_g(x_{i})+grad_f(x_star)',g.grad(ctx[f'x_{i}'])+f.grad(ctx['x_star'])))
        raw_candidates.append((f'q_{i}',f.grad(ctx[f'x_{i}'])+g.grad(ctx[f'x_{i}'])))
raw_candidates.extend((str(v),v) for v in ctx.basis_vectors())
raw_candidates.extend((f'x_{i}',ctx[f'x_{i}']) for i in range(N+1))
base_candidates=list(raw_candidates)
for (a,u),(b,v) in combinations(base_candidates,2):
    raw_candidates.append((f'({a})-({b})',u-v))
candidates=[]
seen=set()
for label,vector in raw_candidates:
    coordinates=np.asarray(pm.eval_vector(vector).coords,dtype=float)
    if np.linalg.norm(coordinates)<1e-10:
        continue
    key=tuple(np.round(coordinates,10))
    neg=tuple(np.round(-coordinates,10))
    if key in seen or neg in seen:
        continue
    seen.add(key)
    candidates.append((label,vector))
labels_by_id={id(v):label for label,v in candidates}
print('Deduplicated nonzero candidates:',len(candidates))

# %% Filter candidates to each required nonzero column space.
in_column={}
for k in range(1,N+1):
    in_column[k]=vectors_in_column_space(lyap[k],[v for _,v in candidates],pep_context=ctx,
        resolve_parameters=params,atol=1e-4,rtol=1e-4)
    print(f'V_{k} column-space candidates:')
    for vector in in_column[k]:
        print('  ',labels_by_id[id(vector)])

# %% Selected basis pattern: perform the actual sparse-basis search.
search_basis={}
search_coefficients={}
for k in range(1,N+1):
    chosen,C=find_basis_with_sparsest_coefficients(lyap[k],in_column[k],pep_context=ctx,
        resolve_parameters=params,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    assert len(chosen)==ranks[k]
    search_basis[k]=chosen
    search_coefficients[k]=C
    print(f'k={k}, rank={ranks[k]}')
    print('sparse basis:',[labels_by_id[id(v)] for v in chosen])
    print('zero coefficients:',int(np.sum(np.abs(C)<1e-6)),'/',C.size)

# %% Adopt a uniform interior basis; every endpoint has its own definition.
def V_k_basis(k):
    if k==0:
        return []
    u0=ctx['x_0']-ctx['x_star']
    if k==N_int:
        return [u0]
    return [u0,ctx[f'x_{k}']-ctx['x_star'],f.grad(ctx[f'x_{k}'])-f.grad(ctx['x_star']),f.grad(ctx[f'x_{k}'])]

def V_k_basis_labels(k):
    if k==0:
        return []
    if k==N_int:
        return ['x_0-x_star']
    return ['x_0-x_star',f'x_{k}-x_star',f'grad_f(x_{k})-grad_f(x_star)',f'grad_f(x_{k})']

for k in range(N+1):
    selected_basis=V_k_basis(k)
    matrix=np.column_stack([pm.eval_vector(v).coords for v in selected_basis]).astype(float) if selected_basis else np.zeros((len(ctx.basis_vectors()),0))
    assert np.linalg.matrix_rank(matrix,tol=1e-7)==len(selected_basis)==ranks[k]
    print(f'k={k}: rank {ranks[k]} basis {V_k_basis_labels(k)}')

# %% Coefficient matrices and meaningful function-value terms at every index.
coeff_by_k={}
coefficient_residuals={}
function_coefficients={}
function_residuals={}
for k in range(N+1):
    chosen=V_k_basis(k)
    target=pm.eval_scalar(lyap[k])
    if chosen:
        C=find_symmetric_coefficient_matrix(lyap[k],chosen,pep_context=ctx,resolve_parameters=params,indep_tol=1e-7,span_tol=1e-5)
        matrix=np.column_stack([pm.eval_vector(v).coords for v in chosen]).astype(float)
        residual=np.linalg.norm(matrix@C@matrix.T-np.asarray(target.inner_prod_coords,dtype=float),ord='fro')
    else:
        C=np.zeros((0,0))
        residual=np.linalg.norm(np.asarray(target.inner_prod_coords,dtype=float),ord='fro')
    assert residual<=1e-5*max(1,np.linalg.norm(np.asarray(target.inner_prod_coords,dtype=float),ord='fro'))
    coeff_by_k[k]=C
    coefficient_residuals[k]=float(residual)
    if k==0:
        alpha,beta=0.0,0.0
        func_error=max_abs(target.func_coords)
    else:
        fgap=f(ctx[f'x_{k}'])-f(ctx['x_star'])
        ggap=g(ctx[f'x_{k}'])-g(ctx['x_star'])
        F=np.column_stack([pm.eval_scalar(fgap).func_coords,pm.eval_scalar(ggap).func_coords]).astype(float)
        alpha,beta=np.linalg.lstsq(F,np.asarray(target.func_coords,dtype=float),rcond=None)[0]
        func_error=max_abs(F@np.array([alpha,beta])-target.func_coords)
    assert func_error<1e-5 and max_abs(target.offset)==0
    function_coefficients[k]=[float(alpha),float(beta)]
    function_residuals[k]=float(func_error)
    print(f'k={k}: quadratic reconstruction residual {residual:.3e}; function residual {func_error:.3e}; offset {target.offset}')
    pf.pprint_labeled_matrix(C,V_k_basis_labels(k),precision=6)
    print('Function coefficients for f(x_k)-f_star, g(x_k)-g_star:',function_coefficients[k])

# %% Reconstruct the complete potential from basis, C, and the identified gaps.
def V_k_structure(k):
    chosen=V_k_basis(k)
    C=coeff_by_k[k]
    quadratic=sum((float(C[i,j])*chosen[i]*chosen[j] for i,j in np.ndindex(C.shape)),pf.Scalar.zero())
    if k==0:
        return quadratic
    alpha,beta=function_coefficients[k]
    return quadratic+alpha*(f(ctx[f'x_{k}'])-f(ctx['x_star']))+beta*(g(ctx[f'x_{k}'])-g(ctx['x_star']))

component_residuals={}
for k in range(N+1):
    value=pm.eval_scalar(V_k_structure(k)-lyap[k])
    target=pm.eval_scalar(lyap[k])
    component_residuals[str(k)]={}
    for name,actual,reference in [('gram',value.inner_prod_coords,target.inner_prod_coords),('function',value.func_coords,target.func_coords),('offset',value.offset,target.offset)]:
        error=max_abs(actual)
        assert error<=1e-4+1e-5*max_abs(reference)
        component_residuals[str(k)][name]=error
print('Full-component reconstruction passed for all indices 0 through',N)
