import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import re

# optional notebook-generation dependency
import nbformat as nb  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

root = runtime.ROOT
path = root / "bppm_example_lyap.ipynb"
book = nb.read(path, as_version=4)
md, code = nb.v4.new_markdown_cell, nb.v4.new_code_cell
read = lambda name: (root / f"supplementary/b5_{name}.py").read_text(  # noqa: E731 - retain the archived notebook helper
    encoding="utf-8-sig"
)
book.cells[0].source = book.cells[0].source.replace(
    "this is not yet a proved theorem.", "the theorem below proves this bound."
)
book.cells[
    11
].source += '\nfor label,saved in (("dense",dense),("selected",b2)):\n    for owner in ("f","h"):\n        point_labels=sorted({tag for name in saved["named_dual_values"] if name.startswith(owner+":") for tag in name.split(":")[1].split(",")})\n        dual_matrix=np.array([[saved["named_dual_values"].get(f"{owner}:{row},{col}") or 0.0 for col in point_labels] for row in point_labels])\n        print(label,owner,"multiplier display; relaxed entries displayed as zero")\n        pf.pprint_labeled_matrix(dual_matrix,point_labels)'
book.cells[
    16
].source += '\nprint("True selected S matrix")\npf.pprint_labeled_matrix(S_array,b2["basis_vectors"],precision=12)'
book.cells[
    33
].source += '\nfor k in range(1,N_int+1):\n    print(f"Closed-form coefficient candidate k={k}")\n    pf.pprint_labeled_matrix(coeff_pattern(k,N_int,params_sp["alpha"]),V_k_basis_labels(k))'
closing = [
    md(r"""## Closed-form conclusion
The exact candidate is
$$V_{0}=0,\qquad V_{k}=\frac{k}{N}(f(x_{k})-f(x_{\star}))+\frac{D_h(x_{\star},x_{k})-D_h(x_{\star},x_{0})}{\alpha N},\quad 1\leq k\leq N.$$
The next cells derive local multipliers from the full symbolic coordinate equations and verify the step, base and boundary identities. Their exact identities establish the formula beyond the numerical samples. The global numerical full-PEP certificate remains separately classified; no separate global analytic lambda/S claim is needed."""),
    code(
        'b4 = json.loads((notebook_dir / "state/bppm_b4.json").read_text())\nassert b4["certificate_id"] == certificate["certificate_id"]\nassert b4["numerical_reconstruction"]["certificate_id"] == certificate["certificate_id"]\nprint("Block 4 structure and selected certificate agree.")'
    ),
    code(read("common")),
    md("## Symbolic Step Recursion Verification"),
    md(r"""For $1\leq k<N$, let $Q^f_{u,v}=f(v)-f(u)+\langle\nabla f(v),u-v\rangle$ and define $Q^h$ likewise. Verify
$$V_{k+1}-V_{k}=\frac{Q^f_{\star,k+1}}{N}+\frac{kQ^f_{k,k+1}}{N}+\frac{(k+1)Q^h_{k+1,k}}{\alpha N}+\frac{kQ^h_{k,k+1}}{\alpha N}.$$
The exact residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish. We first solve for all four multipliers from every coordinate, using the actual relation $\nabla h(x_{k+1})=\nabla h(x_k)-\alpha\nabla f(x_{k+1})$."""),
    code(read("step")),
    md("## Base Case and Boundary Symbolic Verification"),
    md(r"""Build an independent first-step context. With $V_{0}=0$, verify
$$V_{1}-V_{0}=\frac{Q^f_{\star,1}}{N}+\frac{Q^h_{1,0}}{\alpha N}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in every coordinate. This avoids evaluating $f(x_0)$ with a nominal zero coefficient and applies also when $N=1$."""),
    code(read("base")),
    md("### Boundary Identity Symbolic Verification"),
    md(r"""In a separate symbolic terminal context, verify
$$f(x_N)-f(x_{\star})-\frac{R}{\alpha N}=V_N+\frac{D_h(x_{\star},x_0)-R+Q^h_{\star,N}}{\alpha N}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish, including the radius constant. Convexity gives $Q^h_{\star,N}=-D_h(x_{\star},x_N)\leq0$."""),
    code(read("boundary")),
    md(r"""### Signs, domain and telescoping
Each $Q^f,Q^h$ is nonpositive by convexity. For integer $N\geq1$, $\alpha>0$ and $k\geq0$, the four local multipliers $1/N$, $k/N$, $(k+1)/(\alpha N)$ and $k/(\alpha N)$ are nonnegative. Thus the separate base gives $V_1\leq0$, and the step identity gives $V_{k+1}\leq V_k$ for $1\leq k<N$. Hence $V_N\leq V_0=0$.
The initial bound $D_h(x_{\star},x_0)-R\leq0$, terminal convexity residual, and positive denominator $\alpha N$ make the boundary identity's right side nonpositive. Therefore
$$f(x_N)-f(x_{\star})\leq\frac{R}{\alpha N}.$$
For $N=1$, only the separately verified base and boundary are required. $R=0$ is permitted because no step divides by $R$. The equivalent nonnegative energy is $W_k=\alpha k(f(x_k)-f(x_{\star}))+D_h(x_{\star},x_k)$ for $k\geq1$, with $W_0=D_h(x_{\star},x_0)$; it satisfies $W_k=\alpha N V_k+W_0$.
The numerical full-PEP certificate and the exact local Lyapunov proof are verified separately. The latter is complete; a separate global analytic full-PEP formula is not claimed."""),
]
book.cells[36:37] = closing
proof = [
    md("## Proof Statement"),
    md(r"""### Theorem
Let $f,h$ satisfy the stated closedness, properness, convexity and differentiability assumptions, and let $x_{\star}$ minimize $f$. For $\alpha>0$, $R\geq0$ and integer $N\geq1$, suppose $D_h(x_{\star},x_0)\leq R$ and all exact updates
$$x_{k+1}\in\operatorname*{argmin}_{x}\{\alpha f(x)+D_h(x,x_k)\},\qquad k=0,\ldots,N-1,$$
are well-defined. The sequence
$$V_0=0,\qquad V_k=\frac{k}{N}(f(x_k)-f(x_{\star}))+\frac{D_h(x_{\star},x_k)-D_h(x_{\star},x_0)}{\alpha N},\quad 1\leq k\leq N,$$
is nonincreasing. In particular,
$$f(x_N)-f(x_{\star})\leq\frac{R}{\alpha N}.$$
The terminal index uses the same formula. No strong convexity of $h$ is assumed."""),
    md(r"""### Proof outline
Write $D_k=D_h(x_{\star},x_k)$ and $Q^f_{u,v}=f(v)-f(u)+\langle\nabla f(v),u-v\rangle\leq0$, with $Q^h$ defined analogously. The proximal optimality relation is $\nabla h(x_{k+1})=\nabla h(x_k)-\alpha\nabla f(x_{k+1})$.
For $V_k=(k/N)(f(x_k)-f(x_{\star}))+(D_k-D_0)/(\alpha N)$, direct substitution gives, for $1\leq k<N$,
$$V_{k+1}-V_k=\frac{Q^f_{\star,k+1}}{N}+\frac{kQ^f_{k,k+1}}{N}+\frac{(k+1)Q^h_{k+1,k}}{\alpha N}+\frac{kQ^h_{k,k+1}}{\alpha N}\leq0.$$
The first step satisfies
$$V_1-V_0=\frac{Q^f_{\star,1}}{N}+\frac{Q^h_{1,0}}{\alpha N}\leq0,\qquad V_0=0.$$
All multipliers are nonnegative; there are no omitted slack or square terms. Telescoping yields $V_N\leq0$. Finally,
$$f(x_N)-f(x_{\star})-\frac{R}{\alpha N}=V_N+\frac{D_0-R+Q^h_{\star,N}}{\alpha N}\leq0,$$
because $D_0\leq R$ and $Q^h_{\star,N}=-D_N\leq0$. This proves the bound, including $N=1$ and $R=0$."""),
]
book.cells[1:2] = proof
# Mechanical normalization of single-symbol subscripts in Markdown only.
for cell in book.cells:
    if cell.cell_type == "markdown":
        cell.source = re.sub(r"_([A-Za-z0-9])(?![A-Za-z0-9])", r"_{\1}", cell.source)
nb.write(book, path)
print(
    "Final notebook sources saved; static checks must precede final clean-kernel execution."
)
