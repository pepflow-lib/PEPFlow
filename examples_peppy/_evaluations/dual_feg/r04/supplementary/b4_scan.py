from itertools import combinations
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix

candidate_pairs = [(f'A(x_{N_int})', obj(ctx[f'x_{N_int}']))]
for k in range(N_int + 1):
    candidate_pairs += [(f'z_{k}', ctx[f'z_{k}']),
                        (f'x_{k}-x_N', ctx[f'x_{k}'] - ctx[f'x_{N_int}']),
                        (f'x_{k}-x_star', ctx[f'x_{k}'] - ctx['x_star']),
                        (f'x_{k}', ctx[f'x_{k}'])]
candidate_pairs += [(str(v), v) for v in ctx.basis_vectors()]
base = list(candidate_pairs)
for (label_a, vec_a), (label_b, vec_b) in combinations(base, 2):
    candidate_pairs.append((f'({label_a})-({label_b})', vec_a - vec_b))
unique_pairs, coordinates = [], []
for label, vector in candidate_pairs:
    coords = np.asarray(pm.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(coords) < 1e-12 or any(np.allclose(coords, old, atol=1e-12, rtol=0) for old in coordinates):
        continue
    unique_pairs.append((label, vector))
    coordinates.append(coords)
candidates = [v for _, v in unique_pairs]
print('Unique nonzero candidates:', len(candidates))
in_column_by_k = {}
for k in range(1, N_int + 1):
    in_col = vectors_in_column_space(lyap[k], candidates, pep_context=ctx, resolve_parameters=params_sp, rtol=1e-4, atol=1e-4)
    in_column_by_k[k] = in_col
    labels_in_col = [label for label, vec in unique_pairs if any(vec is match for match in in_col)]
    print(f'V_{k} column-space candidates:')
    for label in labels_in_col:
        print('   ', label)
