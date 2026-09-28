import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat as nb
root=runtime.ATTEMPT
path=root/'pgm_example_lyap.ipynb'
book=nb.read(path,as_version=4)
scan=(root/'supplementary/scan_b4.py').read_text()
build=scan[scan.index('base='):scan.index('observations={}')] 
new=[nb.v4.new_markdown_cell(r'''## Identify the vectors composing the Lyapunov function
We now use the rechecked Block 3 partial sums from the same numerical certificate. The common interior rank is 4 at horizons 4 and 6. The initial and terminal terms are handled separately, and every index must pass reconstruction.'''),
nb.v4.new_code_cell('''b3=json.loads((notebook_dir/"state/pgm_b3.json").read_text())
assert b3["certificate_id"]==b2["certificate_id"]
assert ranks==b3["rank_profile"]
for k,Vk in enumerate(lyap):
    ev=pm.eval_scalar(Vk)
    assert np.allclose(np.asarray(ev.inner_prod_coords,dtype=float),b3["lyap_inner_prod_coords"][k],atol=1e-4,rtol=1e-5)
    assert np.allclose(np.asarray(ev.func_coords,dtype=float),b3["lyap_func_coords"][k],atol=1e-4,rtol=1e-5)
    assert abs(float(ev.offset)-b3["lyap_offsets"][k])<=1e-4
print("Verified same-certificate partial sums; interior indices",list(range(1,N)),"exceptional indices",[0,N])'''),
nb.v4.new_markdown_cell(r'''### Candidate-vector scan
Candidates include tagged iterates, basis vectors, smooth gradients, shifted proximal subgradients, composite gradients, point-to-optimum gaps, and pairwise differences. Zero vectors and coordinate duplicates are removed before scanning.'''),
nb.v4.new_code_cell('''from itertools import combinations
from pepflow.lyapunov_utils import vectors_in_column_space, find_basis_with_sparsest_coefficients

ctx=ctx_b2
params_sp={"L":sp.S.One,"R":sp.S.One}
'''+build),
nb.v4.new_code_cell('''in_col_by_k={}
for k in range(1,N+1):
    in_col=vectors_in_column_space(lyap[k],[v for _,v in candidate_pairs],
        pep_context=ctx_b2,resolve_parameters=params_sp,atol=1e-4,rtol=1e-4)
    in_col_by_k[k]=in_col
    print(f"V_{k} column-space candidates:")
    for v in in_col:
        print("   "+labels[id(v)])'''),
nb.v4.new_markdown_cell(r'''### Selected basis pattern
The exhaustive sparse-subset search below is performed on the actual filtered candidates, with the frozen tolerances. We then adopt a consistent coordinate order that avoids changing the basis formula between interior indices.'''),
nb.v4.new_code_cell('''searched_basis={}
searched_C={}
for k in range(1,N+1):
    selected,C=find_basis_with_sparsest_coefficients(lyap[k],in_col_by_k[k],
        pep_context=ctx_b2,resolve_parameters=params_sp,zero_tol=1e-6,indep_tol=1e-7,span_tol=1e-5)
    assert len(selected)==ranks[k]
    searched_basis[k]=selected
    searched_C[k]=C
    print(f"k={k}, rank {ranks[k]}")
    print("  sparse basis:",[labels[id(v)] for v in selected])
    print("  zero coefficients:",int(np.sum(np.abs(C)<1e-6)),"/",C.size)'''),
nb.v4.new_markdown_cell(r'''For $1\le k<N$, adopt the ordered basis
$$[a_\star,\ x_0-x_\star,\ x_k-x_\star,\ a_k-a_\star].$$
This spans the same space as the search-selected bases and has a simpler uniform template. The initial basis is empty; the terminal basis is $[x_0-x_\star]$. The next cell verifies independence and the adopted decomposition at all indices.'''),
nb.v4.new_code_cell((root/'supplementary/b4_basis.py').read_text()),
nb.v4.new_markdown_cell(r'''### Coefficient matrices
For the chosen basis, the quadratic part is $\sum_{i,j}C_{ij}\langle v_i,v_j\rangle$, with off-diagonal coefficients counted twice. Function values are represented separately by $A_k(f(x_k)-f_\star)+B_k(g(x_k)-g_\star)$. Scalar offsets are checked to vanish. The displayed matrices and gap coefficients are numerical samples.'''),
nb.v4.new_code_cell((root/'supplementary/b4_extract.py').read_text()),
nb.v4.new_markdown_cell(r'''### Block 4 conclusion
All indices, including $0$ and $N$, pass independence and full-component reconstruction. The interior expression has the form
$$V_k=\sum_{i,j=0}^{3}c_{ij}(k,N,L)\langle v_i,v_j\rangle+A(k,N,L)(f(x_k)-f_\star)+B(k,N,L)(g(x_k)-g_\star).$$
Here $c_{ij}=c_{ji}$; the ten independent entries and $A,B$ remain named unknown functions for analytic derivation. $V_0=0$. The terminal expression uses a single coefficient $c_{\mathrm{terminal}}(N,L)$ on $\|x_0-x_\star\|^2$ and separate terminal objective-gap coefficients. There is no constant term. Numerical reconstruction is complete; Block 5 must derive closed forms and verify exact step, base, and boundary identities.'''),
nb.v4.new_markdown_cell('## Closed-form theorem and exact identities\nPending Block 5.')]
book.cells=book.cells[:15]+new
nb.write(book,path)
print('B4 mathematical source cells added.')
