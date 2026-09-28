"""Visible candidate scan, basis search, and full-expression reconstruction."""

SANITY = """b3 = json.loads((notebook_dir / "state/ogm_b3.json").read_text())
assert b3["certificate_id"] == b2["certificate_id"]
assert ranks == b3["rank_profile"]
assert b3["rank_search"]["status"] == "confirmed"
assert b3["rank_search"]["boundary_exclusions"] == {"left":1,"right":1}
for k, Vk in enumerate(lyap):
    ev = pm.eval_scalar(Vk)
    for actual, saved in [(ev.inner_prod_coords,b3["lyap_inner_prod_coords"][k]),
                          (ev.func_coords,b3["lyap_func_coords"][k]),(ev.offset,b3["lyap_offsets"][k])]:
        assert np.allclose(np.asarray(actual,dtype=float), np.asarray(saved,dtype=float), atol=1e-4, rtol=1e-5)
print("Rebuilt selected certificate and all partial sums; interior k=1,...,N-1, exceptions k=0,N.")
"""

SCAN = """from itertools import combinations
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix

candidate_pairs = [("d_0", ctx["x_0"]-ctx["x_star"]),
                   ("q_N", ctx[f"z_{N}"]-ctx["x_star"]-(theta[N]/L)*ctx[f"g_{N}"])]
for k in range(N):
    candidate_pairs.append((f"z_{k+1}-x_star",ctx[f"z_{k+1}"]-ctx["x_star"]))
for k in range(N+1):
    candidate_pairs.extend([(f"g_{k}",ctx[f"g_{k}"]), (f"x_{k}-x_star",ctx[f"x_{k}"]-ctx["x_star"])])
base_pairs = [(str(v),v) for v in ctx.basis_vectors()]
for k in range(N+1):
    base_pairs.extend([(f"x_{k}",ctx[f"x_{k}"]),(f"z_{k}",ctx[f"z_{k}"])])
for k in range(1,N+1):
    base_pairs.append((f"y_{k}",ctx[f"y_{k}"]))
candidate_pairs.extend(base_pairs)
for (label_a,vec_a),(label_b,vec_b) in combinations(base_pairs,2):
    candidate_pairs.append((f"({label_a})-({label_b})",vec_a-vec_b))
unique_pairs, unique_coords = [], []
for label, vector in candidate_pairs:
    coords = np.asarray(pm.eval_vector(vector).coords,dtype=float)
    if np.linalg.norm(coords) <= 1e-6:
        continue
    if any(np.allclose(coords,other,atol=1e-6,rtol=0) for other in unique_coords):
        continue
    unique_pairs.append((label,vector))
    unique_coords.append(coords)
candidate_pairs = unique_pairs
candidate_labels = {id(v):label for label,v in candidate_pairs}
print("Unique nonzero candidate vectors:",len(candidate_pairs))
"""

FILTER = """spanning_by_k = {}
for k in range(1,N+1):
    in_col = vectors_in_column_space(lyap[k],[v for _,v in candidate_pairs],pep_context=ctx,
                                    resolve_parameters=params_sp,rtol=1e-4,atol=1e-4)
    spanning_by_k[k] = in_col
    print(f"V_{k} column-space candidates:")
    for v in in_col:
        print("  "+candidate_labels[id(v)])
"""

SEARCH = """searched_basis, searched_coeff = {}, {}
for k in range(1,N+1):
    chosen, C = find_basis_with_sparsest_coefficients(lyap[k],spanning_by_k[k],pep_context=ctx,
        resolve_parameters=params_sp,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    assert len(chosen) == ranks[k]
    searched_basis[k], searched_coeff[k] = chosen,C
    print(f"k={k}, rank={ranks[k]}")
    print("  sparse basis:",[candidate_labels[id(v)] for v in chosen])
    print(f"  zero coefficients: {int(np.sum(np.abs(C)<1e-6))}/{C.size}")
"""

BASIS = """def V_k_basis(k):
    if k == 0:
        return []
    d0 = ctx["x_0"]-ctx["x_star"]
    if k == N:
        return [d0,ctx[f"z_{N}"]-ctx["x_star"]-(theta[N]/L)*ctx[f"g_{N}"]]
    return [d0,ctx[f"z_{k+1}"]-ctx["x_star"],ctx[f"g_{k}"]]

def V_k_basis_labels(k):
    if k == 0:
        return []
    return ["d_0","q_N"] if k == N else ["d_0",f"z_{k+1}-x_star",f"g_{k}"]

for k in range(N+1):
    vectors = V_k_basis(k)
    matrix = np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float) if vectors else np.zeros((len(basis),0))
    basis_rank = int(np.linalg.matrix_rank(matrix,tol=1e-7))
    assert basis_rank == len(vectors) == ranks[k]
    print(f"k={k}: rank {basis_rank} basis {V_k_basis_labels(k)}")
"""

EXTRACT = """coeff_by_k, coefficient_residuals, alpha_by_k, component_residuals = {}, {}, {}, {}
for k in range(N+1):
    vectors = V_k_basis(k)
    C = find_symmetric_coefficient_matrix(lyap[k],vectors,pep_context=ctx,resolve_parameters=params_sp,
        indep_tol=1e-7,span_tol=1e-5) if vectors else np.zeros((0,0))
    coeff_by_k[k] = C
    target = pm.eval_scalar(lyap[k])
    matrix = np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float) if vectors else np.zeros((len(basis),0))
    target_gram = np.asarray(target.inner_prod_coords,dtype=float)
    residual = float(np.linalg.norm(matrix@C@matrix.T-target_gram,ord="fro"))
    assert residual <= 1e-5*max(1.0,float(np.linalg.norm(target_gram,ord="fro")))
    assert np.array_equal(C,C.T) and np.all(np.isfinite(C))
    coefficient_residuals[k] = residual
    gap = obj(ctx[f"x_{k}"])-obj(ctx["x_star"])
    gap_coords = np.asarray(pm.eval_scalar(gap).func_coords,dtype=float)
    target_func = np.asarray(target.func_coords,dtype=float)
    alpha_by_k[k] = float(np.dot(gap_coords,target_func)/np.dot(gap_coords,gap_coords))
    assert np.allclose(alpha_by_k[k]*gap_coords,target_func,atol=1e-5,rtol=1e-5)
    assert abs(float(target.offset)) <= 1e-5
    print(f"k={k}: quadratic reconstruction residual {residual:.3e}; function coefficient {alpha_by_k[k]:.12g}; offset {float(target.offset):.3e}")
    if C.size:
        pf.pprint_labeled_matrix(C,V_k_basis_labels(k),precision=8)

def V_k_structure(k):
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    quadratic = sum((float(C[i,j])*vectors[i]*vectors[j] for i,j in np.ndindex(C.shape)),pf.Scalar.zero())
    return quadratic + alpha_by_k[k]*(obj(ctx[f"x_{k}"])-obj(ctx["x_star"]))

for k in range(N+1):
    ev = pm.eval_scalar(V_k_structure(k)-lyap[k])
    errors = {label:float(np.max(np.abs(np.asarray(coords,dtype=float)),initial=0))
              for label,coords in [("gram",ev.inner_prod_coords),("function",ev.func_coords),("offset",ev.offset)]}
    assert max(errors.values()) <= 1e-4
    component_residuals[str(k)] = errors
print("Complete Gram/function/offset reconstruction passed at every index.")
"""

FIT = """def coeff_pattern(k, horizon, L_value=1.0):
    ts = theta_sequence(horizon)
    tau = L_value/(2*ts[-1]**2)
    if k == 0:
        return np.zeros((0,0))
    if k == horizon:
        return np.diag([-tau,tau])
    return np.diag([-tau,tau,-ts[k]**2/(L_value*ts[-1]**2)])

def alpha_pattern(k, horizon):
    ts = theta_sequence(horizon)
    return 0.0 if k == 0 else 1.0 if k == horizon else 2*ts[k]**2/ts[-1]**2

formula_residuals = {}
for k in range(N+1):
    candidate_C = coeff_pattern(k,N)
    error = float(np.max(np.abs(candidate_C-coeff_by_k[k]),initial=0))
    alpha_error = abs(alpha_pattern(k,N)-alpha_by_k[k])
    assert error <= 1e-4 and alpha_error <= 1e-4
    formula_residuals[str(k)] = {"matrix":error,"function_coefficient":alpha_error}
    print(f"k={k}: candidate matrix/function coefficient errors {error:.3e}, {alpha_error:.3e}")
    if candidate_C.size:
        pf.pprint_labeled_matrix(candidate_C-coeff_by_k[k],V_k_basis_labels(k),precision=10)
print("Coefficient formulas are numerical candidates, not an arbitrary-horizon proof.")
"""
