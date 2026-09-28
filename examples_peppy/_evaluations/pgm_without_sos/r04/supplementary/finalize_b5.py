# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]
import runtime

source = (runtime.ATTEMPT / "supplementary/verify_b5.py").read_text(
    encoding="utf-8-sig"
)
exec(compile(source, "verify_b5.py", "exec"))
derivation = (notebook_dir / "supplementary/b5_coefficient_derivation.py").read_text(
    encoding="utf-8-sig"
)
signs = (notebook_dir / "supplementary/b5_sign_audit.py").read_text(
    encoding="utf-8-sig"
)
exec(compile(derivation, "b5_coefficient_derivation.py", "exec"))
exec(compile(signs, "b5_sign_audit.py", "exec"))
parts = (
    (notebook_dir / "supplementary/b5_cells.py")
    .read_text(encoding="utf-8-sig")
    .split("# CELL")
)
theorem = (notebook_dir / "supplementary/b5_theorem.md").read_text(encoding="utf-8-sig")
outline = (notebook_dir / "supplementary/b5_proof_outline.md").read_text(
    encoding="utf-8-sig"
)
resolved = dict(
    quadratic_convention="Symmetric C, off-diagonal entries counted twice; same B4 basis",
    interior=dict(
        index_domain="1 <= k <= N-1",
        basis_labels=["e_0", "e_k", "grad_f(x_k)-grad_f(x_star)", "grad_f(x_star)"],
        quadratic_coefficients={
            "0,0": "-1/(4N)",
            "1,1": "(N-k)/(2N-k)^2",
            "1,2": "-1/(2L(2N-k))",
            "1,3": "-1/(2L(2N-k))",
            "2,2": "-beta_k/L^2",
            "other": "0",
        },
        beta="Explicit ordered transfer-matrix product in theorem; empty product identity",
    ),
    initial=dict(index_domain="k=0", basis_labels=[], expression="V_0=0"),
    terminal=dict(
        index_domain="k=N",
        basis_labels=["e_0"],
        quadratic_coefficients={"0,0": "-1/(4N)"},
    ),
    function_terms=[
        dict(
            index_domain="1 <= k < N",
            expression="f(x_k)-f(x_star)",
            coefficient="(k+1)/(L(2N-k))",
        ),
        dict(
            index_domain="1 <= k < N",
            expression="g(x_k)-g(x_star)",
            coefficient="k/(L(2N-k))",
        ),
        dict(index_domain="k=N", expression="h(x_N)-h(x_star)", coefficient="1/L"),
    ],
    constant_terms=[],
)
state = {
    **b4,
    "lyapunov_proof_verified": True,
    "analytic_full_pep_verified": False,
    "proof_checks": proof_checks,
    "proof_arguments": dict(
        step="Exact PEPFlow all-coordinate identity with beta_k Möbius recurrence and Q_k block square; k=1..N-2.",
        base="Separate N>=2 identity from x_0; no g(x_0) required. Separate N=1 identity verified.",
        boundary="Separate final-step identity using H_T,K_T and beta_(N-1); exact normalization.",
        signs="Transfer matrices have positive entries for 1<=j<=N-2; terminal beta>=0. H leading principal minors positive by exact determinant formula. All interpolation weights nonnegative.",
        domain="Integers N>=1, L>0, R>=0; t=2N-k>1 on every interior/base block. Empty products defined. No extra assumptions on the functions.",
        normalization="V_N=(h_N-h_star)/L-||e_0||^2/(4N)<=0 and initial squared radius <=R^2.",
    ),
    "lyapunov_formula": theorem,
    "discovery_expression_structure": b4["expression_structure"],
    "expression_structure": resolved,
    "coeff_code": parts[0][
        parts[0].index("def beta_closed") : parts[0].index("\nfor j in range")
    ],
    "local_multiplier_code": parts[1] + parts[2],
    "remaining_unknowns": [],
    "unresolved_coefficients": [],
    "coefficient_formula_status": "verified",
    "run_status": "final_validation_pending",
    "presentation_policy": "evaluation-ancillary-v1",
    "proof_source": "supplementary/b5_cells.py",
    "proof_text": outline,
}
(notebook_dir / "state/pgm_b5.json").write_text(
    json.dumps(state, indent=2, allow_nan=False)
)
nb_path = notebook_dir / "pgm_example_lyap.ipynb"
nb = nbf.read(nb_path, as_version=4)
# Add the actual labeled S matrix to the existing numerical certificate evidence.
for cell in nb.cells:
    if cell.cell_type == "code" and "S_named = pf.MatrixWithNames" in cell.source:
        cell.source = cell.source.replace(
            "D, ell = ldl_decompose_with_reversed_basis",
            "pf.pprint_labeled_matrix(S_named, precision=5)\nD, ell = ldl_decompose_with_reversed_basis",
        )
nb.cells[1:2] = [
    nbf.v4.new_markdown_cell("## Proof Statement"),
    nbf.v4.new_markdown_cell(theorem),
    nbf.v4.new_markdown_cell(outline),
]
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Symbolic step")
)
nb.cells[start:] = [
    nbf.v4.new_markdown_cell(
        "## Closed-form coefficient derivation\nThe B4 coefficients are now resolved. The finite product is an explicit solution, with no unknown coefficient functions or recursive evaluation required. Compare it with all selected numerical matrices and function-gap coefficients."
    ),
    nbf.v4.new_code_cell(parts[0]),
    nbf.v4.new_markdown_cell(r"""### Transfer formula and coefficient equation
The terminal condition is $\beta_{N-1}=(N-1)/(2(N+1)^{2})$. Eliminating the future-gradient block gives
$$\beta_{k}=\frac{k(k+1)(t-1)\bigl(2t(t-1)\beta_{k+1}+k+t+1\bigr)}{2t^{2}\bigl(2(t-1)((2k+1)t-k)\beta_{k+1}+(k^{2}+3k+1)t+1\bigr)},\qquad t=2N-k.$$
The matrix product in the theorem solves this relation: splitting its first factor gives exactly the ratio identity checked below. Its last empty product is the terminal condition. The recurrence evaluates to zero at $k=0$ as required for the initial cancellation. The next cell derives the relation from the actual local quadratic remainder rather than fitting samples."""),
    nbf.v4.new_code_cell(parts[1]),
    nbf.v4.new_code_cell(derivation),
    nbf.v4.new_markdown_cell(r"""### Closed-form Lyapunov conclusion
For $1\leq k<N$ the resulting expression is
$$V_{k}=-\frac{\|e_{0}\|^{2}}{4N}+\frac{k+1}{L(2N-k)}(f_{k}-f_{\star})+\frac{k}{L(2N-k)}(g_{k}-g_{\star})+\frac{N-k}{(2N-k)^{2}}\|e_{k}\|^{2}-\frac{\langle e_{k},\nabla f(x_{k})\rangle}{L(2N-k)}-\beta_{k}\|p_{k}\|^{2},$$
with the explicit transfer-product coefficient from the theorem, $V_{0}=0$, and $V_{N}=(h_{N}-h_{\star})/L-\|e_{0}\|^{2}/(4N)$. The next sections verify the exact local identities over symbolic index and parameter domains."""),
    nbf.v4.new_markdown_cell(
        "## Symbolic recursion contexts\nThe following definitions create the actual proximal-gradient recursion, sum stationarity, normalized gradients and quadratic block remainders in the approved PEPFlow framework."
    ),
    nbf.v4.new_code_cell(parts[2]),
    nbf.v4.new_markdown_cell("## Symbolic Step Recursion Verification"),
    nbf.v4.new_markdown_cell(r"""For $1\leq k\leq N-2$, check
$$V_{k+1}-V_{k}=(a_{k+1}-a_{k})J_{f}(x_{\star},x_{k+1})+a_{k}J_{f}(x_{k},x_{k+1})+(b_{k+1}-b_{k})J_{g}(x_{\star},x_{k+1})+b_{k}J_{g}(x_{k},x_{k+1})-Q_{k}.$$
Here $\beta_{k+1}$ is a nonnegative symbolic coefficient and $\beta_{k}$ is its proved transfer formula. The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in every component."""),
    nbf.v4.new_code_cell(parts[3]),
    nbf.v4.new_markdown_cell("## Base Case and Boundary Symbolic Verification"),
    nbf.v4.new_markdown_cell(r"""For $N\geq2$, check
$$V_{1}=a_{0}J_{f}(x_{\star},x_{0})+(a_{1}-a_{0})J_{f}(x_{\star},x_{1})+a_{0}J_{f}(x_{0},x_{1})+b_{1}J_{g}(x_{\star},x_{1})-Q_{0}-\frac{\|p_{0}\|^{2}}{4N}.$$
This uses a separate initial context and no evaluation of $g(x_{0})$. The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish."""),
    nbf.v4.new_code_cell(parts[4]),
    nbf.v4.new_markdown_cell("### Boundary Identity Symbolic Verification"),
    nbf.v4.new_markdown_cell(r"""For $N\geq2$, check
$$V_{N}-V_{N-1}=\frac1{N+1}J_{f}(x_{\star},x_{N})+\frac{N}{N+1}J_{f}(x_{N-1},x_{N})+\frac2{N+1}J_{g}(x_{\star},x_{N})+\frac{N-1}{N+1}J_{g}(x_{N-1},x_{N})-Q_{T}.$$
Also check $h(x_{N})-h(x_{\star})=L(V_{N}+\|e_{0}\|^{2}/(4N))$. Both residuals must vanish in all coordinates."""),
    nbf.v4.new_code_cell(parts[5]),
    nbf.v4.new_markdown_cell("### Exceptional one-step horizon"),
    nbf.v4.new_markdown_cell(r"""For $N=1$, check separately
$$V_{1}=\tfrac12J_{f}(x_{\star},x_{0})+\tfrac12J_{f}(x_{\star},x_{1})+\tfrac12J_{f}(x_{0},x_{1})+J_{g}(x_{\star},x_{1})-Q_{T}-\tfrac14\|p_{0}\|^{2}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish without using an interior coefficient formula."""),
    nbf.v4.new_code_cell(parts[6]),
    nbf.v4.new_markdown_cell(r"""## Signs, domains and telescoping
For integer $N\geq2$, every transfer index has $1\leq j\leq N-2$ and $t=2N-j>1$. All four entries of $M_{j}$ are positive because $((2j+1)t-j)=j(2t-1)+t>0$. The terminal vector has positive second coordinate and nonnegative first coordinate. Products therefore have $v_{k}>0$ and $\beta_{k}\geq0$; the empty-product $N=2$ case has the same property.
For each local block, $H_{11}>0$ and the determinant formula displayed above is strictly positive for $k\geq0$, $t>1$, and $c\geq0$. Thus each $Q_{k}\geq0$. The terminal matrix has leading principal minors $1/2$ and $1/4$, so $Q_{T}\geq0$.
The interpolation differences satisfy $a_{k+1}-a_{k}=(2N+1)/(t(t-1))>0$ and $b_{k+1}-b_{k}=2N/(t(t-1))>0$. The consecutive weights, initial square coefficient and explicit terminal/one-step weights are nonnegative. Hence every verified increment is nonpositive. For $N\geq2$, use the base, interior and terminal identities; for $N=1$, use its separate identity. In either case $V_{N}\leq0$.
Since $L>0$ and $\|e_{0}\|^{2}\leq R^{2}$, the exact normalization gives the claimed bound, including $R=0$. No numerical sign test substitutes for these domain arguments."""),
    nbf.v4.new_code_cell(signs),
]
nbf.write(nb, nb_path)
print("Analytic proof and final notebook sources assembled.")
