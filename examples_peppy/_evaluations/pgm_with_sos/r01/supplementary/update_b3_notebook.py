import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import os
import hashlib
import re
import nbformat as nb
from nbclient import NotebookClient
root=runtime.ATTEMPT
path=root/'pgm_example_lyap.ipynb'
book=nb.read(path,as_version=4)
intro=r'''## Lyapunov partial sums and ranks
For interpolation residuals $I_q\le0$, set $V_0=0$ and
$$V_k=\sum_{q\text{ assigned through }k}\lambda_q I_q-\sum_{i=1}^{k}\sum_{r=1}^{3}c_{r,i}\|u_{r,i}\|^2.$$
The initial optimum-to-$x_0$ smooth residual enters the first increment. Each step adds both functions' optimum-to-current and predecessor-to-current residuals and subtracts a numerically checked PSD block $Q_i$. The original supplied squares remain the analytic candidate. To repair accumulated numerical reconstruction error, the saved $S$ is reallocated into blocks using the observed support $[a_\star,x_0-x_\star,x_k-x_\star,a_k-a_\star]$. The allocation minimizes distance from the original partial-sum coefficient matrices while constraining step blocks toward PSD; all blocks are then independently checked at the frozen PSD tolerance $10^{-6}$. The auxiliary allocation solves report optimal_inaccurate, which is retained; their labels do not replace the checks. Nonnegative multipliers and square coefficients give $V_{k+1}\le V_k$ in the exact target identity. The numerical construction retains every selected multiplier and all Gram, function, and constant coordinates.

The same construction has rank 4 at every retained index for $N=4$ and $N=6$, excluding only $V_0,V_N$. Rank uses absolute tolerance $10^{-4}$ on unscaled Gram coordinates at $L=R=1$. No interpolation term or part of the saved slack is left out. The terminal rank is 1; the radius constraint is reserved for the boundary argument. These observations do not establish an arbitrary-horizon theorem.'''
code='''certificate = json.loads((notebook_dir/"state/pgm_b3.json").read_text())
basis = ctx_b2.basis_vectors()
S_scalar = sum((float(S_saved[i,j])*basis[i]*basis[j]
                for i,j in np.ndindex(S_saved.shape)),pf.Scalar.zero())
saved_identity = pm.eval_scalar(pb_b2.performance_metric-b2["opt_value"]-weighted+S_scalar)
assert all(maxabs(v)<=1e-5 for v in (saved_identity.inner_prod_coords,saved_identity.func_coords,saved_identity.offset))
'''+(root/'supplementary/b3_decomposition.py').read_text()+'\n'+(root/'supplementary/b3_grouping.py').read_text()+'''
rank_evidence=json.loads((notebook_dir/"supplementary/rank_search.json").read_text())
for sample in rank_evidence["samples"]:
    retained_sample=sample["rank_profile"][1:sample["N"]]
    assert len(retained_sample)>=3 and set(retained_sample)=={4}
    print("Confirming horizon",sample["N"],"retained indices",list(range(1,sample["N"])),
          "common rank",4,"coverage residual",sample["coverage_residual"])
assert rank_evidence["summary"]["selected_certificate_id"]==b2["certificate_id"]
assert ranks==json.loads((notebook_dir/"state/pgm_b3.json").read_text())["rank_profile"]
'''
book.cells=book.cells[:13]+[nb.v4.new_markdown_cell(intro),nb.v4.new_code_cell(code)]+[nb.v4.new_markdown_cell("## Identify the vectors composing the Lyapunov function\nPending B4 retry after slack allocation recovery."),book.cells[-1]]
nb.write(book,path)
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
NotebookClient(book,timeout=180,kernel_name='pgm-attempt',resources={'metadata':{'path':str(root)}}).execute()
nb.write(book,path)
for c in book.cells:
    if c.cell_type=='markdown': assert not any(s in c.source for s in ('\\(', '\\)', '\\[', '\\]', '\x0c', '\r'))
p=root/'supplementary/pgm_example_lyap_checklist.md'
s=p.read_text()
s=re.sub(r'Last reviewed block:.*','Last reviewed block: B3',s)
s=re.sub(r'SHA-256: [a-f0-9]+','SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest(),s)
s=s.replace('| pending | 13 | N4 evidence preserved; selected N6 partial sums and confirmation due in B3. |','| verified | 13,14 | Reconstructed certificate, direct squares, explicit grouping and full coverage; rank 4 confirmed at N4/N6, exclusions (1,1), absolute tolerance 1e-4. |')
s=s.replace('| pending | 14 | Due B4. |','| pending | 15 | Due B4. |').replace('| pending | 15 | Due B4/B5. |','| pending | 16 | Due B4/B5. |').replace('| pending | 15 | Due B5. |','| pending | 16 | Due B5. |')
p.write_text(s)
print('B3 notebook executed; cross-horizon comparison and all coverage checks passed.')

