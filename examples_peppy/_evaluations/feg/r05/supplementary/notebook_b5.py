import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "runtime", Path(__file__).parent / "helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import nbformat as nbf  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup

root = runtime.ROOT
path = root / "feg_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
source = (root / "supplementary/helpers/b5_math.py").read_text(encoding="utf-8-sig")
markers = [
    "LOAD",
    "HELPERS",
    "DERIVATION",
    "NORMALIZED_COEFFICIENTS",
    "STEP",
    "BASE",
    "BOUNDARY",
    "SIGNS",
]
parts = {}
for i, label in enumerate(markers):
    start = source.index("# " + label) + len("# " + label)
    end = source.index("# " + markers[i + 1]) if i + 1 < len(markers) else len(source)
    parts[label] = source[start:end].strip()
for line in [
    "import json",
    "import sympy as sp",
    "import pepflow as pf",
    "import numpy as np",
    "import runtime",
]:
    parts["LOAD"] = parts["LOAD"].replace(line + "\n", "")
proof = [
    nbf.v4.new_markdown_cell("## Proof Statement"),
    nbf.v4.new_markdown_cell(r"""### Theorem
Under the assumptions and updates above, for every integer $N\ge1$,
$$\boxed{\|A(x_{N})\|^2\le\frac{4L^2R^2}{N^2}.}$$
A nonincreasing Lyapunov certificate is
$$\boxed{V_{0}=0,\qquad V_{k}=k^2\|A(x_{k})\|^2+2kL\langle A(x_{k}),x_{k}-x_{0}\rangle\quad(1\le k\le N).}$$
The potential need not be nonnegative; the terminal square identity below converts $V_{N}\le0$ into the residual bound. This exact potential is a positive rescaling of the structure discovered numerically. No matching closed-form formula for the particular floating-point full-PEP dual is claimed."""),
    nbf.v4.new_markdown_cell(r"""### Proof outline
Write $g_{k}=A(x_{k})$ and define the nonpositive residuals
$$\operatorname{Lip}(u,v)=\|A(u)-A(v)\|^2-L^2\|u-v\|^2,\qquad
\operatorname{Mon}(u,v)=-\langle A(u)-A(v),u-v\rangle.$$
For $V_{k}=k^2\|g_{k}\|^2+2kL\langle g_{k},x_{k}-x_{0}\rangle$, the shared point $x_{1/2}=x_{0}$ and $x_{1}=x_{0}-g_{0}/L$ give
$$V_{1}-V_{0}=\operatorname{Lip}(x_{0},x_{1})\le0.$$
For $1\le k<N$, substitution of both updates gives the exact identity
$$V_{k+1}-V_{k}=(k+1)^2\operatorname{Lip}(x_{k+1/2},x_{k+1})+2k(k+1)L\operatorname{Mon}(x_{k},x_{k+1})\le0.$$
The multipliers are nonnegative because $L>0$ and $k\ge1$. Thus $V_{N}\le V_{1}\le0$.
Let $d=x_{0}-x_{\star}$ and use $A(x_{\star})=0$. The terminal identity is
$$N^2\|g_{N}\|^2-4L^2\|d\|^2
=2V_{N}+4NL\operatorname{Mon}(x_{N},x_{\star})-\|Ng_{N}-2Ld\|^2\le0.$$
Both additional terms on the right are nonpositive. Consequently
$$\|g_{N}\|^2\le\frac{4L^2\|d\|^2}{N^2}\le\frac{4L^2R^2}{N^2}.$$
For $N=1$ the recursion range is empty and the base and terminal identities suffice. The proof never divides by $R$, so it also covers $R=0$."""),
]
nb.cells[1:2] = proof
# Mark earlier uncertainty as historical discovery evidence.
for cell in nb.cells:
    if cell.cell_type == "markdown":
        cell.source = cell.source.replace(
            "No all-horizon proof is claimed yet.",
            "This was the B1 conjecture; the exact proof is now given above and verified below.",
        )
        cell.source = cell.source.replace(
            "All three exact coefficient functions remain unknown at this handoff;",
            "At the B4 handoff, all three exact coefficient functions were unknown;",
        )
    elif "LDL diagonal:" in cell.source:
        cell.source += '\npf.pprint_labeled_matrix(np.asarray(b2["S_matrix"]), b2["basis_vectors"], b2["basis_vectors"], precision=6)\n'
start = next(
    i for i, c in enumerate(nb.cells) if c.source.startswith("## Closed-form Lyapunov")
)
nb.cells[start:] = [
    nbf.v4.new_markdown_cell(
        "## Closed-form coefficient derivation\nStart from the verified B4 basis and solve for all three quadratic coefficients and both local residual multipliers. The derivation uses a symbolic PEPFlow context with the actual two updates."
    ),
    nbf.v4.new_code_cell(parts["LOAD"]),
    nbf.v4.new_code_cell(parts["HELPERS"]),
    nbf.v4.new_code_cell(parts["DERIVATION"]),
    nbf.v4.new_markdown_cell(r"""The coefficient equations imply
$$c_{qq}(k)=0,\qquad c_{gq}(k)=\frac{L}{k}c_{gg}(k),\qquad
\frac{c_{gg}(k+1)}{(k+1)^2}=\frac{c_{gg}(k)}{k^2}.$$
Choose the free positive normalization $c_{gg}(1)=1$. Induction gives
$$C(k)=\begin{pmatrix}k^2&kL\\kL&0\end{pmatrix}.$$
The numerical certificate has a slightly different positive scale. The following comparison divides each numerical coefficient matrix by its first-step $c_{gg}$; no certificate entries are replaced."""),
    nbf.v4.new_code_cell(parts["NORMALIZED_COEFFICIENTS"]),
    nbf.v4.new_markdown_cell(r"""### Closed-form Lyapunov conclusion
The exact potential is
$$V_{0}=0,\qquad V_{k}=k^2\|A(x_{k})\|^2+2kL\langle A(x_{k}),x_{k}-x_{0}\rangle\quad(1\le k\le N).$$
There are no function-value or offset terms. We next verify the decrease, initial step, and terminal normalization symbolically, over the complete stated domain."""),
    nbf.v4.new_markdown_cell("## Symbolic Step Recursion Verification"),
    nbf.v4.new_markdown_cell(r"""For $1\le k<N$ and $L>0$, verify
$$V_{k+1}-V_{k}=(k+1)^2\operatorname{Lip}(x_{k+1/2},x_{k+1})+2k(k+1)L\operatorname{Mon}(x_{k},x_{k+1}).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero in every scalar component."""),
    nbf.v4.new_code_cell(parts["STEP"]),
    nbf.v4.new_markdown_cell("## Base Case and Boundary Symbolic Verification"),
    nbf.v4.new_markdown_cell(r"""With $x_{1/2}=x_{0}$ and $x_{1}=x_{0}-A(x_{0})/L$, verify
$$V_{1}-V_{0}=\operatorname{Lip}(x_{0},x_{1}),\qquad V_{0}=0.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero. Lipschitz continuity then yields $V_{1}\le0$."""),
    nbf.v4.new_code_cell(parts["BASE"]),
    nbf.v4.new_markdown_cell("### Boundary Identity Symbolic Verification"),
    nbf.v4.new_markdown_cell(r"""For $N\ge1$, $L>0$, $d=x_{0}-x_{\star}$ and $A(x_{\star})=0$, verify
$$N^2\|A(x_{N})\|^2-4L^2\|d\|^2
=2V_{N}+4NL\operatorname{Mon}(x_{N},x_{\star})-\|NA(x_{N})-2Ld\|^2.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero in every scalar component."""),
    nbf.v4.new_code_cell(parts["BOUNDARY"]),
    nbf.v4.new_markdown_cell(r"""### Signs, domain, and normalization
For integer $k\ge1$, $N\ge1$ and $L>0$, the multipliers $(k+1)^2$, $2k(k+1)L$, and $4NL$ are positive. The square norm is nonnegative. All divisions use only $k$, $k+1$, $N$ or $L$, which are nonzero on their respective domains. Monotonicity, Lipschitz continuity, and $V_{N}\le0$ therefore make the terminal right-hand side nonpositive. Using $\|x_{0}-x_{\star}\|^2\le R^2$ proves the stated rate. No additional condition on $R\ge0$ is needed."""),
    nbf.v4.new_code_cell(parts["SIGNS"]),
    nbf.v4.new_code_cell("""print("V_k = k^2 ||A(x_k)||^2 + 2 k L <A(x_k), x_k-x_0>; V_0=0")
print(r"\\|A(x_N)\\|^2 \\le \\frac{4L^2R^2}{N^2},\\qquad N\\ge1.")
print("Numerical certificate verified: True; analytic full-PEP formula verified: False; analytic Lyapunov proof verified:", all(proof_checks.values()))"""),
]
nbf.write(nb, path)
print(
    "Final notebook source written; static checks must precede clean-kernel final execution."
)
