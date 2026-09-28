from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix
b3=json.loads((notebook_dir/'state/dual_feg_b3.json').read_text())
assert b3['certificate_id']==certificate['certificate_id']
assert b3['rank_profile']==ranks
assert b3['rank_search']['boundary_exclusions']=={'left':1,'right':1}
for k,Vk in enumerate(lyap):
    ev=pm.eval_scalar(Vk)
    for actual,saved in [(ev.inner_prod_coords,b3['lyap_inner_prod_coords'][k]),(ev.func_coords,b3['lyap_func_coords'][k]),(ev.offset,b3['lyap_offsets'][k])]:
        assert np.allclose(np.asarray(actual,dtype=float),np.asarray(saved,dtype=float),atol=1e-4,rtol=1e-5)
candidate_pairs=[(f'g_{N_int}',ctx[f'g_{N_int}']),('x_N-x_0',ctx[f'x_{N_int}']-ctx['x_0'])]
for k in range(N_int+1):
    candidate_pairs += [(f'z_{k}',ctx[f'z_{k}']),(f'x_{k}-x_0',ctx[f'x_{k}']-ctx['x_0']),
        (f'x_{k}-x_N',ctx[f'x_{k}']-ctx[f'x_{N_int}']), (f'g_{k}',ctx[f'g_{k}'])]
for k in range(N_int):
    candidate_pairs += [(f'h_{k}',ctx[f'h_{k}']), (f'y_{k}-x_N',ctx[f'y_{k}']-ctx[f'x_{N_int}'])]
candidate_pairs += [(str(v),v) for v in ctx.basis_vectors()]
candidate_pairs += [('x_0-x_star',ctx['x_0']-ctx['x_star']),('x_N-x_star',ctx[f'x_{N_int}']-ctx['x_star'])]
unique_pairs=[]
unique_coords=[]
for label,vector in candidate_pairs:
    coords=np.asarray(pm.eval_vector(vector).coords,dtype=float)
    if np.linalg.norm(coords)<1e-12 or any(np.allclose(coords,old,atol=1e-12,rtol=0) for old in unique_coords):
        continue
    unique_pairs.append((label,vector))
    unique_coords.append(coords)
candidate_pairs=unique_pairs
candidates=[v for _,v in candidate_pairs]
labels_by_id={id(v):label for label,v in candidate_pairs}
spanning_by_k={}
for k in range(1,N_int+1):
    in_col=vectors_in_column_space(lyap[k],candidates,pep_context=ctx,resolve_parameters=params_sp,rtol=1e-4,atol=1e-4)
    spanning_by_k[k]=in_col
    print(f'V_{k} column-space candidates:')
    for v in in_col:
        print('   '+labels_by_id[id(v)])

