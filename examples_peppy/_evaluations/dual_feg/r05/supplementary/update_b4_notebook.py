"""Add actual basis scan, sparse search, reconstruction and candidate formulas."""
import json
from pathlib import Path
import nbformat
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"dual_feg_example_lyap.ipynb"
nb=nbformat.read(p,as_version=4)
s=json.loads((ROOT/"state/dual_feg_b4.json").read_text())
md=nbformat.v4.new_markdown_cell
code=nbformat.v4.new_code_cell
cells=[
md("## Identify the vectors composing the Lyapunov function\nWe start from the verified partial sums. Interior indices are $1\\leq k\\leq N-1$; both endpoints remain required reconstruction cases."),
code("""from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix
b3 = json.loads((NOTEBOOK_DIR/"state/dual_feg_b3.json").read_text())
certificate = b3
observation = group(certificate)
ctx,pb,obj,pm,weighted_terms,S_scalar,certificate_residuals = recheck(certificate)
ctx.set_as_current()
N_int = certificate["N_verify"]
params_sp = {"L":sp.Integer(1),"R":sp.Integer(1)}
basis = ctx.basis_vectors()
lyap = [sum((float(coords[i][j])*basis[i]*basis[j] for i,j in np.ndindex(np.shape(coords))),pf.Scalar.zero())+offset
        for coords,offset in zip(observation["lyap_inner_prod_coords"],observation["lyap_offsets"])]
assert observation["rank_profile"] == b3["rank_profile"]
assert b3["rank_search"]["boundary_exclusions"] == {"left":1,"right":1}
for k,V in enumerate(lyap):
    evaluated = pm.eval_scalar(V)
    assert np.allclose(evaluated.inner_prod_coords,b3["lyap_inner_prod_coords"][k],atol=1e-4,rtol=1e-5)
    assert np.allclose(evaluated.func_coords,b3["lyap_func_coords"][k],atol=1e-4,rtol=1e-5)
    assert abs(float(evaluated.offset)-b3["lyap_offsets"][k]) <= 1e-4
print("Rebuilt every selected partial sum; interior rank four, endpoints zero and two.")"""),
md("### Candidate-vector scan\nCandidates include all tagged iterates, auxiliary vectors and operator outputs, plus current-to-terminal and initial-to-terminal gaps. Duplicate coordinate vectors and zero vectors are removed."),
code("""candidate_pairs_by_k = {}
for k in range(1,N_int+1):
    pairs=[("A_N",obj(ctx[f"x_{N_int}"])),(f"z_{k}",ctx[f"z_{k}"]),
           (f"x_{k}-x_N",ctx[f"x_{k}"]-ctx[f"x_{N_int}"]),
           ("x_0-x_N",ctx["x_0"]-ctx[f"x_{N_int}"]),
           (f"x_{k}-x_0",ctx[f"x_{k}"]-ctx["x_0"])]
    for i in range(N_int+1):
        for prefix in ["x","z","a"]:
            pairs.append((f"{prefix}_{i}",ctx[f"{prefix}_{i}"]))
    for i in range(N_int):
        for prefix in ["y","b"]:
            pairs.append((f"{prefix}_{i}",ctx[f"{prefix}_{i}"]))
    pairs += [(f"x_{i}-x_N",ctx[f"x_{i}"]-ctx[f"x_{N_int}"]) for i in range(N_int)]
    unique = []
    seen = []
    for label,vector in pairs:
        coordinates = np.asarray(pm.eval_vector(vector).coords,dtype=float)
        if np.linalg.norm(coordinates)<=1e-12 or any(np.allclose(coordinates,v,atol=1e-12,rtol=0) for v in seen):
            continue
        unique.append((label,vector))
        seen.append(coordinates)
    candidate_pairs_by_k[k] = unique"""),
code("""filtered_by_k = {}
labels_by_k = {}
for k,pairs in candidate_pairs_by_k.items():
    labels_by_k[k] = {id(v):label for label,v in pairs}
    inside = vectors_in_column_space(lyap[k],[v for _,v in pairs],pep_context=ctx,
        resolve_parameters={n:v for n,v in params_sp.items()},atol=1e-4,rtol=1e-4)
    filtered_by_k[k] = inside
    print(f"V_{k} column-space candidates:")
    for v in inside:
        print("   "+labels_by_k[k][id(v)])"""),
md("### Selected basis pattern"),
code("""sparse_bases = {}
sparse_coefficients = {}
for k,inside in filtered_by_k.items():
    chosen,C = find_basis_with_sparsest_coefficients(lyap[k],inside,pep_context=ctx,
        resolve_parameters={n:v for n,v in params_sp.items()},
        zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    sparse_bases[k] = chosen
    sparse_coefficients[k] = C
    print(f"k={k}, rank {b3['rank_profile'][k]}")
    print("  sparse basis:", [labels_by_k[k][id(v)] for v in chosen])
    print(f"  zero coefficients: {np.count_nonzero(np.abs(C)<1e-6)}/{C.size}")"""),
md(r"""The sparse search differs at $k=N-1$. We adopt the following consistent independent template to expose the auxiliary recurrence; its reconstruction is checked below:
$$\mathcal B_k=(A(x_N),z_k,x_k-x_N,x_0-x_N),\qquad 1\leq k<N.$$
At $k=0$ the basis is empty. At $k=N$ use $(A(x_N),x_0-x_N)$."""),
code(s["basis_code"]+"""
for k in range(N_int+1):
    vectors = V_k_basis(k)
    rank = int(np.linalg.matrix_rank(np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float),tol=1e-7)) if vectors else 0
    assert rank == len(vectors) == b3["rank_profile"][k]
    print(f"k={k}: rank {rank} basis {V_k_basis_labels(k)}")
"""),
md("### Coefficient matrices\nUse the displayed basis order and the convention $V_k=\\sum_{i,j}C_{ij}\\langle v_i,v_j\\rangle$. The off-diagonal entries contribute twice. Function and constant terms are verified absent."),
code(s["structure_code"]+"""
coeff_by_k = {}
for k in range(N_int+1):
    vectors = V_k_basis(k)
    C = find_symmetric_coefficient_matrix(lyap[k],vectors,pep_context=ctx,
        resolve_parameters={n:v for n,v in params_sp.items()},indep_tol=1e-7,span_tol=1e-5)
    coeff_by_k[k] = C
    diff = pm.eval_scalar(V_k_structure(k)-lyap[k])
    target = pm.eval_scalar(lyap[k])
    error = float(np.linalg.norm(np.asarray(diff.inner_prod_coords,dtype=float),ord="fro"))
    scale = max(1.0,float(np.linalg.norm(np.asarray(target.inner_prod_coords,dtype=float),ord="fro")))
    assert error <= 1e-5*scale
    assert np.max(np.abs(diff.func_coords),initial=0) <= 1e-5
    assert abs(float(diff.offset)) <= 1e-5
    assert np.max(np.abs(target.func_coords),initial=0) == 0 and target.offset == 0
    print(f"k={k}: reconstruction residual {error:.3e}; function terms absent, offset zero.")
    if C.size:
        pf.pprint_labeled_matrix(C,row_labels=V_k_basis_labels(k),column_labels=V_k_basis_labels(k))
"""),
code(s["coeff_code"]+"""
for k,C in coeff_by_k.items():
    candidate = coeff_pattern(k,N_int)
    error = float(np.max(np.abs(candidate-C),initial=0))
    assert error <= 1e-4
    print(f"k={k}: candidate coefficient error {error:.3e}")
other = json.loads((NOTEBOOK_DIR/"supplementary/certificate_N8.json").read_text())
obs8 = group(other)
ctx8,pb8,obj8,pm8,_,_,_ = recheck(other)
ctx8.set_as_current()
for k in range(9):
    vectors = [] if k==0 else ([obj8(ctx8["x_8"]),ctx8["x_0"]-ctx8["x_8"]] if k==8 else
        [obj8(ctx8["x_8"]),ctx8[f"z_{k}"],ctx8[f"x_{k}"]-ctx8["x_8"],ctx8["x_0"]-ctx8["x_8"]])
    B = np.column_stack([pm8.eval_vector(v).coords for v in vectors]).astype(float) if vectors else np.zeros((len(ctx8.basis_vectors()),0))
    error = np.max(np.abs(B@coeff_pattern(k,8)@B.T-np.asarray(obs8["lyap_inner_prod_coords"][k])),initial=0)
    assert error <= 1e-4
    print(f"N=8, k={k}: candidate expression error {error:.3e}")
ctx.set_as_current()
"""),
md(r"""### Block 4 conclusion
For $L=1$ the numerical data suggest, with $a=A(x_N)$ and $t=N-k$,
$$V_k=-4\langle a,z_k\rangle-2\|z_k\|^2+\frac4t\langle a+z_k,x_k-x_N\rangle-\frac4N\langle a,x_0-x_N\rangle,\quad 0\leq k<N,$$
$$V_N=2\|a\|^2-\frac4N\langle a,x_0-x_N\rangle.$$
The formula gives $V_0=0$. All selected numerical partial sums reconstruct, including endpoints, and the candidate fits both tested horizons. These are candidate formulas, not an analytic proof. Block 5 must handle general $L$, exact step and terminal identities, signs, and the final normalization."""),
]
index=next(i for i,c in enumerate(nb.cells) if c.source.startswith("## Special vectors"))
nb.cells[index:index+1]=cells
nbformat.write(nb,p)
print("B4 cells",index,index+len(cells)-1)

