"""Finalize theorem and proof cells, preserving the full discovery notebook."""
from pathlib import Path
import nbformat as nbf

root=Path(__file__).resolve().parents[1]
dest=root/'bppm_example_lyap.ipynb'
nb=nbf.read(dest,as_version=4)
md=nbf.v4.new_markdown_cell
code=nbf.v4.new_code_cell
theorem=r"""### Theorem

Under the stated assumptions, for any $\alpha>0$, $R\geq0$ and integer $N\geq1$, define
$$V_{k}=\frac{\alpha k\bigl(f(x_{k})-f(x_{\star})\bigr)+D_h(x_{\star},x_{k})-D_h(x_{\star},x_{0})}{\alpha N},
\qquad 0\leq k\leq N.$$
Then $V_{0}=0$ and $V_{k+1}\leq V_{k}$. Consequently,
$$\boxed{f(x_{N})-f(x_{\star})\leq\frac{R}{\alpha N}.}$$
Equivalently, the unnormalized energy $\mathcal E_{k}=\alpha k(f(x_{k})-f(x_{\star}))+D_h(x_{\star},x_{k})$ is nonincreasing, with $\mathcal E_{0}\leq R$.
"""
outline=r"""### Proof outline

Write $f_i=f(x_i)$, $h_i=h(x_i)$, $g_i=\nabla f(x_i)$, $q_i=\nabla h(x_i)$, and
$$r^f_{i,j}=f_j-f_i+\langle g_j,x_i-x_j\rangle\leq0,\qquad
r^h_{i,j}=h_j-h_i+\langle q_j,x_i-x_j\rangle\leq0.$$
These signs follow directly from convexity. The proximal optimality equation is $q_{k+1}=q_k-\alpha g_{k+1}$.
For the displayed potential
$$V_{k}=\frac{\alpha k(f_k-f_{\star})+D_h(x_{\star},x_k)-D_h(x_{\star},x_0)}{\alpha N},$$
the initial step satisfies
$$V_1-V_0=\frac1N r^f_{\star,1}+\frac1{\alpha N}r^h_{1,0}\leq0,\qquad V_0=0.$$
For every $1\leq k<N$, the exact decrease identity is
$$V_{k+1}-V_k=
\frac1N r^f_{\star,k+1}+\frac{k}{N}r^f_{k,k+1}
+\frac{k+1}{\alpha N}r^h_{k+1,k}+\frac{k}{\alpha N}r^h_{k,k+1}\leq0.$$
There are no additional residual families or square terms. All four multipliers are nonnegative because $\alpha>0$, $N\geq1$, and $k\geq1$. Thus $V_N\leq V_0=0$.

Finally, $r^h_{\star,N}=-D_h(x_{\star},x_N)\leq0$, and the exact terminal identity is
$$f_N-f_{\star}-\frac{R}{\alpha N}
=V_N+\frac{D_h(x_{\star},x_0)-R+r^h_{\star,N}}{\alpha N}\leq V_N\leq0.$$
The initial condition gives the sign of $D_h(x_{\star},x_0)-R$. This proves the rate with $R$, not $R^2$. When $N=1$, the separate initial-step identity and terminal identity suffice. No strict convexity of $h$, strong convexity, or bounded Euclidean radius is used.
"""
idx=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Proof statement'))
nb.cells[idx:idx+1]=[md('## Proof Statement'),md(theorem),md(outline)]

# Add true selected S and closed-form coefficient displays to existing diagnostic cells.
for c in nb.cells:
    if c.cell_type=='code' and c.source.startswith('S_array = np.asarray'):
        c.source += "\nprint('Selected numerical S (retained, not rounded to zero):')\npf.pprint_labeled_matrix(pf.MatrixWithNames(S_array, b2['S_row_names'], b2['S_col_names']))"
    if c.cell_type=='code' and c.source.startswith('def coeff_pattern'):
        c.source += "\nfor k in range(1, N_int+1):\n    print('Closed-form coefficient candidate at k =', k)\n    pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(coeff_pattern(k, sp.Integer(N_int), params_sp['alpha']), dtype=object), V_k_basis_labels(k), V_k_basis_labels(k)))"
    if c.cell_type=='markdown' and c.source.startswith('### Block 4 conclusion'):
        c.source=c.source.replace('The formula is a candidate; Block 5 must establish the exact step, base and terminal identities and signs for the stated parameter domain.', 'This was the B4 candidate. The symbolic checks below now establish its exact coefficient structure, step, base and terminal identities, and signs for the stated parameter domain.')

sections=[
md('## Closed-form Lyapunov function and symbolic identities'),
md(r"""The numerical pattern is now verified with symbolic $k$, $N$, and $\alpha$ in independent PEPFlow contexts. The local expression is
$$V_{k}=\frac{k}{N}(f(x_k)-f(x_{\star}))+\frac{h(x_0)-h(x_k)+\langle q_0,a_0\rangle-\langle q_k,a_k\rangle}{\alpha N},
\quad a_k=x_{\star}-x_k.$$
The next cells verify its exact one-step identity, including the function coordinates. The proof retains the numerical full-PEP discovery record but does not promote that global certificate to an independently verified arbitrary-horizon full-PEP formula.
"""),
code("b4 = json.loads((notebook_dir / 'state/bppm_b4.json').read_text())\nassert b4['certificate_id'] == b3['certificate_id']\nassert b4['numerical_reconstruction']['certificate_id'] == b4['certificate_id']\nassert b4['numerical_reconstruction']['passed']\nfor k in range(N_int+1):\n    expected_C = np.asarray(b4['coeff_by_k'][str(k)], dtype=float).reshape(coeff_by_k[k].shape)\n    assert np.allclose(expected_C, coeff_by_k[k], atol=1e-4, rtol=1e-5)\n    assert all(error <= 1e-4 for error in component_residuals[str(k)].values())\nprint('B4 basis, coefficients and full-expression reconstruction revalidated before exact proof.')"),
code((root/'supplementary/b5_symbolic_common.py').read_text()),
md('## Symbolic Step Recursion Verification'),
md(r"""For $1\leq k<N$, verify
$$\mathrm{LHS}=V_{k+1}-V_k
=\frac{r^f_{\star,k+1}}N+\frac{k r^f_{k,k+1}}N
+\frac{(k+1)r^h_{k+1,k}}{\alpha N}+\frac{k r^h_{k,k+1}}{\alpha N}=\mathrm{RHS}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ should simplify to zero. The context encodes the proximal optimality equation exactly. A second exact check compares the geometric formula with the discovered quadratic and function-value coefficient structure.
"""),
code((root/'supplementary/b5_step.py').read_text()),
md('## Base Case and Boundary Symbolic Verification'),
md(r"""In a separate initial-step context, verify
$$\mathrm{LHS}=V_1-V_0=\frac{r^f_{\star,1}}N+\frac{r^h_{1,0}}{\alpha N}=\mathrm{RHS},\qquad V_0=0.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ should simplify to zero. The initial energy also satisfies $\mathcal E_0-R=D_h(x_{\star},x_0)-R\leq0$, checked with symbolic $R$. This covers the initial step even for $N=1$.
"""),
code((root/'supplementary/b5_base.py').read_text()),
md('### Boundary Identity Symbolic Verification'),
md(r"""In a separate terminal context with symbolic $N$, verify
$$\mathrm{LHS}=f(x_N)-f(x_{\star})-\frac{R}{\alpha N}-V_N
=\frac{D_h(x_{\star},x_0)-R+r^h_{\star,N}}{\alpha N}=\mathrm{RHS}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ should simplify to zero. Since $r^h_{\star,N}=-D_h(x_{\star},x_N)\leq0$ and the initial radius residual is nonpositive, this inequality discards the terminal Bregman term in the required direction.
"""),
code((root/'supplementary/b5_boundary.py').read_text()),
md(r"""### Domain, signs, and conclusion

The proof uses precisely $\alpha>0$, $R\geq0$, integer $N\geq1$, and $0\leq k<N$. All divisions are therefore defined. The functions' convexity gives every interpolation residual its nonpositive sign. The local multipliers $1/N$, $k/N$, $(k+1)/(\alpha N)$ and $k/(\alpha N)$ are nonnegative, as checked symbolically. The initial condition and convexity of $h$ justify both terminal residual signs. No numerical tolerance is used to establish these exact signs or identities.

The exact identities yield $V_N\leq V_0=0$ and then
$$f(x_N)-f(x_{\star})\leq\frac{R}{\alpha N}.$$
The numerical certificate remains separately verified; the analytic Lyapunov proof is complete. An independent arbitrary-horizon full-PEP certificate verification is not claimed.
""")]
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Closed-form Lyapunov'))
nb.cells[start:]=sections
nbf.write(nb,dest)
print('Final notebook authored:',dest)
