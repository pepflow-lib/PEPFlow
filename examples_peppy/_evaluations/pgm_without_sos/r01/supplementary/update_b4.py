"""Add visible candidate search and full reconstruction to the notebook."""
from pathlib import Path

import nbformat as nbf

root = Path(__file__).resolve().parent.parent
nb = nbf.read(root / "pgm_example_lyap.ipynb", as_version=4)
nb.cells = nb.cells[:26]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells += [
md("## Identify the vectors composing the Lyapunov function\n\nStarting from the verified partial sums, we search for an interpretable basis. The interior domain is $1\\le k\\le N-1$; $V_0$ and $V_N$ are reconstructed separately. Rank agreement alone does not establish this basis."),
code("""from itertools import combinations
from pepflow.lyapunov_utils import (
    vectors_in_column_space, find_basis_with_sparsest_coefficients,
    find_symmetric_coefficient_matrix)

b3 = json.loads((notebook_dir / "state/pgm_b3.json").read_text())
assert b3["certificate_id"] == certificate["certificate_id"]
ctx, pb, obj, _ = rebuild_check(notebook_dir, b3, get_pep_setup)
lyap, _, _, record4 = construct(ctx, pb, b3)
params_sp = json.loads(b3["params_json"])
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
N_int = b3["N_verify"]
assert record4["rank_profile"] == b3["rank_profile"]
assert json.loads((notebook_dir / b3["rank_search"]["evidence_path"]).read_text())["summary"] == b3["rank_search"]
for k in range(N_int+1):
    ev = pm.eval_scalar(lyap[k])
    assert np.allclose(ev.inner_prod_coords.astype(float), b3["lyap_inner_prod_coords"][k], atol=1e-4, rtol=1e-5)
    assert np.allclose(ev.func_coords.astype(float), b3["lyap_func_coords"][k], atol=1e-4, rtol=1e-5)
    assert abs(float(ev.offset)-b3["lyap_offsets"][k]) < 1e-4
print("Same-certificate partial sums replayed, including endpoints.")
"""),
md("### Candidate-vector scan\n\nCandidates include tagged iterates, existing basis vectors, point-to-optimum differences, smooth-gradient differences, and composite gradient sums. We add pairwise differences, remove coordinate duplicates and zero vectors, and filter to each quadratic column space."),
code("""candidates_by_k = {}
for k in range(1, N_int+1):
    labeled = [
        ("x0-star", ctx["x_0"]-ctx["x_star"]),
        ("xk-star", ctx[f"x_{k}"]-ctx["x_star"]),
        ("grad_f_k-star", f.grad(ctx[f"x_{k}"])-f.grad(ctx["x_star"])),
        ("grad_f_k", f.grad(ctx[f"x_{k}"])),
        ("grad_g_k+grad_f_star", g.grad(ctx[f"x_{k}"])+f.grad(ctx["x_star"])),
        ("grad_f_k+grad_g_k", f.grad(ctx[f"x_{k}"])+g.grad(ctx[f"x_{k}"]))]
    base = list(ctx.basis_vectors()) + [ctx[f"x_{j}"] for j in range(N_int+1)]
    labeled += [(str(v), v) for v in base]
    labeled += [(f"({u})-({v})", u-v) for u,v in combinations(base,2)]
    unique, seen = [], []
    for label, vector in labeled:
        coords = pm.eval_vector(vector).coords.astype(float)
        if np.linalg.norm(coords) < 1e-6 or any(np.allclose(coords, old, atol=1e-7, rtol=0) for old in seen):
            continue
        unique.append((label, vector))
        seen.append(coords)
    candidates_by_k[k] = unique
"""),
code("""filtered_by_k = {}
labels_by_k = {}
for k, labeled in candidates_by_k.items():
    found = vectors_in_column_space(lyap[k], [v for _,v in labeled],
        pep_context=ctx, resolve_parameters=params_sp, rtol=1e-4, atol=1e-4)
    labels = {id(v): label for label,v in labeled}
    filtered_by_k[k], labels_by_k[k] = found, labels
    print(f"V_{k} column-space candidates:")
    for vector in found:
        print("  ", labels[id(vector)])
"""),
md("### Selected basis pattern\n\nThe sparse search is shown for every nonzero index. We then use a consistent basis across interior indices to make the recurrence interpretable; the chosen basis is checked independently."),
code("""search_bases, search_coefficients = {}, {}
for k in range(1, N_int+1):
    basis_found, matrix_found = find_basis_with_sparsest_coefficients(
        lyap[k], filtered_by_k[k], pep_context=ctx, resolve_parameters=params_sp,
        zero_tol=1e-6, indep_tol=1e-7, span_tol=1e-5)
    search_bases[k], search_coefficients[k] = basis_found, matrix_found
    assert len(basis_found) == b3["rank_profile"][k]
    print(f"k={k}, rank={len(basis_found)}")
    print("sparse basis:", [labels_by_k[k][id(v)] for v in basis_found])
    print("zero coefficients:", int(np.sum(np.abs(matrix_found)<1e-6)), "/", matrix_found.size)
"""),
md(r"""For $1\le k<N$, use the ordered template
$$[\,x_0-x_\star,\ x_k-x_\star,\ \nabla f(x_k)-\nabla f(x_\star),\ \nabla f(x_k)\,].$$
The first two vectors record distances and the last two separate the smooth-gradient difference from the affine-gradient term. At $k=0$ the basis is empty; at $k=N$ it is $[x_0-x_\star]$."""),
code("""def V_k_basis(k):
    if k == 0:
        return []
    anchor = ctx["x_0"]-ctx["x_star"]
    if k == N_int:
        return [anchor]
    return [anchor, ctx[f"x_{k}"]-ctx["x_star"],
            f.grad(ctx[f"x_{k}"])-f.grad(ctx["x_star"]), f.grad(ctx[f"x_{k}"])]


def V_k_basis_labels(k):
    if k == 0:
        return []
    if k == N_int:
        return ["x0-star"]
    return ["x0-star", "xk-star", "grad_f_k-star", "grad_f_k"]


for k in range(N_int+1):
    vectors = V_k_basis(k)
    matrix = np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float) if vectors else np.zeros((len(ctx.basis_vectors()),0))
    rank = int(np.linalg.matrix_rank(matrix, tol=1e-7)) if vectors else 0
    assert rank == len(vectors) == b3["rank_profile"][k]
    print(f"k={k}: rank {rank} basis {V_k_basis_labels(k)}")
"""),
md("### Coefficient matrices\n\nThe quadratic part is $\\sum_{i,j}C_{ij}\\langle v_i,v_j\\rangle$ with symmetric $C$; off-diagonal entries count twice. Function terms are represented by the two gaps $f(x_k)-f(x_\\star)$ and $g(x_k)-g(x_\\star)$. Their numerical weights are retained, and all scalar components are checked."),
code("""coeff_by_k, coefficient_residuals, function_weights = {}, {}, {}
for k in range(N_int+1):
    basis_k = V_k_basis(k)
    target = pm.eval_scalar(lyap[k])
    target_matrix = target.inner_prod_coords.astype(float)
    if basis_k:
        C = find_symmetric_coefficient_matrix(lyap[k], basis_k,
            pep_context=ctx, resolve_parameters=params_sp, indep_tol=1e-7, span_tol=1e-5)
        B = np.column_stack([pm.eval_vector(v).coords for v in basis_k]).astype(float)
        quadratic_error = float(np.linalg.norm(B@C@B.T-target_matrix, ord="fro"))
    else:
        C = np.zeros((0,0))
        quadratic_error = float(np.linalg.norm(target_matrix, ord="fro"))
    assert quadratic_error <= 1e-5*max(1.0, np.linalg.norm(target_matrix, ord="fro"))
    coeff_by_k[k], coefficient_residuals[k] = C, quadratic_error
    if k == 0:
        weights = np.zeros(2)
    else:
        gaps = [f(ctx[f"x_{k}"])-f(ctx["x_star"]), g(ctx[f"x_{k}"])-g(ctx["x_star"])]
        F = np.column_stack([pm.eval_scalar(gap).func_coords for gap in gaps]).astype(float)
        weights = np.linalg.lstsq(F, target.func_coords.astype(float), rcond=None)[0]
        assert np.max(np.abs(F@weights-target.func_coords.astype(float))) < 1e-5
    function_weights[k] = weights.tolist()
    assert abs(float(target.offset)) < 1e-5
    print(f"k={k}: quadratic reconstruction residual {quadratic_error:.3e}")
    if basis_k:
        pf.pprint_labeled_matrix(C, V_k_basis_labels(k), precision=7)
    print("Function gap weights [f_k-f_star, g_k-g_star]:", weights)
    print("Constant offset:", target.offset)
"""),
code("""def V_k_structure(k):
    vectors = V_k_basis(k)
    C = coeff_by_k[k]
    expression = sum((float(C[i,j])*vectors[i]*vectors[j]
        for i,j in np.ndindex(C.shape)), pf.Scalar.zero())
    if k > 0:
        af, ag = function_weights[k]
        expression += af*(f(ctx[f"x_{k}"])-f(ctx["x_star"]))
        expression += ag*(g(ctx[f"x_{k}"])-g(ctx["x_star"]))
    return expression


component_residuals = {}
for k in range(N_int+1):
    evaluated = pm.eval_scalar(V_k_structure(k)-lyap[k])
    target = pm.eval_scalar(lyap[k])
    errors = {}
    for label, residual, reference in (
        ("gram", evaluated.inner_prod_coords, target.inner_prod_coords),
        ("function", evaluated.func_coords, target.func_coords),
        ("offset", evaluated.offset, target.offset)):
        error = float(np.max(np.abs(np.asarray(residual, dtype=float)), initial=0))
        scale = float(np.max(np.abs(np.asarray(reference, dtype=float)), initial=0))
        assert error <= 1e-4+1e-5*scale
        errors[label] = error
    component_residuals[str(k)] = errors
    print("Complete reconstruction", k, errors)
"""),
md(r"""### Block 4 conclusion

Every index, including both endpoints, passes independence and full-expression reconstruction. For $1\le k<N$ the observed structure is
$$V_k=\sum_{i,j=0}^{3}c_{ij}(k,N,L)\langle v_i,v_j\rangle
+a_f(k,N,L)\bigl(f(x_k)-f(x_\star)\bigr)
+a_g(k,N,L)\bigl(g(x_k)-g(x_\star)\bigr).$$
The symmetric coefficient functions remain unresolved. At $k=0$, $V_0=0$ numerically. At $k=N$, the structure has one quadratic coefficient and two function-gap weights, with no constant term. Block 5 must derive the coefficients and establish the exact step, initial and terminal identities; this numerical reconstruction does not prove them."""),
md("## Closed-form coefficients and symbolic identities\n\nPending Block 5."),
]
nbf.write(nb, root / "pgm_example_lyap.ipynb")
