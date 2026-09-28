import sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'supplementary/helpers'))
import runtime
import os
import nbformat
from nbclient import NotebookClient
path=root/'ogm_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
c,m=nbformat.v4.new_code_cell,nbformat.v4.new_markdown_cell
intro=r'''## Partial-sum Lyapunov construction and rank profile
Normalize each interpolation inequality as $R_{i,j}\leq0$. Set $V_0=0$ and form $V_k$ from the weighted star inequalities through index $k$ and consecutive inequalities through $(k-1,k)$. Thus the first increment includes the initial star term, and subsequent increments obey
$$V_{k+1}-V_k=\lambda_{\star,k+1}R_{\star,k+1}+\lambda_{k,k+1}R_{k,k+1}\leq0.$$
The single nonnegative remainder square is reserved for the terminal boundary. All active interpolation terms are assigned; no terms are omitted. The $N=4$ trial has interior rank three with endpoint exclusions $(1,1)$ at absolute tolerance $10^{-4}$ in unscaled Gram coordinates. A second horizon is still required; B3 is incomplete.'''
check=(root/'supplementary/b3_certificate_check.py').read_text(encoding='utf-8-sig')
check='\n'.join(line for line in check.splitlines() if not line.startswith('from certificate_checks import'))
nb.cells=nb.cells[:16]+[m(intro),c('certificate = b2'),c(check),c((root/'supplementary/b3_decomposition.py').read_text(encoding='utf-8-sig')),c((root/'supplementary/b3_grouping.py').read_text(encoding='utf-8-sig')),m('Cross-horizon confirmation pending acquisition of a coherent N=6 certificate in B2.'),m('## Identify the vectors composing the Lyapunov function\nPending B4.'),m('## Coefficients and symbolic identities\nPending B5.')]
nbformat.write(nb,path)
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
NotebookClient(nb,timeout=120,kernel_name='ogm-attempt',resources={'metadata':{'path':str(root)}}).execute()
nbformat.write(nb,path)
print('B3 N=4 trial notebook executed.')
