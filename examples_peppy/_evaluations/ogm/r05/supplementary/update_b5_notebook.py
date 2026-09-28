"""Finalize theorem, detailed proof, and executable exact checks in the notebook."""
from pathlib import Path

import nbformat

root = Path(__file__).resolve().parents[1]
path = root / 'ogm_example_lyap.ipynb'
nb = nbformat.read(path, as_version=4)
source = (root / 'supplementary/b5_math.py').read_text()
sections = {}
for part in source.split('# CELL: ')[1:]:
    name, body = part.split('\n', 1)
    sections[name] = body
sections['symbolic_setup'] = sections['symbolic_setup'].replace('from runtime import NOTEBOOK_DIR\n', '')
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
theorem = r"""### Theorem
Under the stated smooth convex assumptions and OGM updates, let $g_{k}=\nabla f(x_{k})$, $d=x_{0}-x_{\star}$ and $T=\theta_{N}$. Define $V_{0}=0$, and, for $1\leq k<N$,
$$V_{k}=\frac{1}{T^2}\left[2\theta_{k}^2(f(x_{k})-f(x_{\star}))
-\frac{\theta_{k}^2}{L}\|g_{k}\|^2+\frac L2\|z_{k+1}-x_{\star}\|^2-\frac L2\|d\|^2\right],$$
with the separate terminal value
$$V_{N}=f(x_{N})-f(x_{\star})-\frac{L}{2T^2}\|d\|^2.$$
For every integer $N\geq1$, this sequence is nonincreasing. Consequently
$$\boxed{f(x_{N})-f(x_{\star})\leq\frac{LR^2}{2\theta_{N}^2}.}$$
The constant is sharp: the one-dimensional function $f(x)=Lx^2/2$, with $x_{\star}=0$ and $x_{0}=R$, attains equality. For $N=1$, the interior range is empty and $\theta_{1}=2$; the bound is $LR^2/8$."""
outline = r"""### Proof outline
For any evaluated points $a,b$, smooth convex interpolation gives
$$I_{a,b}=f(b)-f(a)-\langle g_b,b-a\rangle+\frac1{2L}\|g_b-g_a\|^2\leq0,$$
where $g_{x_{\star}}=0$. Let $B=L\|d\|^2/2$ and, for $0\leq k<N$,
$$H_{k}=2\theta_{k}^2(f(x_{k})-f(x_{\star}))-\frac{\theta_{k}^2}{L}\|g_{k}\|^2+\frac L2\|z_{k+1}-x_{\star}\|^2.$$
Thus $V_{k}=(H_{k}-B)/T^2$ for $1\leq k<N$, $V_{0}=0$, and $V_{N}=f(x_{N})-f(x_{\star})-B/T^2$.

Since $\theta_{0}=1$ and $z_{1}=x_{0}-2g_{0}/L$, direct expansion gives
$$H_{0}-B=2I_{x_{\star},x_{0}}.$$
For $0\leq k\leq N-2$, the ordinary recurrence $\theta_{k+1}^2-\theta_{k+1}=\theta_{k}^2$ and the algorithm updates give the exact identity
$$H_{k+1}-H_{k}=2\theta_{k+1}I_{x_{\star},x_{k+1}}+2\theta_{k}^2I_{x_{k},x_{k+1}}.$$
At the terminal step, the distinct relation $T^2-T=2\theta_{N-1}^2$ gives
$$T^2(f(x_{N})-f(x_{\star}))-H_{N-1}
=T I_{x_{\star},x_{N}}+2\theta_{N-1}^2 I_{x_{N-1},x_{N}}
-\frac L2\left\|z_{N}-x_{\star}-\frac TL g_{N}\right\|^2.$$
These are polynomial identities in inner products and function values, so their exact coordinate verifications below apply in any finite dimension.

For $N\geq2$, the corresponding actual sequence starts with
$$V_{1}-V_{0}=\frac{2I_{x_{\star},x_{0}}+2\theta_{1}I_{x_{\star},x_{1}}+2I_{x_{0},x_{1}}}{T^2}\leq0.$$
For $1\leq k\leq N-2$ its increment is
$$V_{k+1}-V_{k}=\frac{2\theta_{k+1}I_{x_{\star},x_{k+1}}+2\theta_{k}^2I_{x_{k},x_{k+1}}}{T^2}\leq0,$$
and its last increment is
$$V_{N}-V_{N-1}=\frac{T I_{x_{\star},x_{N}}+2\theta_{N-1}^2 I_{x_{N-1},x_{N}}
-\frac L2\|z_{N}-x_{\star}-(T/L)g_{N}\|^2}{T^2}\leq0.$$
For $N=1$ the direct identity is
$$V_{1}=\tfrac12(I_{x_{\star},x_{0}}+I_{x_{\star},x_{1}}+I_{x_{0},x_{1}})
-\frac L8\|z_{1}-x_{\star}-(2/L)g_{1}\|^2\leq0.$$
Every theta is positive by its positive-root definition, $L>0$, and all squared norms are nonnegative. Hence every displayed increment has the asserted sign. Now $V_{N}\leq V_{0}=0$ implies
$$f(x_{N})-f(x_{\star})\leq\frac{L\|d\|^2}{2T^2}\leq\frac{LR^2}{2T^2}.$$
No division by $R$ is used, so the argument includes $R=0$.

For sharpness, $f(x)=Lx^2/2$ has $y_{k+1}=0$. Induction from $\theta_{0}=1$, $x_{0}=z_{0}=R$ gives $z_{k}=(-1)^kR$ and $x_{k}=(-1)^kR/\theta_{k}$, using the special terminal coefficient in the last update. Thus $f(x_{N})=LR^2/(2T^2)$."""
nb.cells[1:2] = [md('## Proof Statement'), md(theorem), md(outline)]
nb.cells[-1].source = nb.cells[-1].source.split('## Closed-form Lyapunov function and exact proof')[0]
nb.cells += [
    md(r"""## Closed-form Lyapunov function and exact proof
The diagonal coefficients suggested by B4 are now verified analytically, using the minimal contexts below. It is convenient to work with $H_{k}=T^2V_{k}+B$ in the interior. The base identity and ordinary-step recurrence show inductively that
$$H_{k}-B=2\sum_{i=0}^{k}\theta_{i}I_{x_{\star},x_i}
+2\sum_{i=0}^{k-1}\theta_{i}^2I_{x_i,x_{i+1}}\quad(0\leq k<N).$$
This establishes the exact coefficient formula and its agreement with the partial-sum construction, rather than relying on numerical fitting. The terminal identity supplies the separately normalized endpoint. The complete formulas for $V_{k}$, including function gaps, appear in the theorem above."""),
    md('### Symbolic recursion context and coefficient formulas\nParameters $L,t,u$ are positive. The ordinary relation is $t^2=u^2-u$; the terminal relation is $2t^2=u^2-u$. Exact polynomial remainders impose only these proved recurrence identities. Denominators are powers of positive $L,u$.'),
    code(sections['symbolic_setup']),
    code("T_symbol = sp.symbols('T', positive=True)\nC_closed = sp.diag(-L_symbol/(2*T_symbol**2), L_symbol/(2*T_symbol**2), -t_symbol**2/(L_symbol*T_symbol**2))\npf.pprint_labeled_matrix(np.array(C_closed.tolist(), dtype=object), ['d', 'q_k', 'g_k'], precision=0)\ngap_symbol, d_squared, q_squared, g_squared = sp.symbols('gap d_squared q_squared g_squared', real=True)\nV_symbolic = (2*t_symbol**2*gap_symbol - t_symbol**2*g_squared/L_symbol + L_symbol*q_squared/2 - L_symbol*d_squared/2)/T_symbol**2\nprint('Interior V_k:', V_symbolic)\nprint('LaTeX:', sp.latex(V_symbolic))"),
    md('## Symbolic Step Recursion Verification'),
    md(r"""For $0\leq k\leq N-2$, set $t=\theta_{k}$, $u=\theta_{k+1}$. Verify
$$H_{k+1}-H_{k}=2uI_{x_{\star},x_{k+1}}+2t^2I_{x_k,x_{k+1}},\qquad t^2=u^2-u.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero in Gram, function-value and constant coordinates."""),
    code(sections['step']),
    md('## Base Case and Boundary Symbolic Verification'),
    md(r"""Using $\theta_{0}=1$ and $z_{1}=x_{0}-2g_{0}/L$, verify
$$H_{0}-\frac L2\|x_{0}-x_{\star}\|^2=2I_{x_{\star},x_{0}}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero in every scalar component. The right side is nonpositive, giving the base bound $H_{0}\leq B$."""),
    code(sections['base']),
    md('### Boundary Identity Symbolic Verification'),
    md(r"""Let $t=\theta_{N-1}$ and $u=\theta_{N}$, with $2t^2=u^2-u$. Verify
$$u^2(f(x_{N})-f(x_{\star}))-H_{N-1}
=uI_{x_{\star},x_{N}}+2t^2I_{x_{N-1},x_{N}}
-\frac L2\|z_{N}-x_{\star}-(u/L)g_{N}\|^2.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero in every scalar component."""),
    code(sections['terminal']),
    md('### Exceptional horizon $N=1$'),
    md(r"""There is no ordinary interior transition when $N=1$. Here $\theta_{0}=1$, $\theta_{1}=2$, and $x_{1}=x_{0}-3g_{0}/(2L)$. Verify the direct identity
$$f(x_{1})-f(x_{\star})-\frac L8\|x_{0}-x_{\star}\|^2
=\frac12(I_{x_{\star},x_{0}}+I_{x_{\star},x_{1}}+I_{x_{0},x_{1}})
-\frac L8\|z_{1}-x_{\star}-(2/L)g_{1}\|^2.$$
Again $\mathrm{LHS}-\mathrm{RHS}=0$."""),
    code(sections['small_horizon']),
    md(r"""### Signs, domain, and normalization
Starting at $\theta_{0}=1$, both positive-root recurrences produce positive real values. Their polynomial identities justify the reductions used above. Therefore the interpolation multipliers and square coefficient are positive. Every interpolation residual is nonpositive for convex $L$-smooth $f$, so all increments decrease. The initial-distance assumption then gives the theorem exactly, including $R=0$. These domain and sign facts hold for all integer horizons, not only the numerical samples."""),
    code(sections['domain']),
    md(r"""### Telescoped full certificate
Adding the exact base, ordinary steps, and terminal identity cancels every $H_k$, giving
$$f(x_{N})-f(x_{\star})-\frac{L}{2T^2}\|d\|^2
=\sum_{i=0}^{N-1}\frac{2\theta_i}{T^2}I_{x_{\star},x_i}
+\frac1T I_{x_{\star},x_N}
+\sum_{i=0}^{N-1}\frac{2\theta_i^2}{T^2}I_{x_i,x_{i+1}}
-\frac{L}{2T^2}\|z_N-x_{\star}-(T/L)g_N\|^2.$$
The same cancellation works when the ordinary-step sum is empty at $N=1$. Hence the global lambda and slack candidates of B2 are analytically verified as well. Adding $(L/(2T^2))(\|d\|^2-R^2)$ to the right gives the full-PEP identity normalized by $LR^2/(2T^2)$. All interpolation multipliers and the initial multiplier are nonnegative, and the final slack is a nonnegative square."""),
    md('### Sharpness\nFor $f(x)=Lx^2/2$, write $x_k=\\sigma R/t$ and $z_k=\\sigma R$. The exact scalar update below flips the sign and divides the new iterate by the new coefficient. Taking $\\sigma=(-1)^k$ proves the equality example by induction.'),
    code(sections['tightness']),
    md(r"""### Final conclusion
The exact symbolic step, base, terminal, and exceptional-horizon identities all vanish in Gram, function and constant coordinates. Their signs prove the nonincreasing Lyapunov sequence and the sharp guarantee
$$f(x_N)-f(x_{\star})\leq\frac{LR^2}{2\theta_N^2}.$$
The numerical certificate, analytic full-PEP identity, and analytic Lyapunov proof are separately established. Static checks and clean-kernel execution accompany this notebook. No rendered visual inspection was performed, in accordance with the evaluation presentation policy.""")
]
nbformat.write(nb, path)
