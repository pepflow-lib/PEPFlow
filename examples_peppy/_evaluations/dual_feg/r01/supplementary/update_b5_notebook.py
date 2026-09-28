import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import re
import nbformat
root=runtime.ATTEMPT
path=root/'dual_feg_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
md=nbformat.v4.new_markdown_cell
codecell=nbformat.v4.new_code_cell
theorem=r'''### Theorem
For every integer $N\ge1$, $L>0$ and $R\ge0$, the stated Dual FEG iteration for a monotone $L$-Lipschitz operator with $A(x_\star)=0$, $\|x_0-x_\star\|^2\le R^2$ and $z_0=0$ satisfies
$$\boxed{\|A(x_N)\|^2\le\frac{4L^2R^2}{N^2}.}$$
Set $G=A(x_N)$, $a=x_0-x_N$, and $b_k=x_k-x_N$. A certificate is $V_0=0$ and, for $1\le k\le N-1$,
$$V_k=-\frac{4L}{N}\langle a,G\rangle-2\|z_k\|^2+\frac{4L}{N-k}\langle z_k,b_k\rangle-4\langle z_k,G\rangle+\frac{4L}{N-k}\langle b_k,G\rangle.$$
At the terminal index use the separate expression
$$V_N=2\|G\|^2-\frac{4L}{N}\langle a,G\rangle.$$
The sequence is nonincreasing. The interior expression also gives $V_0=0$ when evaluated at $k=0$, $z_0=0$; it is never evaluated at $k=N$.
'''
proof=r'''### Proof outline
Let $y_k=x_{k+1/2}$ and define the nonpositive residuals
$$\operatorname{Lip}(u,v)=\|A(u)-A(v)\|^2-L^2\|u-v\|^2,\qquad
\operatorname{Mon}(u,v)=-\langle A(u)-A(v),u-v\rangle.$$
With $G=A(x_N)$ and $a=x_0-x_N$, write the interior potential as
$$V_k=-\frac{4L}{N}\langle a,G\rangle-2\|z_k\|^2-4\langle z_k,G\rangle
+\frac{4L}{N-k}\langle z_k+G,x_k-x_N\rangle.$$
Its initial value is zero. Substitution of the algorithm gives, for $0\le k\le N-2$,
$$V_{k+1}-V_k=\frac{2}{(N-k)^2}\operatorname{Lip}(x_k,y_k)
+\frac{4L}{(N-k)(N-k-1)}\operatorname{Mon}(x_N,y_k)\le0.$$
The actual final update is $x_N=x_{N-1}-(z_{N-1}+A(x_{N-1}))/L$. With the separate terminal potential $V_N=2\|G\|^2-(4L/N)\langle a,G\rangle$, it gives
$$V_N-V_{N-1}=2\operatorname{Lip}(x_{N-1},x_N)\le0.$$
For $N=1$ there are no ordinary steps; the same last-step identity with $z_0=0$ starts directly from $V_0=0$. All multipliers are positive on their stated domains, so $V_N\le0$ for every $N\ge1$.

Finally, set $d=x_0-x_\star$. The exact normalized identity is
$$\|G\|^2-\frac{4L^2R^2}{N^2}
=V_N+\frac{4L}{N}\operatorname{Mon}(x_N,x_\star)
-\left\|\frac{2L}{N}d-G\right\|^2
+\frac{4L^2}{N^2}\bigl(\|d\|^2-R^2\bigr).$$
Every term on the right is nonpositive: use $V_N\le0$, monotonicity and $A(x_\star)=0$, the square's nonnegativity, and the given initial-distance bound. This proves the theorem, including $R=0$. The notebook below derives the coefficients and checks every identity exactly in Gram, function-value and constant coordinates.
'''
nb.cells[1:2]=[md('## Proof Statement'),md(theorem),md(proof)]
# Replace the unreached symbolic placeholder with the complete exact derivation.
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Symbolic step, base'))
def source(name):
    return (root/'supplementary'/name).read_text(encoding='utf-8-sig')
derivation_md=r'''## Exact coefficient derivation
The B4 support suggests the ansatz, with $t=N-k$,
$$W_t=\frac{e}{N}\langle a,G\rangle+a_1\|z\|^2+\frac{b}{t}\langle z,x-x_N\rangle+c\langle z,G\rangle+\frac{d}{t}\langle x-x_N,G\rangle.$$
Here the code names $a_1$ as `a`; the anchor vector remains $x_0-x_N$. Solve all scalar-coordinate equations for
$$W_{t-1}(z^+,x^+)-W_t(z,x)=\nu\operatorname{Lip}(x,y)+\mu\operatorname{Mon}(x_N,y).$$
This yields $a_1=-d/(2L)$, $b=d$, $c=-d/L$, $\nu=d/(2Lt^2)$ and $\mu=d/(t(t-1))$. The initial condition gives $e=-d$. Choosing $d=4L$ fixes the useful terminal normalization. This is an exact solved family, not an inference from fitted decimal coefficients; the selected formulas are independently verified below.
'''
closed_md=r'''### Closed-form Lyapunov function
For $1\le k\le N-1$ the resulting expression is
$$V_k=-\frac{4L}{N}\langle x_0-x_N,G\rangle-2\|z_k\|^2-4\langle z_k,G\rangle+\frac{4L}{N-k}\langle z_k+G,x_k-x_N\rangle.$$
Together with $V_0=0$ and $V_N=2\|G\|^2-(4L/N)\langle x_0-x_N,G\rangle$, this resolves every B4 coefficient; function and constant terms remain absent. The following checks verify its exact identities for symbolic indices and parameters.
'''
nb.cells[start:]=[md(derivation_md),codecell(source('b5_derive.py')),md('### Closed-form coefficient matrices\nThe exact coefficients below are compared to the saved numerical discovery matrices at N=6. Their universal justification is the symbolic derivation and identities, not this finite-sample comparison.'),codecell(source('b5_coeff_formula.py')),md(closed_md),md('## Symbolic Step Recursion Verification'),md(r'''For $t=N-k\ge2$, verify
$$V_{k+1}-V_k=\frac{2}{t^2}\operatorname{Lip}(x_k,y_k)+\frac{4L}{t(t-1)}\operatorname{Mon}(x_N,y_k).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in every scalar component.'''),codecell(source('b5_step.py')),md('## Base Case and Boundary Symbolic Verification'),md(r'''For $N\ge1$, $V_0=0$. For $N\ge2$, verify the separate first-step identity
$$V_1=\frac{2}{N^2}\operatorname{Lip}(x_0,y_0)+\frac{4L}{N(N-1)}\operatorname{Mon}(x_N,y_0).$$
Both residuals $\mathrm{LHS}-\mathrm{RHS}$ must be zero. The initial-radius normalization is retained for the final boundary identity.'''),codecell(source('b5_base.py')),md('### Final-step and N=1 identities'),md(r'''Using the actual final update, verify
$$V_N-V_{N-1}=2\operatorname{Lip}(x_{N-1},x_N).$$
For $N=1$, directly verify $V_1=2\operatorname{Lip}(x_0,x_1)$ with $x_1=x_0-A(x_0)/L$. Each residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero.'''),codecell(source('b5_last.py')),md('### Boundary Identity Symbolic Verification'),md(r'''With $d=x_0-x_\star$, verify
$$\|G\|^2-\frac{4L^2R^2}{N^2}=V_N+\frac{4L}{N}\operatorname{Mon}(x_N,x_\star)-\left\|\frac{2L}{N}d-G\right\|^2+\frac{4L^2}{N^2}(\|d\|^2-R^2).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. Since each term on the right is nonpositive, this identity proves the stated rate.'''),codecell(source('b5_boundary.py')),md('### Final proof status\nThe numerical certificate and the arbitrary-horizon Lyapunov proof are verified. The earlier global full-PEP multiplier/S formulas remain recorded as candidates; a separate analytic global-certificate proof is not claimed. All assumptions, signs, endpoints and parameter normalization used by the local Lyapunov proof are accounted for. Rendering was omitted under the evaluation presentation policy; required source checks and clean-kernel execution are retained.')]
# Remove obsolete future-tense statements while preserving the discovery trail.
for cell in nb.cells:
    if cell.cell_type=='markdown':
        cell.source=cell.source.replace('All-horizon formulas and exact endpoint sign reasoning remain for B5.','The final exact formulas and endpoint arguments are established in B5 below.').replace('B5 must derive the coefficients and verify exact step, initial, and terminal identities before any theorem is claimed.','These were the unresolved obligations at the B4 handoff; the exact derivation and verification follow below.')
        def normalize_math(match):
            s=match.group(0).replace('_\\star','_{\\star}')
            return re.sub(r'_([A-Za-z0-9])(?![A-Za-z0-9])',r'_{\1}',s)
        cell.source=re.sub(r'\$\$.*?\$\$|\$[^$]*?\$',normalize_math,cell.source,flags=re.S)
nbformat.write(nb,path)
(root/'supplementary/b5-theorem.md').write_text(theorem+'\n'+proof,encoding='utf-8')
print('Final notebook source assembled; static checks precede final execution.')
