import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import os
import sys
import nbformat as nbf
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
path = root/'feg_example_lyap.ipynb'
nb = nbf.read(path,as_version=4)
start = next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Dense and relaxed proof solves'))
end = next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Lyapunov partial sums'))
nb.cells[start:end] = [nbf.v4.new_markdown_cell('## Dense and relaxed proof solves\nThe direct primal solve uses CLARABEL defaults at $N=6$. A second fresh solve drops all interpolation multipliers below $10^{-6}$ in the dense result. The complete selected certificate comes from that single solve; all small terms still present in its matrix are retained.'),nbf.v4.new_code_cell('dense_summary = json.loads((notebook_dir / "state/feg_dense.json").read_text())\nprint("Dense optimum:",dense_summary["opt_value"])\nfor group in dense_summary["lambda_groups"]:\n    active = [(name,value) for name,value in dense_summary["named_dual_values"].items() if dense_summary["constraint_metadata"][name]["group"]==group and value is not None and abs(value)>1e-6]\n    print(group, active)\nrelaxation = [name for name,value in dense_summary["named_dual_values"].items() if name!="initial_condition" and value is not None and abs(value)<1e-6]\nprint("Dropped constraints:",len(relaxation))'),nbf.v4.new_markdown_cell(r'''## Lambda and S verification
All inequalities are normalized as $r_i\le0$. The fixed-sample numerical identity is
$$\|A(x_N)\|^2-\mathrm{bound}-\sum_i\lambda_i r_i+S=0.$$
Nonnegative multipliers and $S\succeq0$ establish the direction of the numerical bound. The following code reconstructs the full saved constraint inventory and checks every scalar component. The reverse LDL decomposition retains its full matrix, including small pivots.'''),nbf.v4.new_code_cell((root/'supplementary/b2_check_cell.py').read_text(encoding='utf-8-sig').replace('import sympy as sp\n', '')),nbf.v4.new_markdown_cell('### Initial formula search\nThe sparse pattern suggests monotonicity coefficients $4k(k+1)/N^2$, a final root coefficient $4/N$, and Lipschitz coefficients $2(k+1)^2/N^2$. The rank-one matrix suggests $(2(x_0-x_\\star)/N-A(x_N))^2$ at $L=R=1$. These guesses are compared against this same certificate below, with tolerance $10^{-4}$. Target-specific references were excluded by the clean-room rules.'),nbf.v4.new_code_cell((root/'supplementary/b2_search_cell.py').read_text(encoding='utf-8-sig')),nbf.v4.new_markdown_cell('### Block 2 conclusion\nThe full numerical certificate and reverse LDL reconstruction pass. The simple guesses exceed the required numerical comparison tolerance for the selected certificate, so global lambda and S formulas remain unresolved. Numerical partial-sum exploration may proceed with the verified saved certificate. Neither an analytic full-PEP proof nor a Lyapunov proof is claimed.')]
nbf.write(nb,path)
jupyter=root/'supplementary/.runtime/jupyter'
os.environ['JUPYTER_PATH']=str(jupyter)
NotebookClient(nb,timeout=120,kernel_name='feg-owned',resources={'metadata':{'path':str(root)}}).execute()
nbf.write(nb,path)
print('B2 notebook executed',len(nb.cells),'cells')

