"""Finalize proof exposition and visible exact calculations before validation."""
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
notebook = ROOT/'pgm_example_lyap.ipynb'
nb = nbf.read(notebook,as_version=4)
md,code = nbf.v4.new_markdown_cell,nbf.v4.new_code_cell
theorem = r"""### Theorem

Under the assumptions above, for every integer $N\geq1$,
$$h(x_{N})-h(x_{\star})\leq\frac{LR^2}{4N}.$$
Let $r_{k}=x_{k}-x_{\star}$, $a_{k}=\nabla f(x_{k})$, $F_{k}=f(x_{k})-f(x_{\star})$, and $G_{k}=g(x_{k})-g(x_{\star})$. An explicit nonincreasing certificate is $V_{0}=0$,
$$\boxed{V_{k}=-\frac{L}{4N}\|r_{0}\|^2
+\frac{L(N-k)}{(2N-k)^2}\|r_{k}\|^2
+\frac{\|a_{k}-a_{\star}\|^2}{2L(2N-k)}
-\frac{\langle r_{k},a_{k}\rangle}{2N-k}
+\frac{k+1}{2N-k}F_{k}+\frac{k}{2N-k}G_{k},\quad1\leq k<N,}$$
and
$$V_{N}=F_{N}+G_{N}-\frac{L}{4N}\|r_{0}\|^2.$$
The interior range is empty when $N=1$. All identities below are exact for symbolic $N,L$ and the stated index ranges; finite-sample numerical evidence is kept separately.
"""
outline = r"""### Proof outline

Write $s_{i}=L(x_{i-1}-x_{i})-a_{i-1}\in\partial g(x_{i})$, and choose $s_{\star}=-a_{\star}$. For evaluated points define the nonpositive interpolation residuals
$$I^{f}(u,v)=f(v)-f(u)+\langle\nabla f(v),u-v\rangle+\frac{\|\nabla f(u)-\nabla f(v)\|^2}{2L},$$
$$I^{g}(u,v)=g(v)-g(u)+\langle s_{v},u-v\rangle.$$
The potential has quadratic part
$$-\frac{L}{4N}\|r_{0}\|^2+\frac{L(N-k)}{(2N-k)^2}\|r_{k}\|^2
+\frac{\|a_{k}-a_{\star}\|^2}{2L(2N-k)}-\frac{\langle r_{k},a_{k}\rangle}{2N-k},$$
and function part $((k+1)F_{k}+kG_{k})/(2N-k)$ for $1\leq k<N$; its endpoints are $V_{0}=0$ and $V_{N}=F_{N}+G_{N}-L\|r_{0}\|^2/(4N)$.

The supplied SOS aid, now verified in the exact local identities, is $S_{i}=\sum_{j=1}^{3}c_{j,i}\|u_{j,i}\|^2$, where
$$c_{1,i}=\frac{N}{(2N+1-i)(2N-i)L},\qquad
u_{1,i}=\frac{i}{2N}a_{i}+\frac{2N-i}{2N}a_{i-1}-a_{\star},$$
$$c_{2,i}=\frac{1}{2L}\left(\frac{i-1}{2N-i}\frac{2N+2}{2N+1}
+\frac{2N}{(2N-i)^2(2N+1)}\right),\qquad
u_{2,i}=a_{i-1}+s_{i}-\frac{Lr_{i-1}}{2N+1-i},$$
$$c_{3,i}=\frac{i}{2N+1-i}\frac{2N}{2N+1}\frac{1}{2L},\qquad
u_{3,i}=\frac{2N+1}{2N}(a_{i}+s_{i})-\frac{a_{i-1}+s_{i}}{2N}-\frac{Lr_{i}}{2N-i}.$$
All these coefficients are nonnegative for $1\leq i\leq N$ and $L>0$.

For $1\leq i<N$, put
$$\eta^{f}_{i}=\frac{2N+1}{(2N-i)(2N+1-i)},\quad
\eta^{g}_{i}=\frac{2N}{(2N-i)(2N+1-i)},\quad
\theta^{f}_{i}=\frac{i}{2N+1-i},\quad\theta^{g}_{i}=\frac{i-1}{2N+1-i}.$$
For $N\geq2$, the exact base identity is
$$V_{1}=\frac{I^{f}(x_{\star},x_{0})}{2N}
+\eta^{f}_{1}I^{f}(x_{\star},x_{1})+\frac{I^{f}(x_{0},x_{1})}{2N}
+\eta^{g}_{1}I^{g}(x_{\star},x_{1})-S_{1}\leq0.$$
For $2\leq i<N$, the exact step identity is
$$V_{i}-V_{i-1}=\eta^{f}_{i}I^{f}(x_{\star},x_{i})
+\theta^{f}_{i}I^{f}(x_{i-1},x_{i})+\eta^{g}_{i}I^{g}(x_{\star},x_{i})
+\theta^{g}_{i}I^{g}(x_{i-1},x_{i})-S_{i}\leq0.$$
The distinct terminal identity is
$$V_{N}-V_{N-1}=\frac{I^{f}(x_{\star},x_{N})}{N+1}
+\frac{N}{N+1}I^{f}(x_{N-1},x_{N})+\frac{2}{N+1}I^{g}(x_{\star},x_{N})
+\frac{N-1}{N+1}I^{g}(x_{N-1},x_{N})-S_{N}\leq0.$$
No $g(x_{0})$ evaluation is required. When $N=1$, use the separately verified identity
$$V_{1}=\tfrac12 I^{f}(x_{\star},x_{0})+\tfrac12 I^{f}(x_{\star},x_{1})
+\tfrac12 I^{f}(x_{0},x_{1})+I^{g}(x_{\star},x_{1})-S_{1}\leq0.$$
Every displayed decrease follows from nonpositive residuals and nonnegative coefficients and squares. Thus $V_{N}\leq V_{0}=0$ and
$$h(x_{N})-h(x_{\star})\leq\frac{L}{4N}\|r_{0}\|^2\leq\frac{LR^2}{4N}.$$
Summing these same exact local identities gives the full-PEP certificate with initial multiplier $L/(4N)$ and total slack $\sum_{i=1}^{N}S_{i}$. The numerical polar correction used for stable basis discovery is not part of this analytic identity.
"""
if nb.cells[1].source.startswith('## Proof statement'):
    nb.cells[1:2]=[md('## Proof Statement'),md(theorem),md(outline)]
else:
    first_import = next(i for i,c in enumerate(nb.cells) if c.cell_type=='code')
    nb.cells[1:first_import]=[md('## Proof Statement'),md(theorem),md(outline)]
start = next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Closed form'))
symbolic_source = (ROOT/'supplementary'/'b5_symbolic.py').read_text()
definitions,rest=symbolic_source.split('# STEP',1)
step,rest=rest.split('# BASE',1)
base,rest=rest.split('# BOUNDARY',1)
boundary,single=rest.split('# N1',1)
derivation=(ROOT/'supplementary'/'b5_derivation.py').read_text()
formula_check=(ROOT/'supplementary'/'b5_formula_check.py').read_text()
final_checks=(ROOT/'supplementary'/'b5_final_checks.py').read_text()
new_cells = [md('## Closed form and exact proof\nThe B4 numerical structure is now resolved analytically. The sparse pattern suggests a reduced coefficient ansatz; the following full-coordinate equations determine its coefficients, and the subsequent exact identities prove the selected solution without relying on numerical fitting.'),
             md('### Symbolic context and residual definitions\nAll auxiliary contexts below encode the actual proximal update and stationarity of $f+g$ at the minimizer. The supplied square families are carried into the local equations explicitly.'),code(definitions),
             md(r"""### Derive the coefficients
Use the ansatz $A_{k}\|r_{k}\|^2+B_{k}\|a_{k}-a_{\star}\|^2+C_{k}\langle r_{k},a_{k}\rangle+\alpha_{k}F_{k}+\beta_{k}G_{k}$ plus a constant multiple of $\|r_{0}\|^2$. Equate all Gram, function-value and constant coordinates of its difference with the supported local interpolation/SOS combination. The base identity fixes the remaining constant.
"""),code(derivation),md('### Compare derived and numerical coefficients\nThe exact symmetric coefficient matrices are compared with every B4 matrix and every function-gap coefficient, including both endpoints. Off-diagonal entries count twice.'),code(formula_check),
             md(r"""### Closed-form conclusion
For $1\leq k<N$,
$$V_{k}=-\frac{L\|r_{0}\|^2}{4N}+\frac{L(N-k)\|r_{k}\|^2}{(2N-k)^2}
+\frac{\|a_{k}-a_{\star}\|^2}{2L(2N-k)}-\frac{\langle r_{k},a_{k}\rangle}{2N-k}
+\frac{(k+1)F_{k}+kG_{k}}{2N-k}.$$
Set $V_{0}=0$ and $V_{N}=F_{N}+G_{N}-L\|r_{0}\|^2/(4N)$. The next sections verify the exact identities for these expressions; they establish the formulas over arbitrary horizons, not merely the observed samples.
"""),md('## Symbolic Step Recursion Verification'),
             md(r"""For $1\leq k\leq N-2$, with $i=k+1$, verify
$$\mathrm{LHS}=V_{k+1}-V_{k},\quad
\mathrm{RHS}=\eta^{f}_{i}I^{f}(x_{\star},x_{i})+\theta^{f}_{i}I^{f}(x_{i-1},x_{i})
+\eta^{g}_{i}I^{g}(x_{\star},x_{i})+\theta^{g}_{i}I^{g}(x_{i-1},x_{i})-S_{i}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in every coordinate.
"""),code(step),md('## Base Case and Boundary Symbolic Verification'),
             md(r"""For $N\geq2$, verify
$$V_{1}=\frac{I^{f}(x_{\star},x_{0})}{2N}+\frac{2N+1}{(2N-1)2N}I^{f}(x_{\star},x_{1})
+\frac{I^{f}(x_{0},x_{1})}{2N}+\frac{I^{g}(x_{\star},x_{1})}{2N-1}-S_{1}.$$
The residual of the left-hand side minus the right-hand side must vanish in every coordinate. This uses the actual starting point and $V_{0}=0$.
"""),code(base),md('### Boundary Identity Symbolic Verification'),
             md(r"""For $N\geq2$, verify
$$V_{N}-V_{N-1}=\frac{I^{f}(x_{\star},x_{N})}{N+1}+\frac{N I^{f}(x_{N-1},x_{N})}{N+1}
+\frac{2I^{g}(x_{\star},x_{N})}{N+1}+\frac{(N-1)I^{g}(x_{N-1},x_{N})}{N+1}-S_{N}.$$
Here $V_{N}=F_{N}+G_{N}-L\|r_{0}\|^2/(4N)$; the residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in every coordinate.
"""),code(boundary),md('### Single-iteration boundary'),
             md(r"""For $N=1$, verify directly
$$F_{1}+G_{1}-\frac{L\|r_{0}\|^2}{4}
=\frac{I^{f}(x_{\star},x_{0})+I^{f}(x_{\star},x_{1})+I^{f}(x_{0},x_{1})}{2}
+I^{g}(x_{\star},x_{1})-S_{1}.$$
The residual must vanish; no interior formula is evaluated outside its domain.
"""),code(single),md('### Signs, domain, and normalization'),
             md(r"""For $1\leq i\leq N$, write $i=1+u$ and $N=1+u+v$ with nonnegative integers $u,v$. All residual multipliers and square coefficients become nonnegative rational functions with positive denominators when $L>0$. Also $2N-k\geq N+1>0$ on the interior potential's domain. The terminal convention yields the exact normalization identity
$$h(x_{N})-h(x_{\star})-\frac{LR^2}{4N}
=V_{N}+\frac{L}{4N}(\|r_{0}\|^2-R^2).$$
Its residual is checked below. Both terms on the right are nonpositive by the verified decreases and the initial constraint. This also covers $R=0$ without dividing by $R$.

The consecutive multipliers telescope into the star multipliers:
$$\frac{j+1}{2N-j}-\frac{j}{2N+1-j}=\frac{2N+1}{(2N-j)(2N+1-j)},$$
$$\frac{j}{2N-j}-\frac{j-1}{2N+1-j}=\frac{2N}{(2N-j)(2N+1-j)}.$$
Together with the explicit endpoint coefficients, this verifies that summing the local identities gives the complete analytic full-PEP certificate, with no omitted interpolation family, constant or boundary term.
"""),code(final_checks),md(r"""### Final conclusion
The exact symbolic checks establish $V_{N}\leq V_{0}=0$ and therefore
$$\boxed{h(x_{N})-h(x_{\star})\leq\frac{LR^2}{4N}\quad\text{for every integer }N\geq1.}$$
The numerical certificate, analytic full-PEP identity, and analytic Lyapunov proof have distinct supporting evidence. The supplied SOS was declared assistance and was verified against this attempt's numerical certificate and in the exact local proof.
""")]
nb.cells[start:] = new_cells
for cell in nb.cells:
    if cell.cell_type=='markdown':
        assert '\\(' not in cell.source and '\\[' not in cell.source
        assert not any(ord(c)<32 and c not in '\n\t' for c in cell.source)
nbf.write(nb,notebook)
print('Final proof notebook source assembled; static checks and clean-kernel execution remain.')
