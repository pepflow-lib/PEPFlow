import ast
import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
path = root / "pgm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
b4 = json.loads((root / "state/pgm_b4.json").read_text())
source = (root / "supplementary/helpers/basis_structure.py").read_text(
    encoding="utf-8-sig"
)
extract = ast.get_source_segment(
    source,
    next(
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name == "extract_structure"
    ),
)
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Identify the vectors")
)
end = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Symbolic step")
)
cells = [
    nbf.v4.new_markdown_cell("""## Identify the vectors composing the Lyapunov function
Block 4 uses the selected blended partial sums and the same certificate. The interior domain is $1\leq k\leq N-1$; both endpoints remain part of the reconstruction. The preceding two-horizon comparison is discovery evidence, while the following tests check the actual basis and full scalar expression at every selected-horizon index."""),
    nbf.v4.new_code_cell("""b4 = json.loads((notebook_dir / "state/pgm_b4.json").read_text())
trial = construct(b4, variant=b4["rank_search"]["recipe_id"])
ctx, pm, lyap = trial["ctx"], trial["pm"], trial["lyap"]
N_int = b4["N"]
assert trial["observation"]["rank_profile"] == b4["rank_profile"]
for k,V in enumerate(lyap):
    value=pm.eval_scalar(V)
    assert np.allclose(value.inner_prod_coords,b4["lyap_inner_prod_coords"][k],atol=1e-5,rtol=1e-5)
    assert np.allclose(value.func_coords,b4["lyap_func_coords"][k],atol=1e-5,rtol=1e-5)
    assert abs(value.offset-b4["lyap_offsets"][k])<=1e-5
print("Selected B3 partial sums replayed at all indices; rank profile:",b4["rank_profile"])"""),
    nbf.v4.new_markdown_cell("""### Candidate-vector scan
Candidates include tagged iterates, basis vectors, all available smooth gradients and proximal subgradients, their pairwise differences, and the meaningful point and gradient gaps. Zero and coordinate-duplicate vectors are removed, with preferred descriptive labels first."""),
    nbf.v4.new_code_cell("""from itertools import combinations
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients, find_symmetric_coefficient_matrix

candidate_pairs = {}
for k in range(1,N_int+1):
    x=ctx[f"x_{k}"]
    a=setup.f.grad(x)
    pairs=[("x_0-x_star",ctx["x_0"]-ctx["x_star"])]
    if k<N_int:
        pairs += [(f"x_{k}-x_star",x-ctx["x_star"]),(f"a_{k}",a),(f"a_{k}-a_star",a-setup.f.grad(ctx["x_star"]))]
    base=[(str(v),v) for v in ctx.basis_vectors()]
    base += [(f"x_{i}",ctx[f"x_{i}"]) for i in range(N_int+1)]+[("x_star",ctx["x_star"])]
    base += [(f"a_{i}",setup.f.grad(ctx[f"x_{i}"])) for i in range(N_int+1)]
    base += [(f"s_{i}",setup.g.grad(ctx[f"x_{i}"])) for i in range(1,N_int+1)]
    base += [("a_star",setup.f.grad(ctx["x_star"]))]
    pairs += base
    pairs += [(f"({name1})-({name2})",v1-v2) for (name1,v1),(name2,v2) in combinations(base,2)]
    unique=[]
    coordinates=[]
    for label,vector in pairs:
        row=np.asarray(pm.eval_vector(vector).coords,dtype=float)
        if np.linalg.norm(row)<=1e-12 or any(np.allclose(row,old,atol=1e-12,rtol=0) for old in coordinates):
            continue
        unique.append((label,vector))
        coordinates.append(row)
    candidate_pairs[k]=unique"""),
    nbf.v4.new_code_cell("""spanning_by_k={}
labels_by_k={}
for k,pairs in candidate_pairs.items():
    spanning_by_k[k]=vectors_in_column_space(lyap[k],[v for _,v in pairs],pep_context=ctx,
        resolve_parameters={"L":sp.S.One,"R":sp.S.One},rtol=1e-4,atol=1e-4)
    labels_by_k[k]={id(v):label for label,v in pairs}
    print(f"V_{k} column-space candidates:")
    for vector in spanning_by_k[k]:
        print("   "+labels_by_k[k][id(vector)])"""),
    nbf.v4.new_markdown_cell(r"""### Selected basis pattern
The sparse search below selects a consistent interior pattern
$$[x_0-x_\star,\ x_k-x_\star,\ a_k,\ a_k-a_\star].$$
At $k=0$ the quadratic part is zero and has an empty basis. At $k=N$ the basis is $[x_0-x_\star]$. The same templates are then independently checked against each partial sum."""),
    nbf.v4.new_code_cell(
        """sparse_basis_by_k={}
sparse_coefficients={}
for k in range(1,N_int+1):
    basis,C=find_basis_with_sparsest_coefficients(lyap[k],spanning_by_k[k],pep_context=ctx,
        resolve_parameters={"L":sp.S.One,"R":sp.S.One},zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    assert len(basis)==b4["rank_profile"][k]
    sparse_basis_by_k[k]=basis
    sparse_coefficients[k]=C
    print(f"k={k}: rank {len(basis)}; sparse basis: {[labels_by_k[k][id(v)] for v in basis]}")
    print(f"zero coefficients: {int(np.sum(abs(C)<1e-6))}/{C.size}")
"""
        + b4["basis_code"]
        + """
for k in range(N_int+1):
    basis=V_k_basis(k,ctx,N_int)
    B=np.column_stack([pm.eval_vector(v).coords for v in basis]).astype(float) if basis else np.zeros((len(ctx.basis_vectors()),0))
    rank=int(np.linalg.matrix_rank(B,tol=1e-7)) if basis else 0
    assert rank==len(basis)==b4["rank_profile"][k]
    print(f"k={k}: rank {rank} basis {V_k_basis_labels(k,N_int)}")"""
    ),
    nbf.v4.new_markdown_cell("""### Coefficient matrices
The basis order is exactly the displayed template. Symmetric off-diagonal matrix entries contribute twice to the quadratic form. Function-value gaps and the scalar offset are reconstructed separately. All formulas below are candidates supported by this selected sample; no arbitrary-horizon conclusion follows from a fit."""),
    nbf.v4.new_code_cell(
        b4["coeff_code"]
        + "\n"
        + b4["structure_code"]
        + "\n"
        + extract
        + """
coeff_by_k, function_coefficients, offset_coefficients, structure_errors = extract_structure(trial,N_int)
for k,C in coeff_by_k.items():
    labels=V_k_basis_labels(k,N_int)
    print(f"k={k}: quadratic Frobenius residual={structure_errors[k]['quadratic_frobenius']:.8g}")
    if C.size:
        pf.pprint_labeled_matrix(C,labels,precision=8)
        print("Candidate coefficient matrix:")
        pf.pprint_labeled_matrix(np.asarray(coeff_pattern(k,N_int),dtype=object),labels)
    else:
        print("Empty 0-by-0 quadratic matrix.")
    print("Coefficients of f-gap and g-gap:",function_coefficients[k],"offset:",offset_coefficients[k])
    print("Full-component residuals:",structure_errors[k]["components"])
    print("Candidate matrix maximum discrepancy:",structure_errors[k]["candidate_coefficient_max_abs"])"""
    ),
    nbf.v4.new_markdown_cell(r"""### Block 4 conclusion
For $1\leq k<N$, put $d_k=x_k-x_\star$ and $a_k=\nabla f(x_k)$. The reconstructed structure suggests
$$V_k=-\frac{L}{4N}\|d_0\|^2+\frac{L(N-k)}{(2N-k)^2}\|d_k\|^2-\frac{\langle a_k,d_k\rangle}{2N-k}+\frac{\|a_k-a_\star\|^2}{2L(2N-k)}+\frac{k+1}{2N-k}(f_k-f_\star)+\frac{k}{2N-k}(g_k-g_\star).$$
The endpoint candidates are $V_0=0$ and $V_N=h(x_N)-h(x_\star)-L\|d_0\|^2/(4N)$. There are no scalar offset terms. The actual numerical matrix coefficients and gap coefficients reconstruct all selected partial sums within the frozen tolerances, including both endpoints. These numerical checks use the blended pieces; B5 must derive and verify the exact formulas and all step/base/boundary identities. Analytic full-PEP and Lyapunov proof statuses remain false."""),
]
nb.cells[start:end] = cells
nbf.write(nb, path)
print("B4 notebook sections updated")
