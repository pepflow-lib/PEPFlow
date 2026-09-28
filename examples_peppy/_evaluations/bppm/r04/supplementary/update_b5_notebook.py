import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import runtime

root = runtime.ATTEMPT
path = root / "bppm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell


def source(name):
    return (root / "supplementary" / name).read_text(encoding="utf-8-sig")


proof = [
    md("## Proof Statement"),
    md(r"""### Theorem
Under the stated assumptions, for every integer $N\ge1$, define
$$V_{k}=\frac{D_h(x_{\star},x_{k})-D_h(x_{\star},x_{0})}{\alpha N}+\frac{k}{N}\bigl(f(x_{k})-f(x_{\star})\bigr),\qquad 0\le k\le N.$$
Then $V_{0}=0$ and $V_{k+1}\le V_{k}$. In particular,
$$0\le f(x_{N})-f(x_{\star})\le\frac{R}{\alpha N}.$$
The formula applies at both endpoints and for $N=1$ and $R=0$. An equivalent conventional potential is $\Phi_{k}=\alpha k(f(x_{k})-f(x_{\star}))+D_h(x_{\star},x_{k})$; it is nonincreasing and $\Phi_{0}\le R$."""),
    md(r"""### Proof outline
Use the explicit certificate
$$V_{k}=\frac{D_h(x_{\star},x_{k})-D_h(x_{\star},x_{0})}{\alpha N}+\frac{k}{N}(f(x_{k})-f(x_{\star})).$$
For $q=f,h$, set
$$r^q_{i,j}=q(x_{j})-q(x_{i})+\langle\nabla q(x_{j}),x_{i}-x_{j}\rangle\le0.$$
The exact proximal optimality equation is $\nabla h(x_{k+1})=\nabla h(x_{k})-\alpha\nabla f(x_{k+1})$. Substitution yields, for $0\le k<N$,
$$V_{k+1}-V_{k}=\frac{r^f_{\star,k+1}}{N}+\frac{k}{N}r^f_{k,k+1}+\frac{k+1}{\alpha N}r^h_{k+1,k}+\frac{k}{\alpha N}r^h_{k,k+1}\le0.$$
Every multiplier is nonnegative because $k\ge0$, $N\ge1$, and $\alpha>0$. At the first step the two factors $k$ vanish, so the same statement has a separately verified base case. Since $V_{0}=0$, telescoping gives $V_{N}\le0$.
Finally,
$$f(x_{N})-f(x_{\star})-\frac{R}{\alpha N}=V_{N}+\frac{D_h(x_{\star},x_{0})-R}{\alpha N}+\frac{r^h_{\star,N}}{\alpha N}\le0.$$
This uses exactly the given radius $R$. Convexity and minimality of $x_{\star}$ give the lower bound. The executable symbolic checks below verify these identities over symbolic parameters and indices, not only the numerical discovery horizons."""),
]
nb.cells[1:2] = proof
# Add actual S and closed-form comparison matrices to the existing diagnostic trail.
for c in nb.cells:
    if (
        c.cell_type == "code"
        and "Numerical S decomposition: full eigenbasis" in c.source
    ):
        c.source += '\nprint("Actual selected numerical S:")\npf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(b2["S_matrix"]),b2["S_row_names"],b2["S_col_names"]))'
    if c.cell_type == "code" and c.source.startswith("def coeff_pattern("):
        c.source += '\nfor k in range(1,N_int+1):\n    exact_C=coeff_pattern(k,N_int,float(params_sp["alpha"]))\n    print(f"k={k}: closed-form candidate matrix and difference from extracted matrix")\n    pf.pprint_labeled_matrix(pf.MatrixWithNames(exact_C,V_k_basis_labels(k),V_k_basis_labels(k)))\n    pf.pprint_labeled_matrix(pf.MatrixWithNames(coeff_by_k[k]-exact_C,V_k_basis_labels(k),V_k_basis_labels(k)))'
new = [
    md(
        "## Closed form and exact identities\nThe numerical candidate is now verified exactly. The auxiliary contexts below encode the actual proximal recurrence with symbolic $k,N,\\alpha,R$. Their separate tags prevent collisions with the discovery context."
    ),
    code(source("b5_initialize.py")),
    md("## Symbolic Step Recursion Verification"),
    md(r"""Verify, for $0\le k<N$,
$$V_{k+1}-V_{k}=\frac{r^f_{\star,k+1}}{N}+\frac{k}{N}r^f_{k,k+1}+\frac{k+1}{\alpha N}r^h_{k+1,k}+\frac{k}{\alpha N}r^h_{k,k+1}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in every coordinate. Also verify that the ordered quadratic and function-value representation from Block 4 equals this $V_{k}$ exactly."""),
    code(source("b5_step.py")),
    md("## Base Case and Boundary Symbolic Verification"),
    md(r"""Verify $V_{0}=0$ and the actual first-step identity
$$V_{1}-V_{0}=\frac{r^f_{\star,1}}{N}+\frac{r^h_{1,0}}{\alpha N}.$$
Also verify initial normalization with $W_{0}=D_h(x_{\star},x_{0})/(\alpha N)$:
$$W_{0}-\frac{R}{\alpha N}=\frac{D_h(x_{\star},x_{0})-R}{\alpha N}.$$
Each residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. These identities include $N=1$ without using an interior formula outside its domain."""),
    code(source("b5_base.py")),
    md("### Boundary Identity Symbolic Verification"),
    md(r"""Verify the terminal identity
$$f(x_{N})-f(x_{\star})-\frac{R}{\alpha N}=V_{N}+\frac{D_h(x_{\star},x_{0})-R}{\alpha N}+\frac{r^h_{\star,N}}{\alpha N}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. Since $r^h_{\star,N}=-D_h(x_{\star},x_{N})\le0$, the boundary contribution has the correct sign."""),
    code(source("b5_boundary.py")),
    md(
        "### Signs, domains, and telescoping conclusion\nThe coefficients are nonnegative for integer $0\\le k<N$, integer $N\\ge1$, and $\\alpha>0$. Every convex residual is nonpositive and the initial residual is nonpositive by assumption. Thus all terms on the terminal identity’s right-hand side are nonpositive. No positive lower bound on the kernel’s curvature is used; $R=0$ is allowed."
    ),
    code(source("b5_signs.py")),
    md(r"""The exact local Lyapunov proof is complete. Numerical full-PEP certificates are verified separately. A separate global symbolic lambda/S proof was not asserted; the global formulas remain numerically supported discovery candidates. The completed theorem follows from the exact local step, base, and terminal identities above.

The certificate in conventional form is
$$\Phi_{k}=\alpha k\bigl(f(x_{k})-f(x_{\star})\bigr)+D_h(x_{\star},x_{k}),\qquad \Phi_{k+1}\le\Phi_{k},$$
so $\alpha N(f(x_{N})-f(x_{\star}))\le\Phi_{N}\le\Phi_{0}\le R$."""),
]
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Closed form")
)
nb.cells[start:] = new
nbf.write(nb, path)
print(
    "Final notebook source prepared; static checks precede final nbconvert execution."
)
