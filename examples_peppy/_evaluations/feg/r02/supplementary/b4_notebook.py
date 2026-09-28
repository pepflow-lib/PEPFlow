import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import nbformat as nbf
root=Path(__file__).resolve().parents[1]
p=root/'feg_example_lyap.ipynb'
nb=nbf.read(p,as_version=4)
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Identify the vectors'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Closed-form Lyapunov'))
code=lambda name:nbf.v4.new_code_cell((root/f'supplementary/b4_{name}.py').read_text(encoding='utf-8-sig'))
nb.cells[start:end]=[nbf.v4.new_markdown_cell('## Identify the vectors composing the Lyapunov function\nWe use the preceding certificate replay and partial sums from the same saved certificate. Rank confirmation excludes the first and last indices, but reconstruction below includes every index.'),code('sanity'),nbf.v4.new_markdown_cell('### Candidate-vector scan\nCandidates include all setup basis vectors, integer and intermediate iterates, operator values, and pairwise differences. Meaningful anchor gaps are listed first. Zero and duplicate coordinate vectors are removed before filtering.'),code('candidates'),code('filter'),nbf.v4.new_markdown_cell('### Selected basis pattern\nThe actual sparse-basis search is shown below. We then use a common basis across all nonzero indices: the residual and the displacement from the initial point. This basis is slightly less sparse than some search choices, but has one consistent recurrence interpretation and also applies at the terminal index.'),code('search'),nbf.v4.new_markdown_cell(r'''The adopted ordered template is
$$\mathcal B_k=[A(x_k),x_k-x_0],\qquad 1\le k\le N.$$
At $k=0$, $V_0=0$ uses the empty basis. Independence and reconstruction are checked at each index, including $k=N$.'''),code('basis'),nbf.v4.new_markdown_cell('### Coefficient matrices\nThe order is residual first, anchor displacement second. Symmetric off-diagonal entries contribute twice. Function-value and constant terms are absent, as checked below. The printed matrices are numerical data at $N=6$, not exact all-horizon formulas.'),nbf.v4.new_code_cell((root/'supplementary/b4_coefficients.py').read_text(encoding='utf-8-sig').replace("    print('C=',C.tolist())\n",'')),code('structure'),nbf.v4.new_markdown_cell(r'''### Block 4 conclusion
The full interior structure is
$$V_k=c_{00}(k,N,L)\|A(x_k)\|^2+2c_{01}(k,N,L)\langle A(x_k),x_k-x_0\rangle+c_{11}(k,N,L)\|x_k-x_0\|^2.$$
There are no function-value or constant terms. The initial value is $V_0=0$. At $k=N$ the same basis uses unknown coefficients $d_{00},d_{01},d_{11}$ until their relationship to the interior coefficients is established.

All numerical reconstructions pass, including both endpoints. Exact coefficient formulas are unresolved. Block 5 must derive them and prove the step, base, and terminal identities with the required signs and normalization.''')]
nbf.write(nb,p)
