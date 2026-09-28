import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import NOTEBOOK_DIR, configure  # ty: ignore[unresolved-import]

configure()
import inspect  # noqa: E402 - imports follow runtime or notebook setup

import nbformat as nbf  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
from basis import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    V_k_basis,
    V_k_basis_labels,
    discover,
    sample_structure,
)
from jupyter_client import (  # noqa: E402 - imports follow runtime or notebook setup
    KernelManager,
)
from jupyter_client.kernelspec import (  # noqa: E402 - imports follow runtime or notebook setup
    KernelSpecManager,
)
from nbclient import (  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup
    NotebookClient,
)

path = NOTEBOOK_DIR / "pgm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
nb.cells = nb.cells[:24]
nb.cells[23].source = nb.cells[23].source.split("## Special vectors")[0]


def md(s):
    nb.cells.append(nbf.v4.new_markdown_cell(s))


def code(s):
    nb.cells.append(nbf.v4.new_code_cell(s))


md("""## Identify the vectors composing the Lyapunov function

Start from the selected N=4 partial sums with the transported numerical SOS. The interior is k=1,2,3; k=0 and k=4 remain required reconstruction cases. The same rank construction was confirmed at N=6. No new solve is used here.
""")
code("""from pepflow.utils import NUMERICAL_TYPE
b3 = json.loads((notebook_dir / "state/pgm_b3.json").read_text())
ctx, pb, lyap, observation = construct(b3, False)
n = b3["N_verify"]
params: dict[str, NUMERICAL_TYPE] = {"L": sp.S.One, "R": sp.S.One}
pm = pf.ExpressionManager(ctx, resolve_parameters=params)
assert observation["rank_profile"] == b3["rank_profile"]
for k, Vk in enumerate(lyap):
    evaluated = pm.eval_scalar(Vk)
    for actual, saved in (
        (evaluated.inner_prod_coords, b3["lyap_inner_prod_coords"][k]),
        (evaluated.func_coords, b3["lyap_func_coords"][k]),
        (evaluated.offset, b3["lyap_offsets"][k])):
        assert np.allclose(np.asarray(actual, dtype=float), saved, atol=1e-4, rtol=1e-5)
print("Selected rank profile:", observation["rank_profile"])
""")
md("""### Candidate-vector scan

Scan the basis vectors, all iterate-to-solution gaps, gradient differences, and pairwise differences. Remove zero vectors and duplicates by their evaluated coordinates.
""")
src = inspect.getsource(discover)
scan = src[src.index("    base=") : src.index("    outputs=[]")]
scan = "\n".join(line[4:] for line in scan.splitlines())
code(
    """import itertools
from pepflow.lyapunov_utils import (
    vectors_in_column_space, find_basis_with_sparsest_coefficients,
    find_symmetric_coefficient_matrix)
"""
    + scan
)
code("""spanning = {}
for k in range(1, n+1):
    spanning[k] = vectors_in_column_space(
        lyap[k], [v for _, v in candidates], pep_context=ctx,
        resolve_parameters=params, rtol=1e-4, atol=1e-4)
    print(f"V_{k} column-space candidates:")
    for label, v in candidates:
        if any(v is u for u in spanning[k]):
            print("  ", label)
""")
md("""### Selected basis pattern

The sparse search is executed below at every nonzero-rank index. We adopt a common ordering of the same interpretable vectors, which makes the later coefficient comparison simpler.
""")
code("""searched_bases = {}
for k in range(1, n+1):
    selected_basis, selected_C = find_basis_with_sparsest_coefficients(
        lyap[k], spanning[k], pep_context=ctx, resolve_parameters=params,
        zero_tol=1e-6, indep_tol=1e-7, span_tol=1e-5)
    labels = [label for v in selected_basis for label, u in candidates if u is v]
    assert len(selected_basis) == observation["rank_profile"][k]
    searched_bases[k] = selected_basis
    print(f"k={k}: rank {len(selected_basis)}")
    print("  sparse basis:", labels)
    print(f"  zero coefficients: {np.sum(abs(selected_C)<1e-6)}/{selected_C.size}")
""")
md(r"""Let $d_k=x_k-x_\star$ and $a_k=\nabla f(x_k)$. The adopted interior basis is
$$[d_0,\ d_k,\ a_k,\ a_\star-a_k],\qquad 1\leq k<N.$$
At $k=0$ the quadratic part is zero; at $k=N$ use only $[d_0]$. Independence and reconstruction are checked independently of the search ordering.
""")
code(
    inspect.getsource(V_k_basis)
    + "\n"
    + inspect.getsource(V_k_basis_labels)
    + """
for k in range(n+1):
    vectors = V_k_basis(ctx, k, n)
    rank = 0 if not vectors else np.linalg.matrix_rank(
        np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float), tol=1e-7)
    assert rank == len(vectors) == observation["rank_profile"][k]
    print(f"k={k}: rank {rank} basis {V_k_basis_labels(k,n)}")
"""
)
md("""### Coefficient matrices

Use the basis order above with symmetric coefficients; off-diagonal terms occur twice. Function gaps and offsets are reconstructed separately, including both endpoints. Coefficient formulas remain unknown functions for B5.
""")
code(
    inspect.getsource(sample_structure)
    + """
coeff_by_k = {}
sample_values = []
for k in range(n+1):
    vectors = V_k_basis(ctx,k,n)
    target = pm.eval_scalar(lyap[k])
    M = np.asarray(target.inner_prod_coords,dtype=float)
    if vectors:
        B = np.column_stack([pm.eval_vector(v).coords for v in vectors]).astype(float)
        C = find_symmetric_coefficient_matrix(lyap[k],vectors,pep_context=ctx,
            resolve_parameters=params,indep_tol=1e-7,span_tol=1e-5)
        error = np.linalg.norm(B@C@B.T-M)
    else:
        C = np.zeros((0,0))
        error = np.linalg.norm(M)
    assert error <= 1e-5*max(1.,np.linalg.norm(M))
    if k:
        ff = pm.eval_scalar(f(ctx[f"x_{k}"])-f(ctx["x_star"])).func_coords
        gf = pm.eval_scalar(g(ctx[f"x_{k}"])-g(ctx["x_star"])).func_coords
        fg,gg = np.linalg.lstsq(np.column_stack([ff,gf]).astype(float),
                               np.asarray(target.func_coords,dtype=float),rcond=None)[0]
    else:
        fg=gg=0.
    rebuilt = sample_structure(ctx,k,n,C,float(fg),float(gg),float(target.offset))
    diff = pm.eval_scalar(rebuilt-lyap[k])
    errors = [maxabs(diff.inner_prod_coords),maxabs(diff.func_coords),maxabs(diff.offset)]
    assert max(errors) <= 1e-4
    assert float(target.offset) == 0
    coeff_by_k[str(k)] = C
    sample_values.append((float(fg),float(gg),float(target.offset)))
    print(f"k={k}: quadratic reconstruction {error}; component errors {errors}")
    if vectors:
        pf.pprint_labeled_matrix(pf.MatrixWithNames(C,V_k_basis_labels(k,n),V_k_basis_labels(k,n)))
    else:
        print("Empty quadratic basis and 0 by 0 coefficient matrix.")
    print("f(x_k)-f_star coefficient:",fg,"g(x_k)-g_star coefficient:",gg,"offset:",target.offset)
"""
)
md(r"""### Block 4 conclusion

For $1\leq k<N$, the full structure is
$$V_k=\sum_{i,j=0}^3 c_{ij}(k,N,L)\langle v_i,v_j\rangle
+p(k,N)(f(x_k)-f_\star)+q(k,N)(g(x_k)-g_\star),$$
where $v=[d_0,d_k,a_k,a_\star-a_k]$ and $c_{ij}=c_{ji}$. Every independent $c_{ij}$, $p$, and $q$ remains a named analytic unknown. At $k=0$, $V_0=0$. At $k=N$, the only quadratic coefficient is the distinct unknown $t(N,L)$ multiplying $\|d_0\|^2$, with terminal function coefficients retained. All scalar offsets are zero.

The selected numerical partial sums reconstruct at every index. This does not establish the analytic formulas or proof; B5 must derive them and check step, initial, and terminal identities.

## Closed-form coefficients and exact identities (pending)
""")
nbf.write(nb, path)
km = KernelManager(
    kernel_name="attempt",
    kernel_spec_manager=KernelSpecManager(
        kernel_dirs=[str(NOTEBOOK_DIR / "supplementary/.runtime/kernels")]
    ),
)
try:
    NotebookClient(
        nb, km=km, timeout=240, resources={"metadata": {"path": str(NOTEBOOK_DIR)}}
    ).execute()
finally:
    if km.has_kernel:
        km.shutdown_kernel(now=True)
nbf.write(nb, path)
print("B4 notebook executed")
