from itertools import combinations
import sympy as sp
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix
from ogm_setup import theta_sequence

params_sp={'L':sp.Integer(1),'R':sp.Integer(1)}
assert ranks == certificate['rank_profile']
assert certificate['rank_search']['status']=='confirmed'
for k,Vk in enumerate(lyap):
    evaluated=pm.eval_scalar(Vk)
    for actual,saved in ((evaluated.inner_prod_coords,certificate['lyap_inner_prod_coords'][k]),(evaluated.func_coords,certificate['lyap_func_coords'][k]),(evaluated.offset,certificate['lyap_offsets'][k])):
        assert np.allclose(np.asarray(actual,dtype=float),np.asarray(saved,dtype=float),atol=1e-4,rtol=1e-5)
theta=theta_sequence(N_int)
candidate_pairs=[('anchor',ctx['x_0']-ctx['x_star']),('terminal_q',ctx[f'z_{N_int}']-ctx['x_star']-theta[-1]*ctx[f'g_{N_int}'])]
for k in range(N_int+1):
    for family in ('x','z','g','y'):
        if family=='y' and k==0:
            continue
        v=ctx[f'{family}_{k}']
        candidate_pairs.append((f'{family}_{k}',v))
        if family!='g':
            candidate_pairs.append((f'{family}_{k}-x_star',v-ctx['x_star']))
base_pairs=list(candidate_pairs)
for (label_a,v_a),(label_b,v_b) in combinations(base_pairs,2):
    candidate_pairs.append((f'({label_a})-({label_b})',v_a-v_b))
unique_pairs=[]
unique_coords=[]
for label,v in candidate_pairs:
    coords=np.asarray(pm.eval_vector(v).coords,dtype=float)
    if np.linalg.norm(coords)<1e-6:
        continue
    if any(np.allclose(coords,old,atol=1e-6,rtol=0) or np.allclose(coords,-old,atol=1e-6,rtol=0) for old in unique_coords):
        continue
    unique_pairs.append((label,v))
    unique_coords.append(coords)
candidates=[v for _,v in unique_pairs]
label_by_id={id(v):label for label,v in unique_pairs}
filtered={}
for k in range(1,N_int+1):
    filtered[k]=vectors_in_column_space(lyap[k],candidates,pep_context=ctx,resolve_parameters={'L':sp.Integer(1),'R':sp.Integer(1)},rtol=1e-4,atol=1e-4)
    print(f'V_{k} column-space candidates:')
    for v in filtered[k]:
        print('   ',label_by_id[id(v)])
sparse_basis_by_k={}
sparse_coeff_by_k={}
for k in range(1,N_int+1):
    found,C=find_basis_with_sparsest_coefficients(lyap[k],filtered[k],pep_context=ctx,resolve_parameters={'L':sp.Integer(1),'R':sp.Integer(1)},zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    sparse_basis_by_k[k]=found
    sparse_coeff_by_k[k]=C
    assert len(found)==ranks[k]
    print(f'k={k}, rank={ranks[k]} sparse basis:',[label_by_id[id(v)] for v in found])
    print('zero coefficients:',int(np.sum(np.abs(C)<1e-6)),'/',C.size)
    print('C',C)
    print('function',np.asarray(pm.eval_scalar(lyap[k]).func_coords,dtype=float))

