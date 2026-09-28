import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import contextlib
import os
import nbformat as nbf
from nbclient import NotebookClient
root=runtime.ROOT
with (root/'supplementary/b4-verification.log').open('w') as log,contextlib.redirect_stdout(log):
    exec(compile((root/'supplementary/run_b4.py').read_text(encoding='utf-8-sig'),'run_b4.py','exec'))
    exec(compile((root/'supplementary/save_b4.py').read_text(encoding='utf-8-sig'),'save_b4.py','exec'))
nb=nbf.read(root/'pgm_example_lyap.ipynb',as_version=4)
nb.cells=nb.cells[:38]
nb.cells[35].source=nb.cells[35].source.replace('"boundary_S": boundary_S}', '"boundary_S": boundary_S, "ctx": ctx, "pm": pm, "lyap": lyap, "params": params}')
nb.cells.append(nbf.v4.new_markdown_cell('## Identify the vectors composing the Lyapunov function\nWe replay the selected N=4 partial sums and search their column spaces. The interior domain is 1 through N-1; both endpoints retain independent reconstruction obligations. Cross-horizon evidence is recorded above.'))
nb.cells.append(nbf.v4.new_code_cell('''b3=json.loads((notebook_dir/'state/pgm_b3.json').read_text())
rebuilt=reconstruct_partial_sums(b3)
ctx,pm,lyap,params=rebuilt['ctx'],rebuilt['pm'],rebuilt['lyap'],rebuilt['params']
N=N_int=b3['N_verify']
ranks=rebuilt['rank_profile']
assert ranks==b3['rank_profile']
rank_evidence=json.loads((notebook_dir/b3['rank_search']['evidence_path']).read_text())
assert rank_evidence['summary']==b3['rank_search']
for k,Vk in enumerate(lyap):
    value=pm.eval_scalar(Vk)
    for actual,saved in [(value.inner_prod_coords,b3['lyap_inner_prod_coords'][k]),(value.func_coords,b3['lyap_func_coords'][k]),(value.offset,b3['lyap_offsets'][k])]:
        assert np.allclose(np.asarray(actual,dtype=float),np.asarray(saved,dtype=float),atol=1e-4,rtol=1e-5)
print('Selected partial sums rechecked with all scalar components.')
'''))
blocks=(root/'supplementary/b4_notebook_cells.py').read_text(encoding='utf-8-sig').split('# %% ')[1:]
for block_index,chunk in enumerate(blocks):
    heading,cell_source=chunk.split('\n',1)
    if block_index==0:
        title='### Candidate-vector scan'
        explanation='Tagged iterates, point-to-solution gaps, smooth-gradient differences, proximal subgradients, composite residuals, and pairwise differences are scanned. Duplicate and zero coordinates are removed.'
    elif block_index==2:
        title='### Selected basis pattern'
        explanation='The visible search chooses sparse independent spanning subsets using the fixed tolerances.'
    elif block_index==4:
        title='### Coefficient matrices'
        explanation='The displayed symmetric matrices use the adopted ordered basis; cross terms are counted twice. Function gaps and offsets are checked separately.'
    else:
        title='### '+heading
        explanation=''
    if block_index==3:
        explanation=r'''The first sparse search uses $\nabla f(x_\star)$, while later searches use $\nabla f(x_k)$. We adopt the uniform equivalent interior basis
$$[x_0-x_\star,\ x_k-x_\star,\ \nabla f(x_k)-\nabla f(x_\star),\ \nabla f(x_k)].$$
The following independent reconstruction checks justify this choice. At $k=0$ the basis is empty; at $k=N$ it is $[x_0-x_\star]$.'''
    nb.cells.extend([nbf.v4.new_markdown_cell(title+'\n'+explanation),nbf.v4.new_code_cell(cell_source)])
nb.cells.append(nbf.v4.new_markdown_cell(r'''### Block 4 conclusion
For $1\leq k<N$, let $v_k$ be the ordered four-vector basis above. The numerical structure is
$$V_k=\sum_{i,j=0}^3c_{ij}(k,N,L)\langle v_{k,i},v_{k,j}\rangle+\alpha(k,N,L)(f(x_k)-f_\star)+\beta(k,N,L)(g(x_k)-g_\star).$$
Here $c_{ij}=c_{ji}$; the ten independent coefficients and $\alpha,\beta$ remain named analytic unknowns. There is no constant term. The initial potential is $V_0=0$. The terminal structure has the single quadratic coefficient $c_{\mathrm{terminal}}(N,L)$ and gap coefficients $\alpha_{\mathrm{terminal}},\beta_{\mathrm{terminal}}$.
All numerical components reconstruct at every index, including endpoints. The endpoint data suggest $c_{\mathrm{terminal}}=-L/(4N)$ and both gap coefficients equal to one. These observations and the numerical coefficient matrices are evidence for Block 5, which must derive formulas and prove the exact step, base and boundary identities. No analytic proof is claimed here.
'''))
nb.cells.append(nbf.v4.new_markdown_cell('## Symbolic step, base, and boundary identities\nPending Block 5.'))
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
NotebookClient(nb,timeout=180,kernel_name='pgm-private',resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb,root/'pgm_example_lyap.ipynb')
print('B4 state and executed notebook saved.')
