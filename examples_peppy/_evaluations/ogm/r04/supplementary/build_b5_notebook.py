import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from runtime import configure
attempt,approved=configure()
import nbformat as nbf
path=attempt/'ogm_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
nb.cells=nb.cells[:43]
md,code=nbf.v4.new_markdown_cell,nbf.v4.new_code_cell
nb.cells[1:2]=[md('## Proof Statement'),md((attempt/'supplementary/b5_theorem.md').read_text(encoding='utf-8-sig')),md((attempt/'supplementary/b5_proof_outline.md').read_text(encoding='utf-8-sig'))]
# Preserve the discovery trail while making its historical status explicit.
for c in nb.cells:
    if c.cell_type=='markdown':
        c.source=c.source.replace('Block 5 must establish','The exact verification below establishes').replace('Block 5 derives','The exact verification below derives')
nb.cells.append(md(r'''## Closed-form Lyapunov function and exact verification
The candidate coefficients extracted above are reused, with no fitting substituted for proof. The formula for $V_{k}$ is the one in the theorem; use $W_{k}=H^{2}V_{k}$ to remove a common positive normalization. The symbolic contexts encode only one update at a time, with free iterates and gradients constrained solely by the algorithm. They do not assume finite-horizon numerical certificates.

The recurrence is imposed by polynomial remainder reduction: interior $t^{2}=s^{2}-s$, terminal $2t^{2}=s^{2}-s$, and base $s^{2}-s=1$. These are exact consequences of the positive-root definitions. Denominators are checked nonzero using $L,t,s,H>0$. Floating coefficients are rejected. Each helper call below only extracts, simplifies, displays, and checks the identity visibly constructed in its cell.
'''))
sections=(attempt/'supplementary/b5_symbolic_cells.py').read_text(encoding='utf-8-sig').split('# %%')[1:]
nb.cells.append(code(sections[0]))
headings=[('## Symbolic Step Recursion Verification',r'''For arbitrary $1\leq k\leq N-2$, put $t=\theta_{k}$ and $s=\theta_{k+1}$, so $s^{2}-s=t^{2}$. Verify
$$W_{k+1}-W_{k}=2s I_{\star,k+1}+2t^{2}I_{k,k+1}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero in every scalar component.'''),('## Base Case and Boundary Symbolic Verification',r'''For $N\geq2$, use $z_{0}=x_{0}$, $\theta_{0}=1$, and $s=\theta_{1}$ with $s^{2}-s=1$. Verify
$$W_{1}=2I_{\star,0}+2s I_{\star,1}+2I_{0,1}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero; all multipliers are positive, so $V_{1}\leq V_{0}=0$.'''),('### Special Terminal Step',r'''For $N\geq2$, put $t=\theta_{N-1}$ and $s=\theta_{N}$, with $s^{2}-s=2t^{2}$. Verify
$$W_{N}-W_{N-1}=s I_{\star,N}+2t^{2}I_{N-1,N}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. The terminal potential has no gradient-norm correction and uses $q_{N}=z_{N}-x_{\star}-s g_{N}/L$.'''),('### Exceptional Horizon N=1',r'''Here $\theta_{0}=1$, $\theta_{1}=2$. Verify the complete initialization-to-terminal identity
$$W_{1}=2I_{\star,0}+2I_{\star,1}+2I_{0,1}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero; no interior formula is used outside its domain.'''),('### Boundary Identity Symbolic Verification',r'''For all $N\geq1$, let $H=\theta_{N}$ and $\tau=L/(2H^{2})$. Verify
$$F_{N}-\frac{LR^{2}}{2H^{2}}=V_{N}-\tau\|q_{N}\|^{2}+\tau(\|d_{0}\|^{2}-R^{2}).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero, including the $R^{2}$ constant terms. Since $V_{N}\leq0$, $\tau>0$, and $\|d_{0}\|^{2}\leq R^{2}$, its right side is nonpositive.''')]
for (heading,equation),source in zip(headings,sections[1:6]):
    nb.cells.extend([md(heading),md(equation),code(source)])
nb.cells.append(md(r'''### Signs, domain, and telescoping
The positive-root recurrences give $\theta_{0}=1$ and $\theta_{k}\geq1$, hence $H\geq2$. Therefore $2\theta_{k}^{2}/H^{2}$, $2\theta_{k+1}/H^{2}$, $1/H$, and $L/(2H^{2})$ are positive; the only assumed nonnegative radius $R$ never appears in a denominator. The interpolation residuals are nonpositive by the smooth-convex inequality proved in the outline. All step identities therefore decrease $V$, and the terminal nonnegative square is subtracted in the final upper bound.

Summing the verified initialization and local identities covers each optimizer-row and forward-consecutive multiplier exactly once. This proves the global full-PEP identity stated in the outline for arbitrary $N\geq2$; the separate $N=1$ check supplies the remaining case. The exact local proof and global telescoping upgrade the candidate formulas; earlier discovery statuses remain recorded historically in B1–B4.
'''))
nb.cells.append(code(sections[6]))
# Normalize unbraced single-character subscripts only in Markdown math content.
import re
for c in nb.cells:
    if c.cell_type=='markdown':
        c.source=re.sub(r'(?<=[A-Za-z])_([A-Za-z0-9])',r'_{\1}',c.source)
        assert '\\(' not in c.source and '\\[' not in c.source
        assert not any(ord(ch)<32 and ch not in '\n\t' for ch in c.source)
nbf.write(nb,path)
print('Prepared final notebook cells:',len(nb.cells))
