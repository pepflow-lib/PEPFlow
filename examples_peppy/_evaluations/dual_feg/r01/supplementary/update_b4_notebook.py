import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import nbformat
from nbclient import NotebookClient
root=runtime.ATTEMPT
path=root/'dual_feg_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Special-vector'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Symbolic step'))
md=nbformat.v4.new_markdown_cell
codecell=nbformat.v4.new_code_cell
intro=md('## Identify the vectors composing the Lyapunov function\nThe B3 certificate and partial sums are reconstructed above. B4 searches for interpretable vectors spanning each quadratic form. The interior is $1\\le k\\le N-1$; both endpoints are separately reconstructed. The same grouping had interior rank 4 at N=6 and N=8.')
sanity=codecell('''b3 = json.loads((notebook_dir / "state/dual_feg_b3.json").read_text())
assert certificate_checked and grouping_checked
assert certificate["certificate_id"] == b3["certificate_id"]
assert ranks == b3["rank_profile"]
for k, Vk in enumerate(lyap):
    ev = pm.eval_scalar(Vk)
    for actual, saved in ((ev.inner_prod_coords, b3["lyap_inner_prod_coords"][k]), (ev.func_coords, b3["lyap_func_coords"][k]), (ev.offset, b3["lyap_offsets"][k])):
        assert np.allclose(np.asarray(actual,dtype=float), np.asarray(saved,dtype=float), atol=1e-4, rtol=1e-5)
print("Same-certificate partial sums rechecked at all indices.")
''')
scan=(root/'supplementary/b4_scan_cells.py').read_text(encoding='utf-8-sig')
construct,rest=scan.split('spanning_by_k={}',1)
filtering,search=rest.split('searched_basis={}',1)
basis=(root/'supplementary/b4_basis.py').read_text(encoding='utf-8-sig')
coeff=(root/'supplementary/b4_coefficients.py').read_text(encoding='utf-8-sig')
structure=(root/'supplementary/b4_structure.py').read_text(encoding='utf-8-sig')
final=(root/'supplementary/finalize_b4.py').read_text(encoding='utf-8-sig')
checks='component_residuals={}' + final.split('component_residuals={}',1)[1].split('\nunknowns=',1)[0]
checks+='\nprint("Full-component reconstruction errors:", component_residuals)\n'
nb.cells[start:end]=[intro,sanity,md('### Candidate-vector scan\nCandidates include all auxiliary $z_j$, operator values, iterate-to-terminal gaps, pairwise point differences, and original basis vectors. Zero and duplicate coordinate vectors are removed before column-space filtering.'),codecell(construct),codecell('spanning_by_k={}'+filtering),md('### Selected basis pattern\nThe following search maximizes coefficient sparsity among independent subsets of the actual filtered candidates.'),codecell('searched_basis={}'+search),md(r'''The search finds equivalent special choices at the first and penultimate indices. For a uniform recurrence description, adopt the verified interior basis
$$\mathcal B_k=[x_0-x_N,\ z_k,\ x_k-x_N,\ A(x_N)],\qquad 1\le k\le N-1.$$
Use $\mathcal B_0=[]$ and $\mathcal B_N=[x_0-x_N,A(x_N)]$. The next checks verify independence and the adopted basis's reconstruction, including indices where the sparse search selected another basis.'''),codecell(basis),md('### Coefficient matrices\nUse the basis order just displayed. Each symmetric coefficient matrix represents $V_k=\\sum_{i,j}C_{ij}\\langle v_i,v_j\\rangle$, so off-diagonal entries contribute twice. There are no function-value or constant terms.'),codecell(coeff),codecell(structure+'\n'+checks),md(r'''### Block 4 conclusion
The verified numerical structure is
$$V_0=0,\quad V_k=\mathcal B_k^T C(k,N,L)\mathcal B_k\ (1\le k\le N-1),\quad V_N=\mathcal B_N^T T(N,L)\mathcal B_N.$$
All independent entries $c_{ij}(k,N,L)$ for $0\le i\le j\le3$ and $t_{ij}(N,L)$ for $0\le i\le j\le1$ are passed to B5 as named unknown coefficient functions. The printed fractions are numerical observations, not formulas. Function and constant terms are verified absent. Every index passed independence and full-expression reconstruction. B5 must derive the coefficients and verify exact step, initial, and terminal identities before any theorem is claimed.''')]
nbformat.write(nb,path)
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
NotebookClient(nb,timeout=120,kernel_name='dual-feg-attempt',resources={'metadata':{'path':str(root)}}).execute()
nbformat.write(nb,path)
print('B4 notebook replay passed')
