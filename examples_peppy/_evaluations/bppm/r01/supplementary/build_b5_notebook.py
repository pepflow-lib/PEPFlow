import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import re

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import runtime

root = runtime.ROOT
path = root / "bppm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
statement = md(r"""### Theorem

Under the stated Bregman proximal point assumptions, let $\alpha>0$, $R\ge0$, $N\ge1$ be an integer, and $D_h(x_{\star},x_{0})\le R$. No strong convexity of $h$ or Lipschitz gradient assumption is needed. Define
$$V_{0}=0,\qquad V_{k}=\frac{\alpha k\bigl(f(x_{k})-f(x_{\star})\bigr)+D_h(x_{\star},x_{k})-D_h(x_{\star},x_{0})}{\alpha N},\quad 1\le k\le N.$$
Then $V_{k+1}\le V_{k}$ and
$$0\le f(x_{N})-f(x_{\star})\le\frac{R}{\alpha N}.$$
The normalization is the supplied Bregman radius $R$, not $R^2$. The separate definition of $V_{0}$ does not require evaluating $f(x_{0})$.""")
outline = md(r"""### Proof outline

Write $I_q(u,v)=q(v)-q(u)+\langle\nabla q(v),u-v\rangle\le0$ for convex $q\in\{f,h\}$. Proximal optimality gives $\nabla h(x_{k+1})=\nabla h(x_{k})-\alpha\nabla f(x_{k+1})$.

Use $V_{0}=0$ and $V_{k}=k(f(x_{k})-f(x_{\star}))/N+[D_h(x_{\star},x_{k})-D_h(x_{\star},x_{0})]/(\alpha N)$ for $k\ge1$. The initial step is
$$V_{1}-V_{0}=\frac{1}{N}I_f(x_{\star},x_{1})+\frac{1}{\alpha N}I_h(x_{1},x_{0})\le0.$$
For $1\le k<N$, direct expansion and the proximal relation give the complete identity
$$V_{k+1}-V_{k}=\frac{1}{N}I_f(x_{\star},x_{k+1})+\frac{k}{N}I_f(x_{k},x_{k+1})+\frac{k+1}{\alpha N}I_h(x_{k+1},x_{k})+\frac{k}{\alpha N}I_h(x_{k},x_{k+1})\le0.$$
All multipliers are nonnegative, so $V_{N}\le V_{0}=0$. There are no additional squares or residual families in this exact local certificate. Finally,
$$f(x_{N})-f(x_{\star})-\frac{R}{\alpha N}=V_{N}+\frac{D_h(x_{\star},x_{0})-R}{\alpha N}+\frac{I_h(x_{\star},x_{N})}{\alpha N}\le0.$$
Here the last two terms are nonpositive by the initial condition and convexity, respectively. The lower bound follows because $x_{\star}$ minimizes $f$. When $N=1$, the initial step and boundary identity suffice; the proof also covers $R=0$.""")
nb.cells[1:2] = [md("## Proof Statement"), statement, outline]
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Exact step")
)


def source(name):
    return (root / "supplementary" / name).read_text(encoding="utf-8-sig")


nb.cells[start:] = [
    md(
        "## Exact coefficient derivation\n\nUse the Block 4 form $A_{k}(f(x_{k})-f(x_{\\star}))+B[D_h(x_{\\star},x_{k})-D_h(x_{\\star},x_{0})]$. The constant $B$ and local multipliers are initially symbolic. Extract all Gram, function-value and constant coefficient equations from the actual proximal update. The conditions $A_{0}=0$ and $A_{N}=1$ set the initial value and final performance normalization."
    ),
    code(source("b5_derivation.py")),
    md(r"""### Closed-form Lyapunov conclusion

The local equations give $A_{k+1}=A_k+\alpha B$. The base condition $A_{0}=0$ and terminal normalization $A_{N}=1$ yield $A_k=k/N$ and $B=1/(\alpha N)$. Thus
$$V_{0}=0,\qquad V_{k}=\frac{k}{N}\bigl(f(x_{k})-f(x_{\star})\bigr)+\frac{D_h(x_{\star},x_{k})-D_h(x_{\star},x_{0})}{\alpha N},\quad1\le k\le N.$$
In the ordered Block 4 basis the nonzero coefficients are $C_{01}=C_{10}=-1/(2\alpha N)$ and $C_{23}=C_{32}=1/(2\alpha N)$. This includes the function-value terms; the next sections verify the step, initial, and terminal identities exactly."""),
    md("## Symbolic Step Recursion Verification"),
    md(r"""For $1\le k<N$, verify
$$\mathrm{LHS}=V_{k+1}-V_{k}=\frac{I_f(x_{\star},x_{k+1})+kI_f(x_{k},x_{k+1})}{N}+\frac{(k+1)I_h(x_{k+1},x_{k})+kI_h(x_{k},x_{k+1})}{\alpha N}=\mathrm{RHS}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in every scalar coordinate. The preceding cell constructs both sides from the symbolic PEPFlow context; the following substitutes the derived coefficients."""),
    code(source("b5_step.py")),
    md("## Base Case and Boundary Symbolic Verification"),
    md(r"""In a separate initial-step context, verify
$$V_{0}=0,\qquad\mathrm{LHS}=V_{1}-V_{0}=\frac{I_f(x_{\star},x_{1})}{N}+\frac{I_h(x_{1},x_{0})}{\alpha N}=\mathrm{RHS}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. Both multipliers are positive for $\alpha>0$, $N\ge1$, proving the first decrease without evaluating $f(x_{0})$."""),
    code(source("b5_base.py")),
    md("### Boundary Identity Symbolic Verification"),
    md(r"""Verify the exact terminal relation
$$\mathrm{LHS}=f(x_{N})-f(x_{\star})-\frac{R}{\alpha N}=V_{N}+\frac{D_h(x_{\star},x_{0})-R}{\alpha N}+\frac{I_h(x_{\star},x_{N})}{\alpha N}=\mathrm{RHS}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. Since $I_h(x_{\star},x_{N})=-D_h(x_{\star},x_{N})\le0$, every term on the right is nonpositive after the step and initial-condition arguments."""),
    code(source("b5_boundary.py")),
    md(r"""### Signs, domain, and normalization

On the stated domain, $1/N$, $k/N$, $(k+1)/(\alpha N)$, and $k/(\alpha N)$ are nonnegative; $1/(\alpha N)>0$. Convexity supplies all interpolation signs. The initial condition supplies $D_h(x_{\star},x_{0})-R\le0$. Therefore the verified direction is $V_{N}\le V_{0}=0$, and the terminal identity proves the exact bound $R/(\alpha N)$. No division by $R$ occurs. A separate global full-PEP formula certification is not claimed; the analytic local Lyapunov proof is complete."""),
    code(source("b5_signs.py")),
]
# Source-only mathematical delimiter check under evaluation-ancillary-v1.
for cell in nb.cells:
    if cell.cell_type == "markdown":
        cell.source = re.sub(
            r"_(\\[A-Za-z]+|[A-Za-z0-9])",
            lambda m: "_{" + m.group(1) + "}",
            cell.source,
        )
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in cell.source)
nbf.write(nb, path)
print(
    "Final proof cells authored; awaiting static checks and fresh nbconvert execution."
)
