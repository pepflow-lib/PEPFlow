# %% Rebuild
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix

b3 = json.loads((notebook_dir / "state" / "ogm_b3.json").read_text())
observation, coordinates, coverage = build_partial_sums(b3, notebook_dir)
ctx, pb, obj, pm, weighted_terms, checks = check_certificate(b3, notebook_dir)
params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.Integer(1), "R": sp.Integer(1)}
N_int = b3["N"]
lyap = [pf.Scalar.zero()]
for k in range(N_int):
    increment = sum((weighted_terms[name] for name, step in b3["grouping_coverage"]["constraint_assignment"].items() if step == k), pf.Scalar.zero())
    lyap.append(lyap[-1] + increment)
for k, Vk in enumerate(lyap):
    value = pm.eval_scalar(Vk)
    for actual, saved in ((value.inner_prod_coords,b3["lyap_inner_prod_coords"][k]),(value.func_coords,b3["lyap_func_coords"][k]),(value.offset,b3["lyap_offsets"][k])):
        assert np.allclose(np.asarray(actual,dtype=float),saved,atol=1e-4,rtol=1e-5)
rank_evidence = json.loads((notebook_dir / b3["rank_search"]["evidence_path"]).read_text())
assert rank_evidence["summary"] == b3["rank_search"]
print("Selected rank profile:", observation["rank_profile"], "; retained k=2,...,N; exceptions k=0,1")
# %% Candidates
candidates = []
def add_candidate(label, vector):
    coords = np.asarray(pm.eval_vector(vector).coords,dtype=float)
    if np.linalg.norm(coords) < 1e-7:
        return
    if any(np.allclose(coords,np.asarray(pm.eval_vector(v).coords,dtype=float),atol=1e-7,rtol=0) for _,v in candidates):
        return
    candidates.append((label,vector))

for k in range(N_int+1):
    add_candidate(f"x_{k}-x_star",ctx[f"x_{k}"]-ctx["x_star"])
    add_candidate(f"z_{k}-x_star",ctx[f"z_{k}"]-ctx["x_star"])
    add_candidate(f"g_{k}",obj.grad(ctx[f"x_{k}"]))
    add_candidate(f"z_{k}-x_{k}",ctx[f"z_{k}"]-ctx[f"x_{k}"])
    if k:
        add_candidate(f"y_{k}-x_star",ctx[f"y_{k}"]-ctx["x_star"])
        add_candidate(f"x_{k}-x_{k-1}",ctx[f"x_{k}"]-ctx[f"x_{k-1}"])
for vector in ctx.basis_vectors():
    add_candidate(str(vector),vector)
in_col_by_k = {}
for k in range(1,N_int+1):
    in_col_by_k[k] = vectors_in_column_space(lyap[k],[v for _,v in candidates],pep_context=ctx,resolve_parameters=params_sp,atol=1e-4,rtol=1e-4)
    print(f"V_{k} column-space candidates:")
    for label,vector in candidates:
        if any(vector is c for c in in_col_by_k[k]):
            print("  ",label)
# %% Search
sparse_search = {}
for k in range(1,N_int+1):
    sparse_basis, sparse_C = find_basis_with_sparsest_coefficients(lyap[k],in_col_by_k[k],pep_context=ctx,resolve_parameters=params_sp,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    labels = [next(label for label,v in candidates if v is vector) for vector in sparse_basis]
    sparse_search[k] = dict(labels=labels,zero_count=int(np.sum(np.abs(sparse_C)<1e-6)),total=sparse_C.size)
    print(f"k={k}: rank {b3['rank_profile'][k]}; sparse basis: {labels}")
    print(f"zero coefficients: {sparse_search[k]['zero_count']}/{sparse_C.size}")
# %% Basis
def V_k_basis(k):
    if k == 0:
        return []
    if k == 1:
        return [ctx["x_0"]-ctx["x_star"],ctx["z_1"]-ctx["x_star"],obj.grad(ctx["x_1"])]
    return [ctx["x_0"]-ctx["x_star"],ctx[f"z_{k}"]-ctx["x_star"],ctx[f"x_{k}"]-ctx["x_star"],obj.grad(ctx[f"x_{k}"])]

def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == 1:
        return ["x_0-x_star","z_1-x_star","g_1"]
    return ["x_0-x_star",f"z_{k}-x_star",f"x_{k}-x_star",f"g_{k}"]

for k in range(N_int+1):
    basis = V_k_basis(k)
    B = np.asarray(np.column_stack([pm.eval_vector(v).coords for v in basis]),dtype=float) if basis else np.zeros((len(ctx.basis_vectors()),0))
    basis_rank = int(np.linalg.matrix_rank(B,tol=1e-7))
    assert basis_rank == len(basis) == b3["rank_profile"][k]
    print(f"k={k}: rank {basis_rank} basis {V_k_basis_labels(k)}")
# %% Coefficients
coeff_by_k, coefficient_residuals, function_coefficients, gauge_coefficients = {}, {}, {}, {}
for k in range(N_int+1):
    basis = V_k_basis(k)
    C = find_symmetric_coefficient_matrix(lyap[k],basis,pep_context=ctx,resolve_parameters=params_sp,indep_tol=1e-7,span_tol=1e-5)
    coeff_by_k[k] = C
    assert np.array_equal(C,C.T)
    B = np.asarray(np.column_stack([pm.eval_vector(v).coords for v in basis]),dtype=float) if basis else np.zeros((len(ctx.basis_vectors()),0))
    value = pm.eval_scalar(lyap[k])
    matrix = np.asarray(value.inner_prod_coords,dtype=float)
    coefficient_residuals[k] = float(np.linalg.norm(B@C@B.T-matrix,ord="fro"))
    assert coefficient_residuals[k] <= 1e-5*max(1.,np.linalg.norm(matrix,ord="fro"))
    function_vector = np.asarray(value.func_coords,dtype=float)
    function_coefficients[k] = [float(function_vector[j+1]) for j in range(k+1)]
    gauge_coefficients[k] = float(np.sum(function_vector))
    assert np.allclose(function_vector[k+2:],0,atol=1e-5,rtol=0)
    assert abs(value.offset) < 1e-5
    print(f"k={k}, quadratic reconstruction residual {coefficient_residuals[k]:.3e}")
    if basis:
        pf.pprint_labeled_matrix(pf.MatrixWithNames(C,V_k_basis_labels(k),V_k_basis_labels(k)))
    print("Coefficients of f(x_j)-f_star, j=0,...,k:",function_coefficients[k])
    print("Residual f_star gauge coefficient:",gauge_coefficients[k],"; offset:",value.offset)
# %% Structure
def V_k_structure(k):
    basis = V_k_basis(k)
    C = coeff_by_k[k]
    quadratic = sum((float(C[i,j])*basis[i]*basis[j] for i,j in np.ndindex(C.shape)),pf.Scalar.zero())
    function_terms = sum((function_coefficients[k][j]*(obj(ctx[f"x_{j}"])-obj(ctx["x_star"])) for j in range(k+1)),pf.Scalar.zero())
    return quadratic + function_terms + gauge_coefficients[k]*obj(ctx["x_star"])

component_residuals = {}
for k in range(N_int+1):
    diff = pm.eval_scalar(V_k_structure(k)-lyap[k])
    target = pm.eval_scalar(lyap[k])
    component_residuals[k] = {}
    for name,coords,reference in (("gram",diff.inner_prod_coords,target.inner_prod_coords),("function",diff.func_coords,target.func_coords),("offset",diff.offset,target.offset)):
        error = float(np.max(np.abs(np.asarray(coords,dtype=float)),initial=0))
        scale = float(np.max(np.abs(np.asarray(reference,dtype=float)),initial=0))
        assert error <= 1e-4+1e-5*scale
        component_residuals[k][name] = error
print("Full-coordinate reconstruction:",component_residuals)
