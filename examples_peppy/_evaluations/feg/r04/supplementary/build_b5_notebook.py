import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
path = root / "feg_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
# This authoring pass starts from the completed B4 notebook only.
nb.cells = nb.cells[:35]
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
nb.cells[1] = md("## Proof Statement")
theorem = md(r"""### Theorem
Under the assumptions and updates above, for every integer $N\geq1$,
$$\boxed{\|A(x_{N})\|^2\leq\frac{4L^2R^2}{N^2}.}$$
A certificate is the potential $V_{0}=0$ and
$$\boxed{V_{k}=\frac{2k^2}{N^2}\|A(x_{k})\|^2+\frac{4Lk}{N^2}\langle A(x_{k}),x_{k}-x_{0}\rangle,\qquad 1\leq k\leq N.}$$
This potential is nonincreasing. It need not be nonnegative; the terminal identity below is what converts $V_{N}\leq0$ into the residual bound. The result includes $R=0$ and $N=1$.
""")
proof = md(r"""### Proof outline
Define the nonpositive residuals
$$\mathcal L_{j}=\|A(x_{j})-A(x_{j-1/2})\|^2-L^2\|x_{j}-x_{j-1/2}\|^2,\qquad 1\leq j\leq N,$$
$$\mathcal M_{k}=-\langle A(x_{k+1})-A(x_{k}),x_{k+1}-x_{k}\rangle,\qquad 1\leq k<N,$$
$$\mathcal M_{\star}=-\langle A(x_{N}),x_{N}-x_{\star}\rangle,\qquad
\mathcal I_{0}=\|x_{0}-x_{\star}\|^2-R^2.$$
Lipschitz continuity, monotonicity, the zero-point assumption and the initial condition give $\mathcal L_j,\mathcal M_k,\mathcal M_\star,\mathcal I_0\leq0$.

For $V_{k}=2k^2\|A(x_k)\|^2/N^2+4Lk\langle A(x_k),x_k-x_0\rangle/N^2$, the shared initial point $x_{1/2}=x_0$ gives
$$V_{1}-V_{0}=\frac{2}{N^2}\mathcal L_{1}\leq0.$$
Substituting the two update equations yields the exact identity
$$V_{k+1}-V_{k}=\frac{2(k+1)^2}{N^2}\mathcal L_{k+1}+\frac{4Lk(k+1)}{N^2}\mathcal M_{k}\leq0,\qquad 1\leq k<N.$$
Both coefficients are nonnegative, hence $V_N\leq\cdots\leq V_1\leq V_0=0$. Let
$$\mathcal S_N=\left\|A(x_N)-\frac{2L}{N}(x_0-x_\star)\right\|^2\geq0.$$
The exact terminal identity is
$$\|A(x_N)\|^2-\frac{4L^2R^2}{N^2}
=V_N+\frac{4L}{N}\mathcal M_\star+\frac{4L^2}{N^2}\mathcal I_0-\mathcal S_N\leq0.$$
This proves the claim. For $N=1$, the interior sum is empty and the same base and terminal identities apply. No division by $R$ or by $\|A(x_N)\|$ is used, so zero-radius and zero-residual cases are included.
""")
nb.cells[2:2] = [theorem, proof]
# Preserve B1-B4 discovery history, replacing only the final pending section.
nb.cells[-1].source = nb.cells[-1].source.split(
    "## Closed-form Lyapunov function and symbolic identities"
)[0]
nb.cells += [
    md(
        "## Closed-form coefficient derivation\nThe numerical basis suggests three unknown coefficients. Introduce them and the two local residual multipliers in a minimal symbolic PEPFlow context. Solve all Gram, function-value and constant coefficient equations jointly. The numerical certificate is preserved as discovery evidence; exact analytic coefficients are derived independently."
    ),
    code("""b4 = json.loads((notebook_dir / "state/feg_b4.json").read_text())
assert b4["certificate_id"] == certificate["certificate_id"]
assert b4["numerical_reconstruction"]["certificate_id"] == certificate["certificate_id"]
assert b4["numerical_reconstruction"]["passed"]
print("Analytic unknowns:", b4["unresolved_coefficients"])
print("Selected numerical reconstruction has already been replayed above at every index.")
"""),
    code((root / "supplementary/b5_derivation.py").read_text(encoding="utf-8-sig")),
    md(r"""The coefficient equations give
$$a_{k+1}=\frac{(k+1)^2}{k^2}a_k,\quad b_k=\frac{L}{k}a_k,\quad c_k=0,$$
$$\mu^{\rm Lip}_k=\frac{(k+1)^2}{k^2}a_k,\quad\mu^{\rm mon}_k=\frac{2L(k+1)}{k}a_k.$$
Thus $a_k/k^2$ is constant for $k\geq1$. Choose the terminal normalization $a_N=2$, giving $a_k=2k^2/N^2$, $b_k=2Lk/N^2$, and $c_k=0$. The base and terminal identities below verify that this normalization proves the desired bound. For $N=1$, use the base coefficient $a_1=2$ directly. The solution is not asserted to equal the perturbed numerical dual coefficients exactly.
"""),
    code("""def coeff_pattern(k, N, L=sp.S.One):
    if k == 0:
        return sp.zeros(0, 0)
    return sp.Matrix([[2*sp.S(k)**2/sp.S(N)**2, 2*L*sp.S(k)/sp.S(N)**2], [2*L*sp.S(k)/sp.S(N)**2, 0]])

for j in range(1, N_int+1):
    exact_C = coeff_pattern(j, N_int)
    labels = V_k_basis_labels(j)
    pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(exact_C, dtype=object), labels, labels))
    difference = coeff_by_k[j] - np.asarray(exact_C, dtype=float)
    pf.pprint_labeled_matrix(pf.MatrixWithNames(difference, labels, labels))
    print("k:", j, "numerical-sample coefficient discrepancy:", np.max(np.abs(difference)))
print("Exact coefficients are certified by the symbolic identities, not by rounding the numerical certificate.")
"""),
    md(r"""### Closed-form Lyapunov conclusion
The analytic potential is
$$V_0=0,\qquad V_k=\frac{2k^2}{N^2}\|A(x_k)\|^2+\frac{4Lk}{N^2}\langle A(x_k),x_k-x_0\rangle\quad(1\leq k\leq N).$$
It has the discovered basis, no function-value or constant terms, and exact coefficients determined by the recurrence and terminal normalization. The following three symbolic checks verify its decrease and the endpoint implications for arbitrary symbolic parameters.
"""),
    md("## Symbolic Step Recursion Verification"),
    md(r"""For $1\leq k<N$, verify
$$V_{k+1}-V_k=\frac{2(k+1)^2}{N^2}\mathcal L_{k+1}+\frac{4Lk(k+1)}{N^2}\mathcal M_k.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero in every coordinate.
"""),
    code((root / "supplementary/b5_step.py").read_text(encoding="utf-8-sig")),
    md("## Base Case and Boundary Symbolic Verification"),
    md(r"""Using the actual initial step $x_{1/2}=x_0$, $x_1=x_0-A(x_0)/L$, verify
$$V_1-V_0=\frac{2}{N^2}\mathcal L_1.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero, proving $V_1\leq V_0=0$ because $\mathcal L_1\leq0$.
"""),
    code((root / "supplementary/b5_base.py").read_text(encoding="utf-8-sig")),
    md("### Boundary Identity Symbolic Verification"),
    md(r"""Verify
$$\|A(x_N)\|^2-\frac{4L^2R^2}{N^2}=V_N+\frac{4L}{N}\mathcal M_\star+\frac{4L^2}{N^2}\mathcal I_0-\mathcal S_N.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero, including the constant term containing $R^2$.
"""),
    code((root / "supplementary/b5_boundary.py").read_text(encoding="utf-8-sig")),
    md(r"""### Signs, domain, and telescoping
The domain is $L>0$, $R\geq0$, integers $N\geq1$ and $1\leq k<N$ for the interior identity. Every denominator used above is nonzero: $L,N,k,k+1>0$ where each appears. The coefficients $2/N^2$, $2(k+1)^2/N^2$, $4Lk(k+1)/N^2$, $4L/N$, and $4L^2/N^2$ are positive. Lipschitz and monotonicity residuals are nonpositive by the problem assumptions, $\mathcal I_0\leq0$ by initialization, and $\mathcal S_N\geq0$ is a squared norm. Therefore every term on the terminal right-hand side is nonpositive after $V_N\leq0$, and the claimed bound follows with the exact $R^2$ normalization.

The selected numerical certificate, its ranks and basis reconstructions remain finite-sample evidence. The symbolic local Lyapunov proof establishes the theorem for arbitrary admissible horizons and parameters. No separate global analytic identification of the selected numerical dual table is claimed.
"""),
]
# Include the true saved S in the existing decomposition cell, before its residual.
for c in nb.cells:
    if c.cell_type == "code" and 'S_saved = np.asarray(b2["S_matrix"])' in c.source:
        c.source = c.source.replace(
            'print("LDL diagonal:", np.diag(D))',
            'pf.pprint_labeled_matrix(pf.MatrixWithNames(S_saved, b2["basis_vectors"], b2["basis_vectors"]))\nprint("LDL diagonal:", np.diag(D))',
        )
nbf.write(nb, path)
print("Final notebook authored:", len(nb.cells), "cells")
for i, c in enumerate(nb.cells):
    if c.cell_type == "markdown":
        print(i, c.source.splitlines()[0])
