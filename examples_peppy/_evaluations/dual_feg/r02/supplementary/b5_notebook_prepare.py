import importlib.util
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',root/'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat as nbf
path=root/'dual_feg_example_lyap.ipynb'
nb=nbf.read(path,as_version=4)
formula=r'''Set $X=x_{N}$, $G=A(X)$ and $t=N-k$. A nonincreasing certificate is $V_{0}=0$, and, for $1\le k<N$,
$$V_{k}=-4\langle G,z_{k}\rangle-2\|z_{k}\|^{2}+\frac{4L}{N-k}\langle G+z_{k},x_{k}-X\rangle+\frac{4L}{N}\langle G,X-x_{0}\rangle.$$
The terminal value is
$$V_{N}=2\|G\|^{2}+\frac{4L}{N}\langle G,X-x_{0}\rangle.$$
The same interior expression evaluated at $k=0$, $z_{0}=0$ equals zero; its denominator is never used at $k=N$.'''
theorem=r'''### Theorem
For every integer $N\ge1$, $L>0$, and $R\ge0$, let $A$ be monotone and $L$-Lipschitz on a real finite-dimensional Euclidean space. Assume $A(x_{\star})=0$, $\|x_{0}-x_{\star}\|^{2}\le R^{2}$, and $z_{0}=0$. The supplied dual FEG iteration with $\alpha=1/L$ satisfies
$$\boxed{\|A(x_{N})\|^{2}\le\frac{4L^{2}R^{2}}{N^{2}}.}$$
'''+formula
outline=r'''### Proof outline
Write $X=x_{N}$, $G=A(X)$ and
$$\Phi(t,x,z)=-4\langle G,z\rangle-2\|z\|^{2}+\frac{4L}{t}\langle G+z,x-X\rangle+\frac{4L}{N}\langle G,X-x_{0}\rangle.$$
Thus $V_{k}=\Phi(N-k,x_{k},z_{k})$ for $k<N$, $V_{0}=0$, and $V_{N}=2\|G\|^{2}+(4L/N)\langle G,X-x_{0}\rangle$.
Define the nonpositive residuals
$$\operatorname{Lip}(u,v)=\|A(u)-A(v)\|^{2}-L^{2}\|u-v\|^{2},\qquad
\operatorname{Mon}(u,v)=-\langle A(u)-A(v),u-v\rangle.$$
Substituting the iteration gives, for $0\le k\le N-2$ and $t=N-k\ge2$,
$$V_{k+1}-V_{k}=\frac{2}{t^{2}}\operatorname{Lip}(x_{k},y_{k})+\frac{4L}{t(t-1)}\operatorname{Mon}(X,y_{k})\le0.$$
All coefficients are positive. At the last step, $X=y_{N-1}=x_{N-1}-(z_{N-1}+A(x_{N-1}))/L$, and
$$V_{N}-V_{N-1}=2\operatorname{Lip}(x_{N-1},X)\le0.$$
For $N=1$, the separate direct identity is $V_{1}=2\operatorname{Lip}(x_{0},x_{1})\le0$, so every horizon has $V_{N}\le V_{0}=0$.
Finally, with $d=x_{0}-x_{\star}$,
$$\|G\|^{2}-\frac{4L^{2}R^{2}}{N^{2}}
=V_{N}+\frac{4L}{N}\operatorname{Mon}(X,x_{\star})
-\left\|\frac{2L}{N}d-G\right\|^{2}
+\frac{4L^{2}}{N^{2}}(\|d\|^{2}-R^{2})\le0.$$
The last inequality uses monotonicity, nonnegativity of a squared norm, and the initial radius bound. This proves the theorem, including $R=0$, without dividing by $R$.'''
nb.cells[1:2]=[nbf.v4.new_markdown_cell('## Proof Statement'),nbf.v4.new_markdown_cell(theorem),nbf.v4.new_markdown_cell(outline)]
# Preserve the historical B4 candidate discussion, followed by its resolved formula.
last=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Symbolic step'))
def code(name):return (root/'supplementary'/name).read_text(encoding='utf-8-sig')
new=[nbf.v4.new_markdown_cell('## Closed-form conclusion\n'+formula+'\nThe exact symbolic calculations below validate the fitted coefficient structure for every admissible horizon and positive $L$. They also derive the local interpolation multipliers. The earlier numerical global certificate retains its separate analytic status.'),
nbf.v4.new_code_cell(code('b5_definitions.py')),
nbf.v4.new_markdown_cell('## Symbolic Step Recursion Verification'),
nbf.v4.new_markdown_cell(r'''For $t=N-k\ge2$, verify
$$\Phi(t-1,x_{k+1},z_{k+1})-\Phi(t,x_{k},z_{k})=\frac{2}{t^{2}}\operatorname{Lip}(x_{k},y_{k})+\frac{4L}{t(t-1)}\operatorname{Mon}(X,y_{k}).$$
The multipliers are first solved from the full coefficient equations. The residual $\mathrm{LHS}-\mathrm{RHS}$ must then simplify to zero in all scalar components.'''),
nbf.v4.new_code_cell(code('b5_step.py')),
nbf.v4.new_markdown_cell('## Base Case and Boundary Symbolic Verification'),
nbf.v4.new_markdown_cell(r'''For $N\ge2$ and $z_{0}=0$, verify $\Phi(N,x_{0},0)=0$ and
$$V_{1}=\frac{2}{N^{2}}\operatorname{Lip}(x_{0},y_{0})+\frac{4L}{N(N-1)}\operatorname{Mon}(X,y_{0}).$$
Both residuals $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero.'''),nbf.v4.new_code_cell(code('b5_base.py')),
nbf.v4.new_markdown_cell('### Last-step Identity Symbolic Verification'),
nbf.v4.new_markdown_cell(r'''At the actual final update $X=x_{N-1}-(z_{N-1}+A(x_{N-1}))/L$, verify
$$V_{N}-\Phi(1,x_{N-1},z_{N-1})=2\operatorname{Lip}(x_{N-1},X).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero.'''),nbf.v4.new_code_cell(code('b5_terminal.py')),
nbf.v4.new_markdown_cell('### Boundary Identity Symbolic Verification'),
nbf.v4.new_markdown_cell(r'''For $d=x_{0}-x_{\star}$ and $A(x_{\star})=0$, verify
$$\|G\|^{2}-\frac{4L^{2}R^{2}}{N^{2}}=V_{N}+\frac{4L}{N}\operatorname{Mon}(X,x_{\star})-\left\|\frac{2L}{N}d-G\right\|^{2}+\frac{4L^{2}}{N^{2}}(\|d\|^{2}-R^{2}).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero.'''),nbf.v4.new_code_cell(code('b5_boundary.py')),
nbf.v4.new_markdown_cell('### Small horizon and domain signs'),
nbf.v4.new_markdown_cell(r'''For $N=1$, verify separately
$$V_{1}=2\operatorname{Lip}(x_{0},x_{1}),\qquad x_{1}=x_{0}-A(x_{0})/L.$$
There is no interior denominator $N-1$ in this case. For all other steps, $t\ge2$, so $2/t^{2}>0$ and $4L/[t(t-1)]>0$. The terminal and boundary coefficients are positive because $L>0$ and $N\ge1$. The subtracted square is nonnegative. These signs give $V_{N}\le0$ and the displayed boundary identity gives the rate. No positivity of $V_{k}$ itself is required.'''),nbf.v4.new_code_cell(code('b5_small_domain.py'))]
nb.cells[last:]=new
# Add the labeled selected true S, alongside existing candidate and decomposition checks.
for c in nb.cells:
    if c.cell_type=='code' and c.source.startswith('pf.pprint_labeled_matrix(E,'):
        c.source+='\nprint("Selected numerical S:")\npf.pprint_labeled_matrix(S_array, row_labels=selected["basis_vectors"])\n'
        break
# Candidate coefficient displays supplement their numerical comparisons.
for c in nb.cells:
    if c.cell_type=='code' and c.source.startswith('def coeff_pattern'):
        c.source+='\nfor index in range(1, N_int+1):\n    pf.pprint_labeled_matrix(coeff_pattern(index,N_int),row_labels=V_k_basis_labels(index))\n'
        break
for c in nb.cells:
    if c.cell_type=='markdown':
        assert '\\(' not in c.source and '\\[' not in c.source
        assert not any(ord(x)<32 and x not in '\n\t' for x in c.source)
nbf.write(nb,path)
(root/'supplementary/b5-proof-theorem.md').write_text(theorem+'\n\n'+outline,encoding='utf-8')
print('Final notebook source prepared; awaiting static checks and clean nbconvert execution.')
