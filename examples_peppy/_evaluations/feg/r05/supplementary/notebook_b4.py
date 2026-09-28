import importlib.util
import os
from pathlib import Path
spec=importlib.util.spec_from_file_location('runtime',Path(__file__).parent/'helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat as nbf
from nbclient import NotebookClient
root=runtime.ROOT
path=root/'feg_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
source=(root/'supplementary/helpers/b4_math.py').read_text(encoding='utf-8-sig')
markers=['REPLAY','CANDIDATES','FILTER','SEARCH','BASIS','COEFFICIENTS','STRUCTURE']
parts={}
for i,label in enumerate(markers):
    start=source.index('# '+label)+len('# '+label)
    end=source.index('# '+markers[i+1]) if i+1<len(markers) else len(source)
    parts[label]=source[start:end].strip()
start=next(i for i,c in enumerate(nb.cells) if c.source.startswith('## Identify the vectors'))
end=next(i for i,c in enumerate(nb.cells) if c.source.startswith('## Closed-form Lyapunov'))
nb.cells[start:end]=[
nbf.v4.new_markdown_cell('## Identify the vectors composing the Lyapunov function\nReconstruct the selected B3 certificate and its rank profile before scanning vectors. The cross-horizon rank evidence uses exclusions (1,1), but every index is reconstructed here.'),
nbf.v4.new_code_cell(parts['REPLAY'].replace('import sympy as sp'+'\n','')),
nbf.v4.new_markdown_cell('### Candidate-vector scan\nScan operator values, tagged full and half iterates, basis vectors, anchor gaps, and their pairwise differences. Prefer the meaningful names g_k and q_k, and remove duplicate or zero coordinates.'),
nbf.v4.new_code_cell(parts['CANDIDATES']),nbf.v4.new_code_cell(parts['FILTER']),
nbf.v4.new_markdown_cell('### Selected basis pattern\nThe sparsity search below also finds diagonal coefficient bases using half-step differences. We adopt the full-iterate residual and anchor gap because the same template applies to the terminal index and directly describes the algorithm.'),
nbf.v4.new_code_cell(parts['SEARCH']),
nbf.v4.new_markdown_cell(r'''Use
$$g_k=A(x_k),\qquad q_k=x_k-x_0,\qquad \mathcal B_k=[g_k,q_k]\quad(1\le k\le N).$$
At $k=0$, $V_0=0$ and the quadratic basis is empty. The adopted basis is independently checked below.'''),
nbf.v4.new_code_cell(parts['BASIS']),
nbf.v4.new_markdown_cell('### Coefficient matrices\nThe basis order is [g_k,q_k] for all noninitial indices. Off-diagonal matrix entries contribute twice. There are no function-value or scalar-offset terms.'),
nbf.v4.new_code_cell(parts['COEFFICIENTS']),nbf.v4.new_code_cell(parts['STRUCTURE']),
nbf.v4.new_markdown_cell(r'''### Block 4 conclusion
The verified numerical structure is
$$V_k=c_{gg}(k,N,L)\|g_k\|^2+2c_{gq}(k,N,L)\langle g_k,q_k\rangle+c_{qq}(k,N,L)\|q_k\|^2,$$
for $1\le k\le N$, with $V_0=0$. All three exact coefficient functions remain unknown at this handoff; numerical coefficient matrices and full-coordinate checks cover every index. Block 5 derives their exact expressions and proves the step, base, and terminal identities. Numerical reconstruction is not an analytic convergence proof.''')]
nbf.write(nb,path)
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
NotebookClient(nb,timeout=120,kernel_name='feg-private',resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb,path)
print('B4 notebook execution passed.')

