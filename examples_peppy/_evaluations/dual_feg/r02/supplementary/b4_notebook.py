import importlib.util
import json
import hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',root/'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat as nbf
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client import KernelManager
path=root/'dual_feg_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
def code(name):
    return (root/'supplementary'/name).read_text(encoding='utf-8-sig')
scan=code('b4_scan.py')
prefix,filtered=scan.split('spanning_by_k={}',1)
cells=[nbf.v4.new_markdown_cell('## Identify the vectors composing the Lyapunov function\nThe checked Block 3 partial sums supply the numerical matrices. The retained interior is $1\le k\le N-1$; both endpoints are checked separately. Rank 4 was confirmed at horizons 4 and 6.'),
nbf.v4.new_markdown_cell('### Candidate-vector scan\nCandidates include operator outputs, auxiliary vectors, initial and terminal displacement vectors, and point-to-solution gaps. Exact duplicate coordinates and zero vectors are removed.'),
nbf.v4.new_code_cell(prefix),nbf.v4.new_code_cell('spanning_by_k={}'+filtered),
nbf.v4.new_markdown_cell('### Selected basis pattern\nThe sparse search is executed for every nonzero partial sum, including the terminal index.'),nbf.v4.new_code_cell(code('b4_search.py')),
nbf.v4.new_markdown_cell(r'''For a consistent recurrence-based template, adopt
$$b_k=(g_N,z_k,x_k-x_0,x_N-x_0),\qquad1\le k<N,$$
where $g_N=A(x_N)$. The sparse search sometimes chooses equivalent endpoint-specific combinations; this template keeps the auxiliary recurrence visible. Independence and reconstruction are checked below. Use an empty basis at $k=0$ and $(g_N,x_N-x_0)$ at $k=N$.'''),
nbf.v4.new_code_cell(code('b4_basis.py')),
nbf.v4.new_markdown_cell(r'''### Coefficient matrices
The order is $(g_N,z_k,x_k-x_0,x_N-x_0)$ in the interior and $(g_N,x_N-x_0)$ at the terminal index. Off-diagonal entries count twice in $\sum_{i,j}C_{ij}\langle b_i,b_j\rangle$. Function-value and offset terms are absent, as checked at every index.'''),
nbf.v4.new_code_cell(code('b4_coefficients.py')),
nbf.v4.new_code_cell(code('b4_formula.py')),
nbf.v4.new_code_cell(code('b4_structure.py')),
nbf.v4.new_markdown_cell(r'''### Block 4 conclusion
For $L=1$ and $t=N-k$, the numerical matrices suggest
$$C_k=\begin{pmatrix}0&-2&2/t&-2k/(Nt)\\-2&-2&2/t&-2/t\\2/t&2/t&0&0\\-2k/(Nt)&-2/t&0&0\end{pmatrix},\quad 1\le k<N,$$
with $V_0=0$ and terminal coefficient matrix
$$C_N=\begin{pmatrix}2&2/N\\2/N&0\end{pmatrix}.$$
All selected numerical partial sums, including the endpoints, reconstruct within the frozen tolerances. These formulas are candidates at the sampled normalization. Block 5 must derive their parameter scaling and verify the exact step, base, and terminal proof for every horizon.''')]
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Identify the vectors'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Symbolic step'))
nb.cells[start:end]=cells
nbf.write(nb,path)
km=KernelManager(kernel_name='attempt-python',kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(root/'supplementary/.runtime/kernels')]))
NotebookClient(nb,timeout=120,km=km,resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb,path)
for c in nb.cells:
    if c.cell_type=='markdown':
        assert '\\(' not in c.source and '\\[' not in c.source
        assert not any(ord(x)<32 and x not in '\n\t' for x in c.source)
record={'status':'passed','fresh_kernel':True,'source_math_checks':'passed','rendered_review':'omitted by evaluation-ancillary-v1','notebook_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(root/'supplementary/b4-notebook-execution.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
check=root/'supplementary/dual_feg_example_lyap_checklist.md'
lines=check.read_text(encoding='utf-8-sig').splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'):lines[i]='Last reviewed block: B4'
    if line.startswith('SHA-256:'):lines[i]='SHA-256: '+record['notebook_sha256']
    if line.startswith('| 10.'):lines[i]='| 10. special-vector identification | verified | 19–26 | Actual candidate filtering and sparse search; adopted interpretable pattern; independence and full reconstruction passed. |'
    if line.startswith('| 11.'):lines[i]='| 11. coefficient extraction and closed-form V_k | pending | 27–31 | Numerical coefficient/component reconstructions and candidate formula comparisons passed; analytic formula awaits B5. |'
    if line.startswith('| 12.'):lines[i]='| 12. symbolic step, base, and boundary identities | pending | 32 | B5 obligation. |'
check.write_text('\n'.join(lines),encoding='utf-8')
print('B4 notebook executed and source-checked.')
