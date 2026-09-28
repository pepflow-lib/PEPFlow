"""Integrate the exact proof into the evolving notebook, before final static checks."""
import re
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
nb_path = ROOT / "dual_feg_example_lyap.ipynb"
nb = nbf.read(nb_path, as_version=4)
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
source = (ROOT / "supplementary/b5_symbolic.py").read_text()
source = source.split("# PROOF_CODE_START\n", 1)[1].split("# PROOF_CODE_END", 1)[0]
sections = {}
for section in source.split("# SECTION: ")[1:]:
    title, body = section.split("\n", 1)
    sections[title.strip()] = body.strip()
potential_latex = r"""$$V_{0}=0,$$
$$V_{k}=-\frac{4L}{N}\langle g_{N},x_{0}-x_{N}\rangle+\frac{4L}{N-k}\langle g_{N},x_{k}-x_{N}\rangle-4\langle g_{N},z_{k}\rangle+\frac{4L}{N-k}\langle x_{k}-x_{N},z_{k}\rangle-2\|z_{k}\|^{2},\qquad 1\leq k<N,$$
$$V_{N}=2\|g_{N}\|^{2}-\frac{4L}{N}\langle g_{N},x_{0}-x_{N}\rangle,$$"""
theorem = r"""### Theorem
Let $A$ be a monotone, $L$-Lipschitz operator on a real finite-dimensional Euclidean space, with $L>0$, $A(x_{\star})=0$, and $\|x_{0}-x_{\star}\|^{2}\leq R^{2}$ for $R\geq0$. For any integer $N\geq1$, run the displayed Dual-FEG recurrence with $z_{0}=0$ and $\alpha=1/L$. Put $g_{N}=A(x_{N})$. The following potential, anchored at the final point, is nonincreasing:
""" + potential_latex + r"""
and the final residual satisfies
$$\boxed{\|A(x_{N})\|^{2}\leq\frac{4L^{2}R^{2}}{N^{2}}.}$$
The formula for $V_{N}$ applies also when $N=1$; the interior range is then empty."""
outline = r"""### Proof outline
Use the explicitly defined potential
""" + potential_latex + r"""
For $0\leq k\leq N-2$, write $m=N-k$ and $y_{k}=x_{k+1/2}$. Define
$$M_{k}=-\langle x_{N}-y_{k},g_{N}-A(y_{k})\rangle\leq0,$$
$$Q_{k}=\|A(x_{k})-A(y_{k})\|^{2}-L^{2}\|x_{k}-y_{k}\|^{2}\leq0.$$
The exact recurrence identity is
$$V_{k+1}-V_{k}=\frac{4L}{m(m-1)}M_{k}+\frac{2}{m^{2}}Q_{k}\leq0.$$
At $k=0$, the same formula is verified separately with $z_{0}=0$ and $V_{0}=0$. At the terminal step, $x_{N}=x_{N-1}-(z_{N-1}+A(x_{N-1}))/L$, and
$$Q_{N-1}=\|A(x_{N-1})-g_{N}\|^{2}-L^{2}\|x_{N-1}-x_{N}\|^{2}\leq0,$$
$$V_{N}-V_{N-1}=2Q_{N-1}\leq0.$$
For $N=1$, direct substitution gives $V_{1}=2Q_{0}\leq0$. Hence $V_{N}\leq V_{0}=0$ in every case.

Finally let
$$M_{\star}=-\langle x_{N}-x_{\star},g_{N}\rangle\leq0,\qquad S=\left\|\frac{2L}{N}(x_{0}-x_{\star})-g_{N}\right\|^{2}\geq0.$$
The exact normalized boundary identity is
$$\|g_{N}\|^{2}-\frac{4L^{2}R^{2}}{N^{2}}=V_{N}+\frac{4L}{N}M_{\star}-S+\frac{4L^{2}}{N^{2}}\big(\|x_{0}-x_{\star}\|^{2}-R^{2}\big)\leq0.$$
All multipliers are nonnegative on their stated ranges. This proof uses no division by $R$ or $\|g_{N}\|$, so it includes $R=0$ and zero residuals."""
# Replace the initial placeholder with separate proof-statement cells.
placeholder = next(i for i, c in enumerate(nb.cells) if c.source.startswith("## Proof statement"))
nb.cells[placeholder:placeholder+1] = [md("## Proof Statement"), md(theorem), md(outline)]
start = next(i for i, c in enumerate(nb.cells) if c.source.startswith("## Closed-form Lyapunov"))
proof_cells = [md("## Closed-form Lyapunov function and symbolic identities"),
md("### Coherent input and final formula\nThe Block 4 source, complete certificate, grouping, and every-index reconstructions were replayed above from unchanged inputs. The fitted coefficient pattern is now tested symbolically, with no fitted tolerance in the proof. All function-value and constant coordinates are absent from the potential and are checked nonetheless."),
code('b4 = json.loads((notebook_dir / "state/dual_feg_b4.json").read_text())\nassert b4["certificate_id"] == b3["certificate_id"] == reconstruction["certificate_id"]\nassert reconstruction["passed"] and reconstruction6["passed"]\nassert b4["expression_structure"]["function_terms"] == []\nassert b4["expression_structure"]["constant_terms"] == []\nprint("Selected and confirming numerical structures were recomputed above.")'),
md(r"""### Closed-form potential
The exact formula to be verified is
""" + potential_latex + r"""
The interior formula extends algebraically to $k=0$ with $z_{0}=0$, giving zero, but the first step and $N=1$ are checked separately. The next sections prove the one-step and endpoint identities for symbolic positive $L$ and integer horizons, rather than inferring them from finite samples."""),
code(sections["helpers"]),
md("## Symbolic Step Recursion Verification"),
md(r"""For $1\leq k\leq N-2$, $m=N-k\geq2$, the identity is
$$\underbrace{V_{k+1}-V_{k}}_{\mathrm{LHS}}=\underbrace{\frac{4L}{m(m-1)}M_{k}+\frac{2}{m^{2}}Q_{k}}_{\mathrm{RHS}}.$$
The code writes $m=q+1$ with positive integer $q$ to encode the nonzero denominators. This covers every admissible remaining-step count. It treats $N$ symbolically; the actual indices satisfy $m=N-k$. The residual $\mathrm{LHS}-\mathrm{RHS}$ must be exactly zero in all scalar components."""),
code(sections["step"]),
md("## Base Case and Boundary Symbolic Verification"),
md(r"""For $N\geq2$, $z_{0}=0$ gives $V_{0}=0$, and
$$\underbrace{V_{1}-V_{0}}_{\mathrm{LHS}}=\underbrace{\frac{4L}{N(N-1)}M_{0}+\frac{2}{N^{2}}Q_{0}}_{\mathrm{RHS}}.$$
Here $N=q+1$ runs through all horizons at least 2. Both the initial-potential expression and $\mathrm{LHS}-\mathrm{RHS}$ must simplify exactly to zero."""),
code(sections["base"]),
md("### Terminal Step Symbolic Verification"),
md(r"""The final update is $x_{N}=x_{N-1}-(z_{N-1}+A(x_{N-1}))/L$. For $N\geq2$,
$$\underbrace{V_{N}-V_{N-1}}_{\mathrm{LHS}}=\underbrace{2\big(\|A(x_{N-1})-g_{N}\|^{2}-L^{2}\|x_{N-1}-x_{N}\|^{2}\big)}_{\mathrm{RHS}}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero. The terminal auxiliary update is $z_{N}=-A(x_{N})$, but $V_{N}$ does not depend on $z_{N}$."""),
code(sections["terminal"]),
md("### Exceptional Horizon N=1"),
md(r"""When $N=1$, $x_{1}=x_{0}-A(x_{0})/L$ and $z_{0}=0$. There is no interior formula to substitute into. Directly,
$$\underbrace{2\|A(x_{1})\|^{2}-4L\langle A(x_{1}),x_{0}-x_{1}\rangle}_{V_{1}}=\underbrace{2\big(\|A(x_{0})-A(x_{1})\|^{2}-L^{2}\|x_{0}-x_{1}\|^{2}\big)}_{\mathrm{RHS}}.$$
The residual $V_{1}-\mathrm{RHS}$ must be exactly zero."""),
code(sections["single"]),
md("### Boundary Identity Symbolic Verification"),
md(r"""For every $N\geq1$, define $M_{\star}=-\langle x_{N}-x_{\star},g_{N}\rangle$ and $S=\|(2L/N)(x_{0}-x_{\star})-g_{N}\|^{2}$. We verify
$$\underbrace{\|g_{N}\|^{2}-\frac{4L^{2}R^{2}}{N^{2}}}_{\mathrm{LHS}}=\underbrace{V_{N}+\frac{4L}{N}M_{\star}-S+\frac{4L^{2}}{N^{2}}\big(\|x_{0}-x_{\star}\|^{2}-R^{2}\big)}_{\mathrm{RHS}}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must be zero in Gram, function-value and constant coordinates, including the $R^{2}$ normalization."""),
code(sections["boundary"]),
md(r"""### Domain, signs, and telescoping proof
All denominators are nonzero: $L>0$, $N\geq1$, and $m\geq2$ in the nonterminal identities. Thus $4L/[m(m-1)]$, $2/m^{2}$, $2$, $4L/N$, and $4L^{2}/N^{2}$ are positive. Monotonicity gives $M_{k}\leq0$ and $M_{\star}\leq0$; Lipschitz continuity gives each $Q_{k}\leq0$. The squared norm $S$ is nonnegative. The initial-radius residual is nonpositive by assumption. These elementary signs need no auxiliary localization argument.

For $N\geq2$, the initial-step identity, all interior-step identities, and the terminal-step identity telescope to $V_{N}\leq V_{0}=0$. For $N=1$, the separate direct check gives the same conclusion. Every term on the right of the normalized boundary identity is therefore nonpositive, proving the theorem for every $N\geq1$, $L>0$, and $R\geq0$.

### Explicit global certificate
The same exact identities establish the global multiplier and square candidates, separately from their earlier numerical fits. Set $I_{0}=\|x_{0}-x_{\star}\|^{2}-R^{2}$. Telescoping yields the exact identity
$$\|g_{N}\|^{2}-\frac{4L^{2}R^{2}}{N^{2}}-\frac{4L^{2}}{N^{2}}I_{0}-\sum_{k=0}^{N-2}\left(\frac{4L}{(N-k)(N-k-1)}M_{k}+\frac{2}{(N-k)^{2}}Q_{k}\right)-2Q_{N-1}-\frac{4L}{N}M_{\star}+S=0.$$
For $N=1$ the sum is empty. Its derivation substitutes the sum of the verified local identities into the verified boundary identity. Hence this is an arbitrary-horizon full-PEP identity with every active interpolation family, the initial normalization, and the Gram square included. All other interpolation multipliers are zero. No numerical coefficient is used in this analytic certificate."""),
code('assert set(exact_checks) == {"step", "base_zero", "base", "terminal_step", "N1", "boundary"}\nassert all(all(check[key] is True for key in ["gram_zero", "function_zero", "offset_zero"]) for check in exact_checks.values())\nprint("Exact component checks:", exact_checks)\nprint("Nonincreasing direction: positive multipliers times nonpositive interpolation residuals.")\nprint("Boundary direction: V_N <= 0, M_star <= 0, -S <= 0, and the initial-radius residual <= 0.")\nprint("Theorem: ||A(x_N)||^2 <= 4 L^2 R^2 / N^2 for N>=1, L>0, R>=0.")\nprint("Global analytic certificate follows by the displayed finite telescoping sum.")')]
nb.cells[start:] = proof_cells
# Preserve the discovery chronology but update the top-level statements to distinguish evidence from the theorem below.
nb.cells[0].source = nb.cells[0].source.replace("investigate a uniform bound", "prove the uniform bound")
# Ensure the true selected numerical S is displayed, alongside the existing factor/candidate matrices.
for cell in nb.cells:
    if cell.cell_type == "code" and 'print("Selected S eigenvalues:"' in cell.source:
        cell.source += '\nprint("Selected numerical S")\npf.pprint_labeled_matrix(np.asarray(b2["S_matrix"], dtype=float), b2["basis_vectors"], precision=6)'
    if cell.cell_type == "markdown":
        # Normalize single-token unbraced subscripts without changing already braced expressions.
        cell.source = re.sub(r"_([A-Za-z0-9])(?![A-Za-z0-9])", r"_{\1}", cell.source)
        assert not any(c in cell.source for c in ["\x0c", "\r", "\\(", "\\)", "\\[", "\\]"])
nbf.write(nb, nb_path)
print("Final proof notebook written; static checks and fresh nbconvert execution are pending")
