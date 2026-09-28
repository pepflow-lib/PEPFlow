import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import nbformat as nbf
root=Path(__file__).resolve().parents[1]
p=root/'feg_example_lyap.ipynb'
nb=nbf.read(p,as_version=4)
md=nbf.v4.new_markdown_cell
code=lambda name:nbf.v4.new_code_cell((root/f'supplementary/b5_{name}_cell.py').read_text(encoding='utf-8-sig'))
nb.cells[1:2]=[md('## Proof Statement'),md(r'''### Theorem
Under the assumptions and updates above, for every integer $N\ge1$,
$$\|A(x_{N})\|^{2}\le\frac{4L^{2}R^{2}}{N^{2}}.$$
An exact nonincreasing Lyapunov certificate is $V_{0}=0$ and
$$V_{k}=\frac{2k^{2}}{N^{2}}\|A(x_{k})\|^{2}+\frac{4kL}{N^{2}}\langle A(x_{k}),x_{k}-x_{0}\rangle,\qquad 1\le k\le N.$$
No function-value or constant terms are present. The same formula applies at the terminal index. The bound is valid at $N=1$, although the numerical PEP value there is smaller.'''),md(r'''### Proof outline
Write
$$M(u,v)=-\langle A(u)-A(v),u-v\rangle\le0,\qquad Q(u,v)=\|A(u)-A(v)\|^{2}-L^{2}\|u-v\|^{2}\le0.$$
For $V_{k}=2k^{2}\|A(x_{k})\|^{2}/N^{2}+4kL\langle A(x_{k}),x_{k}-x_{0}\rangle/N^{2}$, the initial update $x_{1}=x_{0}-A(x_{0})/L$ gives
$$V_{1}=\frac{2}{N^{2}}Q(x_{0},x_{1})\le0=V_{0}.$$
For every $1\le k\le N-1$, the two algorithm updates give the exact identity
$$V_{k+1}-V_{k}=\frac{4Lk(k+1)}{N^{2}}M(x_{k},x_{k+1})+\frac{2(k+1)^{2}}{N^{2}}Q(x_{k+1/2},x_{k+1})\le0.$$
Both multipliers are positive on this range, so $V_{N}\le0$. Set
$$S_{N}=\left\|A(x_{N})-\frac{2L}{N}(x_{0}-x_{\star})\right\|^{2}\ge0.$$
Since $A(x_{\star})=0$, the terminal identity is
$$\|A(x_{N})\|^{2}-\frac{4L^{2}R^{2}}{N^{2}}=V_{N}+\frac{4L}{N}M(x_{N},x_{\star})-S_{N}+\frac{4L^{2}}{N^{2}}\bigl(\|x_{0}-x_{\star}\|^{2}-R^{2}\bigr).$$
Every term on the right is nonpositive. This proves the claim. For $N=1$ the interior sum is empty, and the separate base and terminal identities still apply. No division by $R$ is used, so $R=0$ is included.''')]
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Closed-form Lyapunov'))
nb.cells[start:]=[md('## Closed-form Lyapunov function and exact identities'),code('load'),md('### Symbolic recursion context and coefficient derivation\nWe retain all three unknown symmetric coefficients in the basis $[A(x_{k}),x_{k}-x_{0}]$, together with unknown Lipschitz and monotonicity multipliers. The equations below require all Gram, function-value, and constant components to vanish. The resulting family has one scale parameter; choosing it to match the terminal normalization gives the stated nonzero certificate.'),code('derivation'),md(r'''### Derived Lyapunov coefficients
The equations give $a_{k}=k^{2}\nu/(k+1)^{2}$, $b_{k}=Lk\nu/(k+1)^{2}$, $c_{k}=0$, $a_{k+1}=\nu$, $b_{k+1}=L\nu/(k+1)$, $c_{k+1}=0$, and $\mu=2Lk\nu/(k+1)$. Selecting $\nu=2(k+1)^{2}/N^{2}$ produces a consistent sequence across steps:
$$V_{k}=\frac{2k^{2}}{N^{2}}\|A(x_{k})\|^{2}+\frac{4kL}{N^{2}}\langle A(x_{k}),x_{k}-x_{0}\rangle.$$
The initial value is $V_{0}=0$; the same nonzero-index formula also supplies the terminal coefficients. The next sections verify the original step identity, the separate base case, and the target normalization exactly.'''),md('## Symbolic Step Recursion Verification'),md(r'''For $k\ge1$ and $N\ge k+1$, verify
$$V_{k+1}-V_{k}=\frac{4Lk(k+1)}{N^{2}}M(x_{k},x_{k+1})+\frac{2(k+1)^{2}}{N^{2}}Q(x_{k+1/2},x_{k+1}).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero in every component. There are no additional square or scalar terms in this step.'''),code('step'),code('coefficients'),md('## Base Case and Boundary Symbolic Verification'),md(r'''The base context explicitly uses $x_{1/2}=x_{0}$ and $x_{1}=x_{0}-A(x_{0})/L$. Verify
$$V_{1}-V_{0}=V_{1}=\frac{2}{N^{2}}Q(x_{0},x_{1}),\qquad V_{0}=0.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. Lipschitz continuity gives $V_{1}\le0$.'''),code('base'),md('### Boundary Identity Symbolic Verification'),md(r'''For every $N\ge1$, verify
$$\|A(x_{N})\|^{2}-\frac{4L^{2}R^{2}}{N^{2}}=V_{N}+\frac{4L}{N}M(x_{N},x_{\star})-\left\|A(x_{N})-\frac{2L}{N}(x_{0}-x_{\star})\right\|^{2}+\frac{4L^{2}}{N^{2}}\bigl(\|x_{0}-x_{\star}\|^{2}-R^{2}\bigr).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero, including its constant component.'''),code('boundary'),md(r'''### Sign, domain, and normalization conclusion
For integer $k\ge1$, integer $N\ge1$, and $L>0$, all step, base, and terminal residual multipliers are nonnegative, and all denominators are nonzero. Monotonicity and Lipschitz continuity supply the residual signs; the terminal norm square is subtracted. The initial-distance residual is nonpositive by assumption. Therefore the base identity, step decrease, and terminal identity prove
$$\|A(x_{N})\|^{2}\le4L^{2}R^{2}/N^{2}.$$
The proof handles $N=1$ separately through the base identity, and it also applies when $R=0$. The universal Lyapunov proof is established. The earlier global numerical certificate remains verified at its sampled horizon; a separate analytic global lambda/S-table verification is not claimed.''')]
nbf.write(nb,p)
print('Final proof cells written:',len(nb.cells))
