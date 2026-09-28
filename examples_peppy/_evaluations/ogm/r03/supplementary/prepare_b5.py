"""Finalize notebook mathematics before required static and kernel verification."""
from pathlib import Path

import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"ogm_example_lyap.ipynb"
nb=nbf.read(path,as_version=4)
formula=r"""Write $g_{k}=\nabla f(x_{k})$, $T=\theta_{N}$, and
$$\rho_{k}=\begin{cases}\theta_{k},&0\leq k<N,\\ T/2,&k=N.\end{cases}$$
For $0\leq k\leq N$, define
$$V_{k}=\frac{L}{2T^{2}}\bigl(\|z_{k}-x_{\star}\|^{2}-\|x_{0}-x_{\star}\|^{2}\bigr)
+\frac{2\theta_{k-1}^{2}}{T^{2}}(f(x_{k})-f(x_{\star}))
+\frac{\theta_{k-1}^{2}}{LT^{2}}\|g_{k}\|^{2}
+\frac{2\rho_{k}}{T^{2}}\langle g_{k},x_{k}-z_{k}\rangle.$$
Here $\theta_{-1}=0$, so $V_{0}=0$. The terminal coefficient uses $\rho_{N}=T/2$.
"""
theorem=r"""### Theorem
Under the smooth-convex assumptions and the algorithm stated above, the following potential is nonincreasing for every integer $N\geq1$, every $L>0$, and every $R\geq0$.
"""+formula+r"""
The terminal identity implies the finite-horizon bound
$$\boxed{f(x_{N})-f(x_{\star})\leq\frac{L R^{2}}{2\theta_{N}^{2}}.}$$
The claim is an upper bound; no separate arbitrary-horizon tightness construction is asserted.
"""
outline=r"""### Proof outline
"""+formula+r"""
Define the nonpositive interpolation residual
$$I_{i,j}=f(x_{j})-f(x_{i})+\langle g_{j},x_{i}-x_{j}\rangle+\frac{\|g_{i}-g_{j}\|^{2}}{2L}\leq0,$$
including $x_{\star}$ with $g_{\star}=0$.
The exact recursion, including the final update, is
$$V_{k+1}-V_{k}=\frac{2\theta_{k}}{T^{2}}I_{\star,k}+\frac{2\theta_{k}^{2}}{T^{2}}I_{k,k+1}\leq0\qquad(0\leq k<N).$$
Both multipliers are positive. Thus $V_{N}\leq V_{0}=0$. The terminal relation is
$$f(x_{N})-f(x_{\star})-\frac{L}{2T^{2}}\|x_{0}-x_{\star}\|^{2}
=V_{N}+\frac{I_{\star,N}}{T}-\frac{L}{2T^{2}}\left\|z_{N}-x_{\star}-\frac{T}{L}g_{N}\right\|^{2}\leq0.$$
The initial radius bound gives the stated result. Separate exact checks below cover the generic step, the base step, the terminal identity, normalization, and $N=1$.
"""
nb.cells[1:2]=[nbf.v4.new_markdown_cell("## Proof Statement"),nbf.v4.new_markdown_cell(theorem),nbf.v4.new_markdown_cell(outline)]
for cell in nb.cells:
    if cell.cell_type=='markdown' and cell.source.startswith('### Block 4 conclusion'):
        cell.source=r"""### Block 4 conclusion and resolved formula
The numerical basis reconstructs every index. The sparse ansatz suggested by the coefficient matrices is resolved and verified symbolically in Block 5 below:
"""+formula+r"""
In the four-vector order $[x_{0}-x_{\star},z_{k}-x_{\star},x_{k}-x_{\star},g_{k}]$, the only nonzero matrix entries are
$$C_{00}=-\frac{L}{2T^{2}},\quad C_{11}=\frac{L}{2T^{2}},\quad
C_{13}=C_{31}=-\frac{\rho_{k}}{T^{2}},\quad C_{23}=C_{32}=\frac{\rho_{k}}{T^{2}},\quad
C_{33}=\frac{\theta_{k-1}^{2}}{LT^{2}}.$$
At $k=1$, the three-vector order is $[x_{0}-x_{\star},z_{1}-x_{\star},g_{1}]$; its nonzero entries are
$$C_{00}=-\frac{L}{2T^{2}},\quad C_{11}=\frac{L}{2T^{2}},\quad
C_{02}=C_{20}=\frac{1}{2\theta_{1}T^{2}},\quad C_{12}=C_{21}=-\frac{1}{2\theta_{1}T^{2}},\quad C_{22}=\frac{1}{LT^{2}}.$$
The function component is exactly $2\theta_{k-1}^{2}(f(x_{k})-f(x_{\star}))/T^{2}$; all earlier gap coefficients, the absolute-function coefficient, and the offset are zero. Numerical roundoff terms in the discovery certificate remain documented above.
"""
source=(ROOT/"supplementary"/"b5_symbolic_cells.py").read_text()
parts={chunk.split('\n',1)[0]:chunk.split('\n',1)[1] for chunk in source.split('# %% ')[1:]}
def md(text):
    return nbf.v4.new_markdown_cell(text)
def code(text):
    return nbf.v4.new_code_cell(text)
nb.cells.extend([
md("## Closed-form derivation\nThe saved B4 structure is retained as numerical discovery evidence. The following calculation derives and verifies a universal potential without replacing the selected numerical certificate."),
code('b4_final = json.loads((notebook_dir / "state" / "ogm_b4.json").read_text())\nassert b4_final["numerical_reconstruction"]["certificate_id"] == b4_final["certificate_id"]\nprint("Selected certificate:",b4_final["certificate_id"])\nprint("Discovery coefficient formula status:",b4_final["coefficient_formula_status"])'),
md(r"""### Symbolic recursion context and coefficient equations
Let $t=\theta_{k}$ and $u=\theta_{k+1}$. For an ordinary current step, $\theta_{k-1}^{2}=t^{2}-t$. At the next point, both the ordinary and terminal recurrences imply
$$\rho_{k+1}(u-1)=t^{2}.$$
Thus the same symbolic step covers both cases by using $\rho_{k+1}=t^{2}/(u-1)$. The sparse ansatz uses constants $a,b,c,d$ for the norm difference, function gap, gradient square, and mixed term in $T^{2}V_{k}$, and local multipliers $mt$ and $nt^{2}$. The radius normalization fixes $a=1/2$. Solving all Gram, function, and constant equations gives $b=d=m=n=2$ and $c=1$; substituting them back is checked separately.
"""),code(parts["Symbolic setup"]),code(parts["Derivation"]),
md("## Symbolic Step Recursion Verification"),
md(r"""The exact identity is
$$V_{k+1}-V_{k}=\frac{2\theta_{k}}{T^{2}}I_{\star,k}+\frac{2\theta_{k}^{2}}{T^{2}}I_{k,k+1}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in the Gram, function, and constant coordinates. The generic calculation uses $u\ne1$ and applies at every $0\leq k<N$ under the stated recurrences.
"""),code(parts["Step"]),
md("## Base Case and Boundary Symbolic Verification"),
md(r"""With $z_{0}=x_{0}$ and $\theta_{0}=1$,
$$V_{0}=0,\qquad V_{1}-V_{0}=\frac{2}{T^{2}}I_{\star,0}+\frac{2}{T^{2}}I_{0,1}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. The first update is constructed separately, with symbolic $u=\theta_{1}$, covering both $N=1$ and $N>1$.
"""),code(parts["Base"]),
md(r"""### Initial basis reduction
The actual first update gives $x_{1}-z_{1}=(\theta_{1}-1)(x_{0}-z_{1})/(2\theta_{1})$. Therefore the three-vector coefficient formula shown above equals $V_{1}$. The following full-coordinate residual must vanish.
"""),code(parts["First coefficient reduction"]),
md("### Boundary Identity Symbolic Verification"),
md(r"""Using $2\theta_{N-1}^{2}=T^{2}-T$,
$$f(x_{N})-f(x_{\star})-\frac{L}{2T^{2}}\|x_{0}-x_{\star}\|^{2}
=V_{N}+\frac{I_{\star,N}}{T}-\frac{L}{2T^{2}}\left\|z_{N}-x_{\star}-\frac{T}{L}g_{N}\right\|^{2}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish. The square is subtracted, so it is discarded in the upper-bound direction.
"""),code(parts["Boundary"]),
md(r"""### Radius normalization
Adding the initial residual gives
$$f(x_{N})-f(x_{\star})-\frac{LR^{2}}{2T^{2}}
=V_{N}+\frac{I_{\star,N}}{T}-S+\frac{L}{2T^{2}}\bigl(\|x_{0}-x_{\star}\|^{2}-R^{2}\bigr).$$
Here $S=L\|z_{N}-x_{\star}-Tg_{N}/L\|^{2}/(2T^{2})$. The residual is checked exactly, including its $R^{2}$ offset.
"""),code(parts["Normalization"]),
md(r"""### Recurrence and one-step horizon checks
The defining square roots give $\theta_{k}^{2}-\theta_{k}=\theta_{k-1}^{2}$ before the terminal index and $T^{2}-T=2\theta_{N-1}^{2}$ at the terminal index. For $N=1$, $\theta_{0}=1$ and $T=2$; the exact terminal identity is also checked directly in the first-step context.
"""),code(parts["Terminal and small horizon recurrence checks"]),
md("### Closed-form coefficient matrices and numerical correspondence\nThe exact formulas are now compared with the retained numerical matrices and all partial-sum components at horizons 4 and 6. These comparisons connect the exact proof to the discovery path; the symbolic identities establish the theorem."),code((ROOT/"supplementary"/"b5_formula_cells.py").read_text()),
md(r"""### Domain, signs, and telescoping proof
Induction from $\theta_{0}=1$ gives $\theta_{k}\geq1$, with $\theta_{k}>1$ for $k\geq1$; the terminal recurrence gives $T\geq2$. Hence all denominators used above are nonzero. In particular $u-1>0$ in every actual update. Since $L>0$, all local multipliers $2\theta_{k}/T^{2}$, $2\theta_{k}^{2}/T^{2}$, the terminal multiplier $1/T$, and the square/normalization coefficient $L/(2T^{2})$ are positive. The interpolation residuals and initial-radius residual are nonpositive. The exact identities therefore imply $V_{k+1}\leq V_{k}$ and the upper-bound direction in the theorem. No positivity of $V_{k}$ itself is required. The argument contains no division by $R$ and includes $R=0$.

The full analytic certificate follows by the finite telescoping sum of the verified local identities:
$$V_{N}=\sum_{k=0}^{N-1}\left(\frac{2\theta_{k}}{T^{2}}I_{\star,k}+\frac{2\theta_{k}^{2}}{T^{2}}I_{k,k+1}\right).$$
Substitution into the radius identity gives
$$f(x_{N})-f(x_{\star})-\frac{LR^{2}}{2T^{2}}
-\frac{L}{2T^{2}}\bigl(\|x_{0}-x_{\star}\|^{2}-R^{2}\bigr)
-\sum_{k=0}^{N-1}\left(\frac{2\theta_{k}}{T^{2}}I_{\star,k}+\frac{2\theta_{k}^{2}}{T^{2}}I_{k,k+1}\right)
-\frac{I_{\star,N}}{T}+S=0.$$
This proves the global multiplier and square formulas as well as the Lyapunov theorem for arbitrary authorized assumptions and every integer horizon. The numerical certificates remain separate fixed-sample evidence. All coefficient functions left unresolved in B4 are resolved by the displayed matrices and gap coefficient.
""")])
for cell in nb.cells:
    if cell.cell_type=='markdown':
        assert not any(s in cell.source for s in ('\x0c','\r','\\(','\\['))
nbf.write(nb,path)
print("Final notebook prepared for static checks and clean-kernel execution.")
