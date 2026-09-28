"""Assemble final theorem and native symbolic proof cells without executing."""

import re
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
theorem = r"""### Theorem
Under the stated assumptions, for every integer $N\geq1$ the given dual FEG algorithm satisfies
$$\boxed{\|A(x_{N})\|^2\leq\frac{4L^2R^2}{N^2}.}$$
An exact terminal-dependent Lyapunov certificate is obtained by writing $g=A(x_{N})$, $a=x_{0}-x_{N}$, $b_{k}=x_{k}-x_{N}$ and defining, for $0\leq k<N$,
$$V_{k}=-\frac{4L}{N}\langle g,a\rangle+\frac{4L}{N-k}\langle g,b_{k}\rangle-4\langle g,z_{k}\rangle+\frac{4L}{N-k}\langle b_{k},z_{k}\rangle-2\|z_{k}\|^2,$$
with the separate terminal expression
$$V_{N}=2\|g\|^2-\frac{4L}{N}\langle g,a\rangle.$$
Then $V_{0}=0$ and $V_{k+1}\leq V_{k}$ for every step. The certificate uses the terminal point as an anchor; it is not required to be positive. The rate bound is valid, but not tight at $N=1$ according to the numerical PEP evidence.
"""
outline = r"""### Proof outline
Define the nonpositive residuals
$$\operatorname{Lip}(u,v)=\|A(u)-A(v)\|^2-L^2\|u-v\|^2\leq0,\qquad
\operatorname{Mon}(u,v)=-\langle A(u)-A(v),u-v\rangle\leq0.$$
For $g=A(x_{N})$, $a=x_{0}-x_{N}$ and $b_{k}=x_{k}-x_{N}$, use
$$V_{k}=-\frac{4L}{N}\langle g,a\rangle+\frac{4L}{N-k}\langle g,b_{k}\rangle-4\langle g,z_{k}\rangle+\frac{4L}{N-k}\langle b_{k},z_{k}\rangle-2\|z_{k}\|^2\quad(0\leq k<N),$$
and $V_{N}=2\|g\|^2-\frac{4L}{N}\langle g,a\rangle$. Since $z_{0}=0$ and $b_{0}=a$, $V_{0}=0$.

For $0\leq k\leq N-2$, put $t=N-k\geq2$. Substituting the algorithm's two updates gives the exact identity
$$V_{k+1}-V_{k}=\frac{2}{t^2}\operatorname{Lip}(x_{k},x_{k+1/2})+\frac{4L}{t(t-1)}\operatorname{Mon}(x_{k+1/2},x_{N})\leq0.$$
At the last step, $x_{N}=x_{N-1/2}=x_{N-1}-[z_{N-1}+A(x_{N-1})]/L$, and
$$V_{N}-V_{N-1}=2\operatorname{Lip}(x_{N-1},x_{N})\leq0.$$
These coefficients are positive on their stated domains. Thus $V_{N}\leq V_{0}=0$. For $N=1$, there are no interior steps; the last-step identity applies directly with $z_{0}=0$.

Finally, $A(x_{\star})=0$ gives the exact boundary identity
$$\begin{aligned}
\|g\|^2-\frac{4L^2R^2}{N^2}
={}&V_{N}+\frac{4L}{N}\operatorname{Mon}(x_{N},x_{\star})
-\left\|g-\frac{2L}{N}(x_{0}-x_{\star})\right\|^2\\
&+\frac{4L^2}{N^2}\bigl(\|x_{0}-x_{\star}\|^2-R^2\bigr).
\end{aligned}$$
Each term on the right is nonpositive: use the decrease just proved, monotonicity, nonnegativity of a squared norm, and the initial condition. This proves the stated bound, including $R=0$, without dividing by $R$ or $\|g\|$. The exact symbolic checks below cover Gram, function-value and constant components separately.
"""
top_cells = [md("## Proof Statement"), md(theorem), md(outline)]
for i, cell in enumerate(top_cells):
    cell.id = f"b5-top-{i:02d}"
nb.cells = [c for c in nb.cells if c.id != "b1-01" and not c.id.startswith("b5-")]
nb.cells[1:1] = top_cells
nb.cells[0].source = nb.cells[0].source.replace(
    "The conjectured bound is", "The bound proved below is"
)
for cell in nb.cells:
    if cell.id == "b2n8-00":
        cell.source = cell.source.replace(
            "Cross-horizon grouping is pending B3.",
            "The verified cross-horizon grouping appears below.",
        )
    if cell.id == "b4-12":
        cell.source = cell.source.replace(
            "Block 5 must establish parameter scaling, exact step/base/boundary identities, and the residual theorem; neither numerical reconstruction nor the coefficient fit establishes that theorem.",
            "The exact parameter scaling, step/base/boundary identities, and residual theorem are established below. The numerical reconstruction and fit above are the discovery evidence.",
        )


def source(name):
    return (ROOT / "supplementary" / name).read_text()


cells = [
    md(r"""## Exact Lyapunov formula and symbolic context
The coefficient pattern from B4 extends to arbitrary $L>0$ by multiplying each position–operator cross coefficient by $L$. This gives the formula in the theorem. We now verify it algebraically for arbitrary symbolic $N$ and $t=N-k$; no finite horizon is substituted. The local interpolation multipliers are derived by solving all scalar-coordinate equations. The separate terminal expression avoids the vanishing denominator at $t=0$.
"""),
    code(
        source("b5_symbolic_definitions.py")
        + "\n"
        + source("b5_analytic_coefficients.py")
    ),
    md("## Symbolic Step Recursion Verification"),
    md(r"""For $t=N-k\geq2$, verify
$$V_{k+1}-V_{k}=\frac{2}{t^2}\operatorname{Lip}(x_{k},x_{k+1/2})+\frac{4L}{t(t-1)}\operatorname{Mon}(x_{k+1/2},x_{N}).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero in every scalar component."""),
    code(source("b5_step.py")),
    md("## Base Case and Boundary Symbolic Verification"),
    md(r"""For all $N\geq1$, verify $V_{0}=0$ using $z_{0}=0$. For $N\geq2$, also construct the actual first update and verify
$$V_{1}=\frac{2}{N^2}\operatorname{Lip}(x_{0},x_{1/2})+\frac{4L}{N(N-1)}\operatorname{Mon}(x_{1/2},x_{N}).$$
Both residuals $\mathrm{LHS}-\mathrm{RHS}$ must be zero. The $N=1$ case is checked separately next."""),
    code(source("b5_base.py")),
    md("### Last step and exceptional horizon"),
    md(r"""Using $x_{N}=x_{N-1}-[z_{N-1}+A(x_{N-1})]/L$, verify
$$V_{N}-V_{N-1}=2\operatorname{Lip}(x_{N-1},x_{N}).$$
For $N=1$, explicitly verify $V_{1}=2\operatorname{Lip}(x_{0},x_{1})$ with $x_{1}=x_{0}-A(x_{0})/L$. Both residuals must be zero."""),
    code(source("b5_last_step.py")),
    md("### Boundary Identity Symbolic Verification"),
    md(r"""Verify the exact metric identity
$$\|A(x_{N})\|^2-\frac{4L^2R^2}{N^2}=V_{N}+\frac{4L}{N}\operatorname{Mon}(x_{N},x_{\star})-\left\|A(x_{N})-\frac{2L}{N}(x_{0}-x_{\star})\right\|^2+\frac{4L^2}{N^2}\bigl(\|x_{0}-x_{\star}\|^2-R^2\bigr).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. This includes the radius normalization and every boundary term."""),
    code(source("b5_boundary.py")),
    md(r"""### Sign, domain, and telescoping argument
All required signs are elementary: $L>0$, $N\geq1$, and interior $t\geq2$ make the denominators and multipliers positive. The last step has coefficient $2$. Monotonicity and Lipschitz continuity make their residuals nonpositive. The boundary square is nonnegative, and the initial residual is nonpositive. Hence $V_{N}\leq V_{0}=0$ and the exact boundary identity proves $\|A(x_{N})\|^2\leq4L^2R^2/N^2$. The proof covers $R=0$ and $N=1$ directly.

This is an analytic local Lyapunov proof. The original numerical full-PEP tables and their candidate formulas retain their discovery status; no separate arbitrary-horizon global full-PEP formula proof is claimed."""),
    code(source("b5_signs.py")),
]
for i, cell in enumerate(cells):
    cell.id = f"b5-{i:02d}"
nb.cells = [c for c in nb.cells if c.id != "b1-16"]
nb.cells.extend(cells)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        cell.source = re.sub(r"_([A-Za-z0-9])(?![A-Za-z0-9])", r"_{\1}", cell.source)
        assert not any(c in cell.source for c in ("\x0c", "\r", "\x08"))
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert cell.source.count("$$") % 2 == 0
nbformat.write(nb, path)
print(
    "Final proof notebook source assembled; static checks and clean execution remain."
)
