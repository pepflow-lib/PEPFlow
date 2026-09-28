import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

root = runtime.ROOT
path = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
symbolic = (
    (root / "supplementary/b5_symbolic_cells.py")
    .read_text(encoding="utf-8-sig")
    .replace("symbolic_mapping =", "symbolic_mapping: dict =")
)
signs = (root / "supplementary/b5_sign_cells.py").read_text(encoding="utf-8-sig")
formula = r"""For $N\geq2$, write $a_i=\nabla f(x_i)$ and $d_i=x_i-x_\star$. Set $V_0=0$, and for $1\leq k<N$ define
$$V_k=-\frac{L}{4N}\|d_0\|^2+\frac{L(N-k)}{(2N-k)^2}\|d_k\|^2+\frac{\|a_k-a_\star\|^2}{2L(2N-k)}-\frac{\langle d_k,a_k\rangle}{2N-k}+\frac{k+1}{2N-k}(f_k-f_\star)+\frac{k}{2N-k}(g_k-g_\star).$$
At the terminal index define
$$V_N=h(x_N)-h(x_\star)-\frac{L}{4N}\|d_0\|^2.$$
For $N=1$, use only the two exceptional values $V_0=0$ and the displayed terminal formula."""
theorem = (
    "### Theorem\nUnder the assumptions stated above, proximal gradient with step $1/L$ satisfies\n$$0\\leq h(x_N)-h(x_\\star)\\leq \\frac{LR^2}{4N}.$$\n"
    + formula
    + "\nThe sequence is nonincreasing. The bound is sharp."
)
outline = r"""### Proof outline
Use the full potential
$$V_k=-\frac{L}{4N}\|d_0\|^2+\frac{L(N-k)}{(2N-k)^2}\|d_k\|^2+\frac{\|a_k-a_\star\|^2}{2L(2N-k)}-\frac{\langle d_k,a_k\rangle}{2N-k}+\frac{k+1}{2N-k}(f_k-f_\star)+\frac{k}{2N-k}(g_k-g_\star),\quad1\leq k<N,$$
with $V_0=0$ and $V_N=h_N-h_\star-L\|d_0\|^2/(4N)$.
Define the nonpositive interpolation residuals
$$I_f(u,v)=f(v)-f(u)+\langle\nabla f(v),u-v\rangle+\frac{\|\nabla f(u)-\nabla f(v)\|^2}{2L}\leq0,$$
$$I_g(u,v)=g(v)-g(u)+\langle s_v,u-v\rangle\leq0,$$
where $s_i=L(x_{i-1}-x_i)-a_{i-1}$ and $s_\star=-a_\star$. Write $I_f(\star,i)=I_f(x_\star,x_i)$ and likewise for other pairs. Let
$$\alpha_i=\frac{i}{2N+1-i},\qquad\beta_i=\frac{i}{2N-i},\quad\beta_0=0.$$
The supplied SOS aid, now verified as part of this proof, is $S_i=c_{1,i}\|u_{1,i}\|^2+c_{2,i}\|u_{2,i}\|^2+c_{3,i}\|u_{3,i}\|^2$, with
$$c_{1,i}=\frac{N}{(2N+1-i)(2N-i)L},\quad u_{1,i}=\frac{i}{2N}a_i+\frac{2N-i}{2N}a_{i-1}-a_\star,$$
$$c_{2,i}=\frac1{2L}\left(\frac{i-1}{2N-i}\frac{2N+2}{2N+1}+\frac{2N}{(2N-i)^2(2N+1)}\right),\quad u_{2,i}=a_{i-1}+s_i-\frac{L}{2N+1-i}d_{i-1},$$
$$c_{3,i}=\frac{i}{2N+1-i}\frac{2N}{2N+1}\frac1{2L},\quad u_{3,i}=\frac{2N+1}{2N}(a_i+s_i)-\frac{a_{i-1}+s_i}{2N}-\frac{L}{2N-i}d_i.$$
For $N\geq2$, the base identity is
$$V_1=\alpha_1 I_f(\star,0)+(\alpha_2-\alpha_1)I_f(\star,1)+\alpha_1 I_f(0,1)+\beta_1 I_g(\star,1)-S_1.$$
For $2\leq i\leq N-1$, the interior identity is
$$V_i-V_{i-1}=(\alpha_{i+1}-\alpha_i)I_f(\star,i)+\alpha_i I_f(i-1,i)+(\beta_i-\beta_{i-1})I_g(\star,i)+\beta_{i-1}I_g(i-1,i)-S_i.$$
The final identity is
$$V_N-V_{N-1}=(1-\alpha_N)I_f(\star,N)+\alpha_N I_f(N-1,N)+(1-\beta_{N-1})I_g(\star,N)+\beta_{N-1}I_g(N-1,N)-S_N.$$
All coefficients are nonnegative: $2N-i\geq N>0$, $2N+1-i\geq N+1>0$;
$$\alpha_{i+1}-\alpha_i=\frac{2N+1}{(2N-i)(2N+1-i)},\qquad\beta_i-\beta_{i-1}=\frac{2N}{(2N-i)(2N+1-i)},$$
and $1-\alpha_N=1/(N+1)$, $1-\beta_{N-1}=2/(N+1)$. The three SOS coefficients are nonnegative term by term. Thus $V_N\leq\cdots\leq V_1\leq V_0=0$ and
$$h_N-h_\star\leq\frac{L}{4N}\|d_0\|^2\leq\frac{LR^2}{4N}.$$
For $N=1$, the separate identity is
$$V_1=\tfrac12 I_f(\star,0)+\tfrac12 I_f(\star,1)+\tfrac12 I_f(0,1)+I_g(\star,1)-S_1\leq0.$$
This also covers $R=0$; the proof never divides by $R$. For sharpness with $R>0$, take $f=0$, $g(x)=c\max(x,0)$, $c=LR/(2N)$, $x_0=R$, $x_\star=0$. Then $x_k=R-kR/(2N)>0$ for $0\leq k\leq N$, so $h_N-h_\star=LR^2/(4N)$."""
nb.cells[1:2] = [
    nbformat.v4.new_markdown_cell("## Proof Statement"),
    nbformat.v4.new_markdown_cell(theorem),
    nbformat.v4.new_markdown_cell(outline),
]
# Correct earlier discovery wording now that the analytic verification follows.
for cell in nb.cells:
    if cell.cell_type == "markdown" and cell.source.startswith(
        "### Block 4 conclusion"
    ):
        cell.source = cell.source.replace(
            "The displayed coefficients are candidates; Block 5 must prove the step, initial, and terminal identities for arbitrary horizons and justify their signs.",
            "The displayed coefficients were inferred numerically in Block 4. The exact symbolic identities and domain arguments below now establish them for arbitrary horizons.",
        )
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Symbolic step")
)
parts = symbolic.split("# SECTION ")
new = [
    nbformat.v4.new_markdown_cell(
        "## Closed-form conclusion and symbolic recursion context\n" + formula
    ),
    nbformat.v4.new_code_cell(
        "b4 = json.loads((notebook_dir/'state/pgm_b4.json').read_text())\nassert b4['numerical_reconstruction']['certificate_id'] == b4['certificate_id'] == b3['certificate_id']\nprint('Verified numerical structure loaded; exact proof starts below.')\n"
        + parts[0]
    ),
]
headings = {
    "symbolic_step": "## Symbolic Step Recursion Verification",
    "symbolic_base": "## Base Case and Boundary Symbolic Verification",
    "symbolic_boundary": "### Boundary Identity Symbolic Verification",
    "symbolic_n1": "### Exceptional horizon N=1",
}
equations = {
    "symbolic_step": r"For $i=k+1$ and $1\leq k\leq N-2$, verify $$V_i-V_{i-1}=(\alpha_{i+1}-\alpha_i)I_f(\star,i)+\alpha_i I_f(i-1,i)+(\beta_i-\beta_{i-1})I_g(\star,i)+\beta_{i-1}I_g(i-1,i)-S_i.$$ The residual $\mathrm{LHS}-\mathrm{RHS}$ must be exactly zero in all components.",
    "symbolic_base": r"For $N\geq2$, verify $$V_1=\alpha_1I_f(\star,0)+(\alpha_2-\alpha_1)I_f(\star,1)+\alpha_1I_f(0,1)+\beta_1I_g(\star,1)-S_1.$$ The residual $\mathrm{LHS}-\mathrm{RHS}$ must be exactly zero. This uses the actual starting displacement $d_0=x_0-x_\star$.",
    "symbolic_boundary": r"For $N\geq2$, verify $$V_N-V_{N-1}=(1-\alpha_N)I_f(\star,N)+\alpha_NI_f(N-1,N)+(1-\beta_{N-1})I_g(\star,N)+\beta_{N-1}I_g(N-1,N)-S_N,$$ where $V_N=h_N-h_\star-L\|d_0\|^2/(4N)$. The residual $\mathrm{LHS}-\mathrm{RHS}$ must be exactly zero.",
    "symbolic_n1": r"When $N=1$, verify $$h_1-h_\star-\tfrac L4\|d_0\|^2=\tfrac12I_f(\star,0)+\tfrac12I_f(\star,1)+\tfrac12I_f(0,1)+I_g(\star,1)-S_1.$$ This separately verifies the zero residual without applying an interior formula outside its domain.",
}
for part in parts[1:]:
    key, code = part.split("\n", 1)
    new += [
        nbformat.v4.new_markdown_cell(headings[key]),
        nbformat.v4.new_markdown_cell(equations[key]),
        nbformat.v4.new_code_cell(code),
    ]
new += [
    nbformat.v4.new_markdown_cell(r"""### Signs, normalization, and telescoping
For integers $1\leq i\leq N$ with $N\geq1$, the denominators $2N-i$, $2N+1-i$, $2N+1$, and $L$ are strictly positive. The factor $i-1$ in $c_{2,i}$ is nonnegative. Hence every square coefficient and every interpolation multiplier used above is nonnegative. The initial/terminal weights simplify as in the exact checks below.
The interior index range is empty when $N=2$; base and terminal identities still apply. The separate $N=1$ identity handles the only remaining case. Since every residual is nonpositive and each square is subtracted, the potential is nonincreasing. Its terminal definition then gives the theorem with the original squared-radius normalization.
Summing the checked local identities also establishes the analytic full-PEP identity
$$h_N-h_\star-\frac{L}{4N}\|d_0\|^2=\alpha_1I_f(\star,0)+\sum_{i=1}^{N-1}(\alpha_{i+1}-\alpha_i)I_f(\star,i)+(1-\alpha_N)I_f(\star,N)+\sum_{i=1}^N\alpha_iI_f(i-1,i)+\sum_{i=1}^N(\beta_i-\beta_{i-1})I_g(\star,i)+\sum_{i=2}^N\beta_{i-1}I_g(i-1,i)-\sum_{i=1}^NS_i.$$
Every active multiplier family is displayed, and every supplied square appears once. The finite sum telescopes by the verified base, interior, and terminal identities; the $N=1$ identity gives the same empty-sum convention. This is an all-horizon proof of the full candidate certificate, distinct from the earlier numerical solver checks."""),
    nbformat.v4.new_code_cell(signs),
    nbformat.v4.new_markdown_cell(
        "The exact symbolic residuals vanish and all sign/domain obligations hold. The numerical certificate, analytic full-PEP identity, and analytic Lyapunov proof are each verified by their respective evidence. Supplied SOS assistance is explicitly retained in the proof provenance."
    ),
]
nb.cells[start:] = new
# Display the exact candidate matrices as well as their earlier numerical versions.
index = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("### Block 4 conclusion")
)
nb.cells.insert(
    index,
    nbformat.v4.new_code_cell(
        "for k in range(N_int+1):\n    C_exact = coeff_pattern(k,N_int)\n    if C_exact.rows:\n        print('Closed-form coefficient matrix at k=',k)\n        pf.pprint_labeled_matrix(np.array(C_exact.tolist(),dtype=object),V_k_basis_labels(k))"
    ),
)
# Normalize accidentally doubled TeX command slashes in Markdown only.
for cell in nb.cells:
    if cell.cell_type == "markdown":
        cell.source = cell.source.replace("\\\\", "\\")
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(c) < 32 and c not in "\n\t" for c in cell.source)
nbformat.write(nb, path)
print("Prepared final notebook, cells:", len(nb.cells))
