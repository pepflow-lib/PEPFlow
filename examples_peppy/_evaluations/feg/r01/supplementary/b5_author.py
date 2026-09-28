"""Finalize proof exposition and visible symbolic calculations before gates."""
from pathlib import Path
import nbformat as nbf

root=Path.cwd()
path=root / "feg_example_lyap.ipynb"
nb=nbf.read(path,as_version=4)
source=(root / "supplementary/b5_symbolic.py").read_text()
def block(label):
    return source.split(f"# BEGIN {label}\n")[1].split(f"# END {label}")[0]

theorem=r"""### Theorem
Let $A$ be monotone and $L$-Lipschitz in a real finite-dimensional Euclidean space, with $L>0$, $A(x_{\star})=0$, and $\|x_{0}-x_{\star}\|\le R$ for $R\ge0$. For integer $N\ge1$, use
$$x_{k+1/2}=x_{k}+\frac{x_{0}-x_{k}}{k+1}-\frac{k}{(k+1)L}A(x_{k}),\qquad
x_{k+1}=x_{k}+\frac{x_{0}-x_{k}}{k+1}-\frac1L A(x_{k+1/2}),$$
for $0\le k<N$, with $x_{1/2}=x_{0}$.
Define the normalized potential
$$V_{0}=0,\qquad V_{k}=\frac{2k^{2}}{N^{2}}\|A(x_{k})\|^{2}
+\frac{4kL}{N^{2}}\langle A(x_{k}),x_{k}-x_{0}\rangle,\quad 1\le k\le N.$$
Then $V_{k+1}\le V_{k}$, and
$$\boxed{\|A(x_{N})\|^{2}\le\frac{4L^{2}R^{2}}{N^{2}}.}$$
The potential need not be nonnegative. Its terminal identity, rather than positivity, supplies the residual bound. The result covers $N=1$ and $R=0$."""
outline=r"""### Proof outline
Set $g_{k}=A(x_{k})$, $d=x_{0}-x_{\star}$, and define nonpositive residuals
$$\operatorname{Mon}(u,v)=-\langle A(u)-A(v),u-v\rangle,\qquad
\operatorname{Lip}(u,v)=\|A(u)-A(v)\|^{2}-L^{2}\|u-v\|^{2}.$$
For $V_{k}=2k^{2}\|g_{k}\|^{2}/N^{2}+4kL\langle g_{k},x_{k}-x_{0}\rangle/N^{2}$ and $V_{0}=0$, the shared initial half-step gives
$$V_{1}-V_{0}=\frac{2}{N^{2}}\operatorname{Lip}(x_{1},x_{0})\le0.$$
For every $1\le k<N$, substitution of both updates gives the exact identity
$$V_{k+1}-V_{k}=\frac{4Lk(k+1)}{N^{2}}\operatorname{Mon}(x_{k},x_{k+1})
+\frac{2(k+1)^{2}}{N^{2}}\operatorname{Lip}(x_{k+1},x_{k+1/2})\le0.$$
There are no other local residual or square terms. All multipliers are positive on the stated domain, so $V_{N}\le V_{0}=0$.
The terminal completion of the square is
$$\|g_{N}\|^{2}-\frac{4L^{2}R^{2}}{N^{2}}
=V_{N}+\frac{4L^{2}}{N^{2}}(\|d\|^{2}-R^{2})
+\frac{4L}{N}\operatorname{Mon}(x_{N},x_{\star})
-\left\|g_{N}-\frac{2L}{N}d\right\|^{2}.$$
Every term on the right is nonpositive: use the initial radius bound, monotonicity with $A(x_{\star})=0$, and nonnegativity of a squared norm. This proves the claimed rate. For $N=1$ the interior telescoping sum is empty; the base and terminal identities still apply. No division by $R$ or $\|g_{N}\|$ is needed."""
proof_cells=[nbf.v4.new_markdown_cell("## Proof Statement"),nbf.v4.new_markdown_cell(theorem),nbf.v4.new_markdown_cell(outline)]
for i,c in enumerate(proof_cells):
    c.id=f"proof-{i:02d}"
start=next(i for i,c in enumerate(nb.cells) if c.id in ("b1-01","proof-00"))
end=next(i for i,c in enumerate(nb.cells) if c.id=="b1-02")
nb.cells[start:end]=proof_cells
for c in nb.cells:
    if c.id=="b2-06" and "True saved S" not in c.source:
        c.source+='\nprint("True saved S, not the rejected analytic guess:")\npf.pprint_labeled_matrix(S_array,b2["basis_vectors"],precision=7)'
    if c.id=="b2-02" and "Active certificate weights" not in c.source:
        c.source+='\nactive_names=[name for name,value in b2["named_dual_values"].items() if value is not None]\nprint("Active certificate weights:")\npf.pprint_labeled_matrix(np.asarray([[b2["named_dual_values"][name]] for name in active_names]),active_names,["numerical dual"],precision=8)'
    if c.id=="b4-11":
        c.source=c.source.replace("The coefficient functions are explicitly unresolved; B5 must derive them", "At the B4 handoff the coefficient functions were unresolved; the next section derives them").replace("No analytic proof is claimed here.","This section records the numerical discovery stage.")

coefficient_code='''def coeff_pattern(k, n, ell):
    if k == 0:
        return sp.zeros(0, 0)
    return sp.Matrix([[2*sp.S(k)**2/sp.S(n)**2, 2*sp.S(k)*ell/sp.S(n)**2],
                      [2*sp.S(k)*ell/sp.S(n)**2, 0]])

numeric_scale = float(coeff_by_k[1][0,0])*N_int**2/2
print("Positive sample scale relative to the analytic normalization:",numeric_scale)
assert numeric_scale > 0
for index in range(1,N_int+1):
    exact_C = coeff_pattern(index,N_int,sp.S(1))
    raw_error = np.max(np.abs(coeff_by_k[index]-np.asarray(exact_C,float)))
    scale_adjusted_error = np.max(np.abs(coeff_by_k[index]/numeric_scale-np.asarray(exact_C,float)))
    print(f"k={index}: raw difference {raw_error:.3g}; after common positive scale {scale_adjusted_error:.3g}")
    assert scale_adjusted_error <= 1e-5
    pf.pprint_labeled_matrix(np.asarray(exact_C,dtype=object),V_k_basis_labels(index),V_k_basis_labels(index))
'''
cells=[
    nbf.v4.new_markdown_cell("## Block 5: exact coefficient derivation\nThe B4 sample is retained as numerical evidence. The symbolic ansatz uses its basis and leaves all three symmetric coefficients and both local multipliers unknown. We solve the recurrence identities exactly rather than rounding the numerical certificate."),
    nbf.v4.new_code_cell('from typing import Any\nb4=json.loads((notebook_dir / "state/feg_b4.json").read_text())\nassert b4["certificate_id"] == b3["certificate_id"]\nassert b4["numerical_reconstruction"]["required_indices"] == list(range(N_int+1))\nprint("Basis:",b4["basis_templates"])\nprint("Unknown coefficient roles:",b4["unresolved_coefficients"])\n'+block("SYMBOLIC HELPERS")),
    nbf.v4.new_markdown_cell(r"""### Symbolic recursion context and coefficient equations
Let $V_{k}=a_{k}\|g_{k}\|^{2}+2b_{k}\langle g_{k},x_{k}-x_{0}\rangle+c_{k}\|x_{k}-x_{0}\|^{2}$. We require
$$V_{k+1}-V_{k}=\lambda_{k}\operatorname{Mon}(x_{k},x_{k+1})+\mu_{k}\operatorname{Lip}(x_{k+1},x_{k+1/2}).$$
The next cell constructs the actual two updates with symbolic $k,L,N$, extracts every Gram/function/offset equation, and solves jointly for the coefficients and multipliers."""),
    nbf.v4.new_code_cell(block("DERIVATION")),
    nbf.v4.new_markdown_cell(r"""### Resolved recurrence and normalization
The equations give
$$a_{k+1}=a_{k}\frac{(k+1)^{2}}{k^{2}},\quad b_{k}=\frac{La_{k}}{k},\quad c_{k}=0,\quad
\lambda_{k}=\frac{2La_{k}(k+1)}{k},\quad\mu_{k}=a_{k}\frac{(k+1)^{2}}{k^{2}}.$$
Thus $a_{k}=\gamma k^{2}$ for a constant positive scale $\gamma$. We choose $\gamma=2/N^{2}$; the base and terminal identities below verify that this normalization yields the claimed performance bound, so a homogeneous zero solution is not being used.

The selected floating-point certificate has a slightly different common scale. We report raw differences honestly and also check the scale-invariant numerical pattern. This does not replace or change any saved multipliers or $S$. The exact proof concerns the newly derived normalized potential."""),
    nbf.v4.new_code_cell(coefficient_code),
    nbf.v4.new_markdown_cell(r"""### Closed-form Lyapunov function
The derived analytic potential is
$$V_{0}=0,\qquad V_{k}=\frac{2k^{2}}{N^{2}}\|A(x_{k})\|^{2}+\frac{4kL}{N^{2}}\langle A(x_{k}),x_{k}-x_{0}\rangle\quad(1\le k\le N).$$
There are no function-value, scalar-offset, or additional terminal-basis terms. We now verify this potential's exact one-step identity and its separate base and terminal cases."""),
    nbf.v4.new_markdown_cell("## Symbolic Step Recursion Verification"),
    nbf.v4.new_markdown_cell(r"""For $1\le k<N$, verify
$$V_{k+1}-V_{k}=\frac{4Lk(k+1)}{N^{2}}\operatorname{Mon}(x_{k},x_{k+1})+\frac{2(k+1)^{2}}{N^{2}}\operatorname{Lip}(x_{k+1},x_{k+1/2}).$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in every scalar component."""),
    nbf.v4.new_code_cell(block("STEP")),
    nbf.v4.new_markdown_cell("## Base Case and Boundary Symbolic Verification"),
    nbf.v4.new_markdown_cell(r"""Use the actual initial update $x_{1}=x_{0}-A(x_{0})/L$ and shared point $x_{1/2}=x_{0}$ to verify
$$V_{1}-V_{0}=\frac{2}{N^{2}}\operatorname{Lip}(x_{1},x_{0}),\qquad V_{0}=0.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. The positive multiplier and Lipschitz condition imply $V_{1}\le0$. This verification applies to every $N\ge1$."""),
    nbf.v4.new_code_cell(block("BASE")),
    nbf.v4.new_markdown_cell("### Boundary Identity Symbolic Verification"),
    nbf.v4.new_markdown_cell(r"""With $d=x_{0}-x_{\star}$, verify
$$\|A(x_{N})\|^{2}-\frac{4L^{2}R^{2}}{N^{2}}
=V_{N}+\frac{4L^{2}}{N^{2}}(\|d\|^{2}-R^{2})+\frac{4L}{N}\operatorname{Mon}(x_{N},x_{\star})
-\left\|A(x_{N})-\frac{2L}{N}d\right\|^{2}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish, including the constant involving $R^{2}$."""),
    nbf.v4.new_code_cell(block("BOUNDARY")),
    nbf.v4.new_markdown_cell("### Signs, domain, and conclusion\nFor integer $N\ge1$, $1\le k<N$, and $L>0$, all displayed multipliers are positive and every denominator is nonzero. Monotonicity and Lipschitz continuity make the residuals nonpositive, while the terminal squared norm is nonnegative. Hence the potential decreases from zero, and the terminal identity proves the stated residual bound. The proof uses no nonnegativity assumption on the potential, no division by $R$, and no finite-horizon interpolation claim beyond the given inequalities. The local analytic Lyapunov proof is complete; the earlier global numerical certificate remains a distinct object with unresolved analytic formulas."),
    nbf.v4.new_code_cell(block("SIGNS")+'\nassert step_verified and base_verified and boundary_verified\nprint("Exact local Lyapunov theorem verified; global numerical-certificate formula status remains separate.")'),
]
for i,c in enumerate(cells):
    c.id=f"b5-{i:02d}"
start=next(i for i,c in enumerate(nb.cells) if c.id in ("b1-10","b5-00"))
nb.cells[start:]=cells
markdown="\n".join(c.source for c in nb.cells if c.cell_type=="markdown")
assert not any(x in markdown for x in ("\\(","\\)","\\[","\\]","\x0c","\r"))
nbf.write(nb,path)
(root / "supplementary/b5-coeff-code.txt").write_text(coefficient_code)
print("Final proof source authored; static checks and final execution pending.")
