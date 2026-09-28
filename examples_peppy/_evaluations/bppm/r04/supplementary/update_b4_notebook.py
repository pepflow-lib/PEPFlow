import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import nbformat as nbf
from nbclient import NotebookClient
root=runtime.ATTEMPT
path=root/'bppm_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
md=nbf.v4.new_markdown_cell
code=nbf.v4.new_code_cell
def source(name):
    return (root/'supplementary'/name).read_text(encoding='utf-8-sig')
new=[md('## Identify the vectors composing the Lyapunov function\nStart from the revalidated selected $N=4$ partial sums above. The fixed rank-comparison interior is $1\\le k\\le N-1$; $k=0,N$ are explicit boundary cases and are reconstructed below.'),
md('### Candidate-vector scan\nCandidates include tagged iterates, solution gaps, both gradient families, coordinate basis vectors, and pairwise iterate differences. Duplicate evaluated coordinates and zero vectors are removed.'),code(source('b4_candidates.py')),code(source('b4_filter.py')),
md('### Selected basis pattern\nThe actual sparsity search is performed for every nonzero index, including the terminal one.'),code(source('b4_search.py')),
md(r'''The search suggests the ordered template
$$b_k=(x_0-x_\star,\nabla h(x_0),x_k-x_\star,\nabla h(x_k)),\qquad 1\le k\le N.$$
At $k=0$ use the empty quadratic basis, because $V_0=0$. No exceptional terminal template is needed. The same order is used in every coefficient matrix below.'''),code(source('b4_basis.py')),
md('### Coefficient matrices\nOff-diagonal entries count twice in $\\sum_{i,j}C_{ij}\\langle b_i,b_j\\rangle$. Retain function values and constants separately.'),code(source('b4_coefficients.py')),code(source('b4_structure.py')),code(source('b4_fit.py')),
md(r'''### Block 4 conclusion
The numerical expression is reconstructed at every $k=0,\ldots,N$. The coefficient candidates are $C_{01}=C_{10}=-1/(2\alpha N)$ and $C_{23}=C_{32}=1/(2\alpha N)$, with other entries zero. The function-value candidates are $(h(x_0)-h(x_k))/(\alpha N)+(k/N)(f(x_k)-f(x_\star))$ and the scalar offset is zero.
Equivalently, the candidate is
$$V_k=\frac{D_h(x_\star,x_k)-D_h(x_\star,x_0)}{\alpha N}+\frac{k}{N}(f(x_k)-f(x_\star)),\qquad 0\le k\le N.$$
This includes $V_0=0$ and the terminal case. The checks above establish numerical reconstruction only. Block 5 must establish the coefficient identities, decrease direction, and base/terminal proof for arbitrary horizons and parameters.''')]
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Special vectors'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Closed form'))
nb.cells[start:end]=new
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
nbf.write(nb,path)
NotebookClient(nb,timeout=120,kernel_name='bppm-attempt',resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb,path)
print('B4 notebook executed and saved')
