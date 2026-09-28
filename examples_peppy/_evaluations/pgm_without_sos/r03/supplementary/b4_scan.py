from itertools import combinations
candidate_pairs=[('grad_f_star',f.grad(ctx['x_star']))]
for j in range(N_int+1):
    candidate_pairs += [(f'd_{j}',ctx[f'x_{j}']-ctx['x_star']),(f'p_{j}',f.grad(ctx[f'x_{j}'])-f.grad(ctx['x_star'])),(f'grad_f_{j}',f.grad(ctx[f'x_{j}']))]
    if j>0:
        candidate_pairs.append((f'q_{j}',g.grad(ctx[f'x_{j}'])+f.grad(ctx['x_star'])))
candidate_pairs += [(str(v),v) for v in ctx.basis_vectors()]
anchors=[ctx[f'x_{j}'] for j in range(N_int+1)]+[ctx['x_star']]
for i,j in combinations(range(len(anchors)),2):
    candidate_pairs.append((f'anchor_{i}-anchor_{j}',anchors[i]-anchors[j]))
unique=[]
coords=[]
for label,v in candidate_pairs:
    row=np.asarray(pm.eval_vector(v).coords,float)
    if np.linalg.norm(row)<1e-6 or any(np.allclose(row,old,atol=1e-6,rtol=0) for old in coords):
        continue
    unique.append((label,v))
    coords.append(row)
candidate_pairs=unique
in_column={}
for k in range(1,N_int):
    in_column[k]=vectors_in_column_space(lyap[k],[v for _,v in candidate_pairs],pep_context=ctx,resolve_parameters=params_sp,atol=1e-4,rtol=1e-4)
    print(f'V_{k} column-space candidates:')
    for label,v in candidate_pairs:
        if any(v is w for w in in_column[k]):
            print('   '+label)
