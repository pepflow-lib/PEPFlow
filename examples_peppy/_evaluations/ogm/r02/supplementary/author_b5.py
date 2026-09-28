"""Finalize the mathematical exposition and visible exact proof cells."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supplementary"))
# optional notebook-generation dependency
import nbformat as nbf  # noqa: E402  # ty: ignore[unresolved-import]
from b5_notebook_cells import (  # noqa: E402 - imports follow runtime or notebook setup
    BASE,
    BOUNDARY,
    HELPERS,
    LOAD,
    SIGNS,
    SMALL,
    STEP,
    TERMINAL,
)

THEOREM = r"""### Theorem
Let $f$ be convex and $L$-smooth, with $L>0$, $R\ge0$, $\nabla f(x_{\star})=0$, and $\|x_{0}-x_{\star}\|\le R$.
Run the stated OGM iteration for any integer $N\ge1$, including its special terminal coefficient. Write $g_{k}=\nabla f(x_{k})$, $T=\theta_{N}$, $d_{0}=x_{0}-x_{\star}$, and $q_{N}=z_{N}-x_{\star}-Tg_{N}/L$.
Define $V_{0}=0$ and, for $1\le k<N$,
$$V_{k}=\frac{L}{2T^{2}}\left(\|z_{k+1}-x_{\star}\|^{2}-\|d_{0}\|^{2}\right)
-\frac{\theta_{k}^{2}}{LT^{2}}\|g_{k}\|^{2}
+\frac{2\theta_{k}^{2}}{T^{2}}\left(f(x_{k})-f(x_{\star})\right).$$
At the terminal index set
$$V_{N}=f(x_{N})-f(x_{\star})+\frac{L}{2T^{2}}\left(\|q_{N}\|^{2}-\|d_{0}\|^{2}\right).$$
Then $V_{N}\le\cdots\le V_{1}\le V_{0}=0$, and consequently
$$\boxed{f(x_{N})-f(x_{\star})\le\frac{LR^{2}}{2\theta_{N}^{2}}.}$$
For $N=1$ the interior formula has an empty index range, and the terminal formula still applies.
"""

OUTLINE = r"""### Proof outline
For two evaluation points define the smooth convex interpolation residual
$$I_{i,j}=f(x_{j})-f(x_{i})+\langle g_{j},x_{i}-x_{j}\rangle+\frac{1}{2L}\|g_{i}-g_{j}\|^{2}\le0,$$
where $x_{\star}$ is the stationary minimizer and $g_{\star}=0$.
The potential consists of the norm difference with coefficient $L/(2T^{2})$, the gradient term $-\theta_{k}^{2}\|g_{k}\|^{2}/(LT^{2})$, and the gap term $2\theta_{k}^{2}(f(x_{k})-f(x_{\star}))/T^{2}$; its terminal expression is the gap plus $L(\|q_{N}\|^{2}-\|d_{0}\|^{2})/(2T^{2})$.

For $N\ge2$, direct use of the updates and $\theta_{k+1}^{2}-\theta_{k+1}=\theta_{k}^{2}$ gives
$$V_{1}=\frac{2I_{\star,0}+2\theta_{1}I_{\star,1}+2\theta_{0}^{2}I_{0,1}}{T^{2}},$$
$$V_{k+1}-V_{k}=\frac{2\theta_{k+1}}{T^{2}}I_{\star,k+1}+\frac{2\theta_{k}^{2}}{T^{2}}I_{k,k+1}\quad(1\le k\le N-2).$$
The distinct terminal recurrence $T^{2}-T=2\theta_{N-1}^{2}$ gives
$$V_{N}-V_{N-1}=\frac1T I_{\star,N}+\frac{2\theta_{N-1}^{2}}{T^{2}}I_{N-1,N}.$$
For $N=1$, $\theta_{0}=1$ and $T=2$; the exact exceptional identity is
$$V_{1}=\tfrac12\left(I_{\star,0}+I_{\star,1}+I_{0,1}\right).$$
All multipliers are positive. Hence every displayed increment is nonpositive and $V_{N}\le0$.
Finally,
$$f(x_{N})-f(x_{\star})-\frac{LR^{2}}{2T^{2}}
=V_{N}-\frac{L}{2T^{2}}\|q_{N}\|^{2}
+\frac{L}{2T^{2}}\left(\|d_{0}\|^{2}-R^{2}\right)\le0.$$
The last two terms are nonpositive by squared-norm nonnegativity and the initial condition. This argument includes $R=0$ without dividing by $R$.
The exact symbolic cells below verify every identity in all scalar components; finite-sample numerical agreement is not used as the proof.
"""

FORMULA = r"""## Closed-form Lyapunov conclusion
The B4 candidate formulas are now established by the exact identities below. Define the useful unnormalized quantities
$$U_{k}=\frac L2\|z_{k+1}-x_{\star}\|^{2}+2\theta_{k}^{2}\bigl(f(x_{k})-f(x_{\star})\bigr)-\frac{\theta_{k}^{2}}L\|g_{k}\|^{2}\quad(0\le k<N),$$
$$U_{N}=T^{2}\bigl(f(x_{N})-f(x_{\star})\bigr)+\frac L2\|q_{N}\|^{2},\qquad c=\frac L2\|d_{0}\|^{2}.$$
For $1\le k\le N$, $V_{k}=(U_{k}-c)/T^{2}$; the discovery sequence has the exceptional base $V_{0}=0$.
Thus the complete closed form is the theorem's norm, gradient, and function-gap expression, with no scalar offset.
The base check proves $U_{0}\le c$, and the step and terminal checks prove $U_{N}\le\cdots\le U_{0}$. These facts also establish the exceptional first increment $V_{1}\le V_{0}$.
The generic local verification uses arbitrary consecutive coefficients satisfying the recurrence, so it applies at every admissible index and horizon, rather than just the numerical sample.
"""

DOMAIN = r"""## Domain, signs, and telescoping
Since $\theta_{-1}=0$, the ordinary recurrence gives $\theta_{0}=1$. If its previous coefficient is positive, its square root exceeds one, so the next coefficient exceeds one. Induction proves positivity of every coefficient. The terminal coefficient is also positive (indeed at least two), and squaring its defining equation yields $T^{2}-T=2\theta_{N-1}^{2}$. The ordinary equation gives $\theta_{k+1}^{2}-\theta_{k+1}=\theta_{k}^{2}$.
These relations justify the substitutions in the symbolic contexts. Their local identities require only these relations and $L>0$; generic independent vectors ensure no hidden geometric assumption is introduced.
The local multipliers $2\theta_{k+1}$, $2\theta_{k}^{2}$, and $T$ are positive; the normalization coefficients $T^{-2}$ and $L/(2T^{2})$ are positive. Every interpolation residual is nonpositive for a smooth convex function, and every squared norm is nonnegative. Therefore all steps decrease $U$ and the normalized sequence decreases $V$ in the direction stated in the theorem. The boundary identity gives the exact finite-horizon rate under $\|d_{0}\|^{2}\le R^{2}$.
The local Lyapunov proof is complete. The earlier global full-PEP formulas remain recorded as numerical candidates; no separate global analytic certificate flag is inferred from the local proof.
"""

path = ROOT / "ogm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
start = next(
    i for i, c in enumerate(nb.cells) if c.id in ("proof-placeholder", "proof-heading")
)
end = next(i for i, c in enumerate(nb.cells) if c.id == "b1-imports")
nb.cells[start:end] = [
    nbf.v4.new_markdown_cell("## Proof Statement", id="proof-heading"),
    nbf.v4.new_markdown_cell(THEOREM, id="proof-theorem"),
    nbf.v4.new_markdown_cell(OUTLINE, id="proof-outline"),
]
start = next(
    i for i, c in enumerate(nb.cells) if c.id in ("b5-placeholder", "b5-heading")
)
nb.cells[start:] = [
    nbf.v4.new_markdown_cell(
        "## Exact Lyapunov theorem and identities\nThe preceding numerical work identifies the candidate. This section establishes it over the full stated domain.",
        id="b5-heading",
    ),
    nbf.v4.new_code_cell(LOAD, id="b5-load"),
    nbf.v4.new_markdown_cell(FORMULA, id="b5-formula"),
    nbf.v4.new_code_cell(HELPERS, id="b5-symbolic-tools"),
    nbf.v4.new_markdown_cell(
        "## Symbolic Step Recursion Verification", id="b5-step-heading"
    ),
    nbf.v4.new_markdown_cell(
        r"For $0\le k\le N-2$, with $a=\theta_{k}$ and $b=\theta_{k+1}$ satisfying $a^{2}=b^{2}-b$, verify $$U_{k+1}-U_{k}=2bI_{\star,k+1}+2a^{2}I_{k,k+1}.$$ The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero. Here the independent vector $z_{k+1}$ and the recurrence define $x_{k+1}$ and $z_{k+2}$.",
        id="b5-step-equation",
    ),
    nbf.v4.new_code_cell(STEP, id="b5-step"),
    nbf.v4.new_markdown_cell(
        "## Base Case and Boundary Symbolic Verification", id="b5-base-heading"
    ),
    nbf.v4.new_markdown_cell(
        r"With $z_{0}=x_{0}$ and $\theta_{0}=1$, verify $$U_{0}-\frac L2\|x_{0}-x_{\star}\|^{2}=2I_{\star,0}.$$ The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero; $I_{\star,0}\le0$ gives the required initial upper bound.",
        id="b5-base-equation",
    ),
    nbf.v4.new_code_cell(BASE, id="b5-base"),
    nbf.v4.new_markdown_cell(
        "### Terminal Transition Symbolic Verification", id="b5-terminal-heading"
    ),
    nbf.v4.new_markdown_cell(
        r"Set $a=\theta_{N-1}$ and $T=\theta_{N}$, so $2a^{2}=T^{2}-T$. Verify $$U_{N}-U_{N-1}=T I_{\star,N}+2a^{2}I_{N-1,N}.$$ The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero. This separate calculation preserves the special terminal recurrence.",
        id="b5-terminal-equation",
    ),
    nbf.v4.new_code_cell(TERMINAL, id="b5-terminal"),
    nbf.v4.new_markdown_cell(
        "### Boundary Identity Symbolic Verification", id="b5-boundary-heading"
    ),
    nbf.v4.new_markdown_cell(
        r"For $\tau=L/(2T^{2})$, verify $$f(x_{N})-f(x_{\star})-\tau R^{2}=V_{N}-\tau\|q_{N}\|^{2}+\tau(\|d_{0}\|^{2}-R^{2}).$$ The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero in Gram, function, and constant coordinates. Every term on the right is nonpositive under the proved decrease and the initial condition.",
        id="b5-boundary-equation",
    ),
    nbf.v4.new_code_cell(BOUNDARY, id="b5-boundary"),
    nbf.v4.new_markdown_cell("### One-step horizon", id="b5-small-heading"),
    nbf.v4.new_markdown_cell(
        r"At $N=1$, $T=2$ and $x_{1}=x_{0}-3g_{0}/(2L)$. Verify $$V_{1}=\tfrac12(I_{\star,0}+I_{\star,1}+I_{0,1}).$$ The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero; no nonexistent interior step is invoked.",
        id="b5-small-equation",
    ),
    nbf.v4.new_code_cell(SMALL, id="b5-small"),
    nbf.v4.new_markdown_cell(DOMAIN, id="b5-domain"),
    nbf.v4.new_code_cell(
        SIGNS
        + '\nprint("B5_EXACT_RESULTS="+json.dumps(proof_results,sort_keys=True))\n',
        id="b5-signs",
    ),
]
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert not any(
            char in cell.source for char in ["\x0c", "\r", "\\(", "\\)", "\\[", "\\]"]
        )
nbf.write(nb, path)
print("Authored", path)
