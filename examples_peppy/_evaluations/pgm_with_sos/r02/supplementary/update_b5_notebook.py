import ast
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
path = root / "pgm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
helper = (root / "supplementary/helpers/exact_lyapunov.py").read_text(
    encoding="utf-8-sig"
)


def function_source(name):
    return ast.get_source_segment(
        helper,
        next(
            n
            for n in ast.parse(helper).body
            if isinstance(n, ast.FunctionDef) and n.name == name
        ),
    )


theorem = r"""### Theorem
Under the assumptions above, for every integer $N\geq1$,
$$h(x_{N})-h(x_{\star})\leq\frac{L\|x_{0}-x_{\star}\|^2}{4N}\leq\frac{LR^2}{4N}.$$
Write $d_{k}=x_{k}-x_{\star}$, $a_{k}=\nabla f(x_{k})$, $a_{\star}=\nabla f(x_{\star})$, $F_{k}=f(x_{k})-f(x_{\star})$, and $G_{k}=g(x_{k})-g(x_{\star})$ for $k\geq1$. An explicit nonincreasing Lyapunov certificate is $V_{0}=0$,
$$V_{k}=-\frac{L}{4N}\|d_{0}\|^2+\frac{L(N-k)}{(2N-k)^2}\|d_{k}\|^2-\frac{\langle a_{k},d_{k}\rangle}{2N-k}+\frac{\|a_{k}-a_{\star}\|^2}{2L(2N-k)}+\frac{k+1}{2N-k}F_{k}+\frac{k}{2N-k}G_{k},\quad 1\leq k<N,$$
and
$$V_{N}=F_{N}+G_{N}-\frac{L}{4N}\|d_{0}\|^2.$$
For $N=1$ there are no interior indices, and the separately verified one-step identity gives the same conclusion. No value of $g(x_{0})$ is required. The constant is sharp: in one dimension, $f=0$, $g(x)=LR|x|/(2N)$, $x_{0}=R$, $x_{\star}=0$ give $x_{N}=R/2$ and equality (with the zero-radius case immediate)."""
outline = r"""### Proof outline
Set $s_{i}=L(x_{i-1}-x_{i})-a_{i-1}\in\partial g(x_{i})$ and $s_{\star}=-a_{\star}\in\partial g(x_{\star})$. Define the nonpositive interpolation residuals
$$I^f_{u,v}=f(v)-f(u)+\langle\nabla f(v),u-v\rangle+\frac{\|\nabla f(u)-\nabla f(v)\|^2}{2L},\qquad I^g_{u,v}=g(v)-g(u)+\langle s_v,u-v\rangle.$$
For the interior expression, write
$$\Phi_{k}=\frac{L(N-k)}{(2N-k)^2}\|d_{k}\|^2-\frac{\langle a_{k},d_{k}\rangle}{2N-k}+\frac{\|a_{k}-a_{\star}\|^2}{2L(2N-k)}+\frac{k+1}{2N-k}F_{k}+\frac{k}{2N-k}G_{k},\qquad V_{k}=\Phi_{k}-\frac{L}{4N}\|d_{0}\|^2.$$
Let $p_{0}=1/(2N)$. For $1\leq i<N$, set
$$p_{i}=\frac{2N+1}{(2N-i)(2N+1-i)},\qquad q_{i}=\frac{2N}{(2N-i)(2N+1-i)},$$
while $p_{N}=1/(N+1)$ and $q_{N}=2/(N+1)$. Also set $\alpha_{i}=i/(2N+1-i)$ and $\beta_{i}=(i-1)/(2N+1-i)$.
The supplied SOS aid, verified here by the exact local identities, is $S_{i}=c_{1,i}\|u_{1,i}\|^2+c_{2,i}\|u_{2,i}\|^2+c_{3,i}\|u_{3,i}\|^2$, with
$$c_{1,i}=\frac{N}{(2N+1-i)(2N-i)L},\qquad u_{1,i}=\frac{i}{2N}a_{i}+\frac{2N-i}{2N}a_{i-1}-a_{\star},$$
$$c_{2,i}=\frac{1}{2L}\left(\frac{i-1}{2N-i}\frac{2N+2}{2N+1}+\frac{2N}{(2N-i)^2(2N+1)}\right),\qquad u_{2,i}=a_{i-1}+s_{i}-\frac{L}{2N+1-i}d_{i-1},$$
$$c_{3,i}=\frac{i}{2N+1-i}\frac{2N}{2N+1}\frac{1}{2L},\qquad u_{3,i}=\frac{2N+1}{2N}(a_{i}+s_{i})-\frac{a_{i-1}+s_{i}}{2N}-\frac{L}{2N-i}d_{i}.$$
The exact base, interior and terminal calculations below establish the unified identity
$$V_{i}-V_{i-1}=p_{i}I^f_{x_{\star},x_{i}}+q_{i}I^g_{x_{\star},x_{i}}+\alpha_{i}I^f_{x_{i-1},x_{i}}+\beta_{i}I^g_{x_{i-1},x_{i}}-S_{i}+\mathbf1_{i=1}\,p_{0}I^f_{x_{\star},x_{0}},\quad 1\leq i\leq N.$$
The $g$ adjacent term is absent when $i=1$; it is not an evaluation of $g(x_{0})$ multiplied by zero. The $N=1$ identity is verified separately.
All interpolation multipliers and SOS coefficients are nonnegative: $2N-i\geq N\geq1$, $2N+1-i\geq N+1>0$, $L>0$, and $i-1\geq0$. Thus every right-hand side is nonpositive. Hence $V_{N}\leq V_{0}=0$, giving $h(x_{N})-h(x_{\star})\leq L\|d_{0}\|^2/(4N)\leq LR^2/(4N)$.
Summing the same exact identities also proves the global full-PEP identity with all displayed interpolation weights and $S=\sum_{i=1}^{N}S_i$. The normalization multiplier is $L/(4N)$ for $\|d_{0}\|^2-R^2\leq0$. This is an analytic argument for every horizon; the numerical factor blending used during discovery is not used in the proof."""
nb.cells[1:2] = [
    nbf.v4.new_markdown_cell("## Proof Statement"),
    nbf.v4.new_markdown_cell(theorem),
    nbf.v4.new_markdown_cell(outline),
]
# All prior discovery cells are retained; the final symbolic placeholders are replaced.
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Symbolic step")
)
common = "\n\n".join(
    function_source(n)
    for n in (
        "smooth_residual",
        "convex_residual",
        "phi",
        "step_square",
        "exact_components",
        "assert_identity",
    )
)
context_template = """ctx_symbolic = pf.PEPContext("{label}").set_as_current()
F_symbolic = pf.SmoothConvexFunction(is_basis=True, tags=["f_{{{label}}}"], L=Lpar)
G_symbolic = pf.ConvexFunction(is_basis=True, tags=["g_{{{label}}}"])
H_symbolic = F_symbolic + G_symbolic
star_symbolic = H_symbolic.set_stationary_point("x_{{star,{label}}}")
x_symbolic = pf.Vector(is_basis=True, tags=["x_{{{label}}}"])
xplus_symbolic = G_symbolic.prox(x_symbolic-F_symbolic.grad(x_symbolic)/Lpar, 1/Lpar, tag="x_{{plus,{label}}}")
F_symbolic(xplus_symbolic)
"""


def context(label):
    return context_template.format(label=label)


step_code = (
    context("step")
    + """LHS = phi(Kpar+1,Npar,Lpar,xplus_symbolic,star_symbolic,F_symbolic,G_symbolic)-phi(Kpar,Npar,Lpar,x_symbolic,star_symbolic,F_symbolic,G_symbolic)
RHS = (2*Npar+1)/((2*Npar-Kpar-1)*(2*Npar-Kpar))*smooth_residual(F_symbolic,star_symbolic,xplus_symbolic,Lpar)
RHS += 2*Npar/((2*Npar-Kpar-1)*(2*Npar-Kpar))*convex_residual(G_symbolic,star_symbolic,xplus_symbolic)
RHS += (Kpar+1)/(2*Npar-Kpar)*smooth_residual(F_symbolic,x_symbolic,xplus_symbolic,Lpar)
RHS += Kpar/(2*Npar-Kpar)*convex_residual(G_symbolic,x_symbolic,xplus_symbolic)
RHS -= step_square(Kpar+1,Npar,Lpar,x_symbolic,xplus_symbolic,star_symbolic,F_symbolic,G_symbolic)
diff_step = LHS-RHS
symbolic_checks["step"] = assert_identity("Interior step, 1 <= k <= N-2", LHS, RHS, ctx_symbolic, symbolic_parameters, display=True)"""
)
base_code = (
    context("base")
    + """LHS = phi(sp.S.One,Npar,Lpar,xplus_symbolic,star_symbolic,F_symbolic,G_symbolic)-Lpar/(4*Npar)*(x_symbolic-star_symbolic)**2
RHS = smooth_residual(F_symbolic,star_symbolic,x_symbolic,Lpar)/(2*Npar)
RHS += (2*Npar+1)/((2*Npar-1)*(2*Npar))*smooth_residual(F_symbolic,star_symbolic,xplus_symbolic,Lpar)
RHS += sp.S.One/(2*Npar-1)*convex_residual(G_symbolic,star_symbolic,xplus_symbolic)
RHS += smooth_residual(F_symbolic,x_symbolic,xplus_symbolic,Lpar)/(2*Npar)
RHS -= step_square(sp.S.One,Npar,Lpar,x_symbolic,xplus_symbolic,star_symbolic,F_symbolic,G_symbolic)
diff_base = LHS-RHS
symbolic_checks["base"] = assert_identity("Base, N >= 2", LHS, RHS, ctx_symbolic, symbolic_parameters, display=True)"""
)
boundary_code = (
    context("boundary")
    + """LHS = H_symbolic(xplus_symbolic)-H_symbolic(star_symbolic)-phi(Npar-1,Npar,Lpar,x_symbolic,star_symbolic,F_symbolic,G_symbolic)
RHS = smooth_residual(F_symbolic,star_symbolic,xplus_symbolic,Lpar)/(Npar+1)+2/(Npar+1)*convex_residual(G_symbolic,star_symbolic,xplus_symbolic)
RHS += Npar/(Npar+1)*smooth_residual(F_symbolic,x_symbolic,xplus_symbolic,Lpar)
RHS += (Npar-1)/(Npar+1)*convex_residual(G_symbolic,x_symbolic,xplus_symbolic)
RHS -= step_square(Npar,Npar,Lpar,x_symbolic,xplus_symbolic,star_symbolic,F_symbolic,G_symbolic)
diff_boundary = LHS-RHS
symbolic_checks["boundary"] = assert_identity("Final step, N >= 2", LHS, RHS, ctx_symbolic, symbolic_parameters, display=True)"""
)
one_code = (
    context("one")
    + """LHS = H_symbolic(xplus_symbolic)-H_symbolic(star_symbolic)-Lpar/4*(x_symbolic-star_symbolic)**2
RHS = sp.Rational(1,2)*smooth_residual(F_symbolic,star_symbolic,x_symbolic,Lpar)+sp.Rational(1,2)*smooth_residual(F_symbolic,star_symbolic,xplus_symbolic,Lpar)
RHS += convex_residual(G_symbolic,star_symbolic,xplus_symbolic)+sp.Rational(1,2)*smooth_residual(F_symbolic,x_symbolic,xplus_symbolic,Lpar)
RHS -= step_square(sp.S.One,sp.S.One,Lpar,x_symbolic,xplus_symbolic,star_symbolic,F_symbolic,G_symbolic)
diff_one = LHS-RHS
symbolic_checks["N1"] = assert_identity("Exceptional N=1", LHS, RHS, ctx_symbolic, symbolic_parameters, display=True)"""
)
cells = [
    nbf.v4.new_markdown_cell("## Closed-form derivation and exact verification"),
    nbf.v4.new_markdown_cell(
        r"""The sparse coefficient pattern from B4 fixes the candidate $\Phi_{k}$ displayed in the theorem. The adjacent interpolation weights are $\alpha_i=i/(2N+1-i)$ and $\beta_i=(i-1)/(2N+1-i)$; their differences generate the star weights in the interior. The base and terminal coefficients are fixed by $V_{0}=0$ and $V_{N}=h(x_N)-h(x_\star)-L\|d_0\|^2/(4N)$. We now substitute these candidates into the actual proximal-gradient recurrence and verify all coordinates exactly, with independent base and terminal contexts. No coefficient fitting or numerical blending is used in these symbolic identities."""
    ),
    nbf.v4.new_code_cell(
        """assert b4["numerical_reconstruction"]["certificate_id"] == b4["certificate_id"]
assert all(error["quadratic_frobenius"] <= 1e-5 for error in structure_errors.values())
Kpar, Npar, Lpar = pf.Parameter("k"), pf.Parameter("N"), pf.Parameter("L")
k_symbolic, N_symbolic = sp.symbols("k N", integer=True, positive=True)
L_symbolic = sp.Symbol("L", positive=True)
symbolic_parameters = {"k": k_symbolic, "N": N_symbolic, "L": L_symbolic}
symbolic_checks = {}
"""
        + common
    ),
    nbf.v4.new_code_cell("""# Exact recurrence relations for the candidate interpolation coefficients.
i_symbolic = sp.Symbol("i", integer=True, positive=True)
p_increment = (i_symbolic+1)/(2*N_symbolic-i_symbolic)-i_symbolic/(2*N_symbolic+1-i_symbolic)
q_increment = i_symbolic/(2*N_symbolic-i_symbolic)-(i_symbolic-1)/(2*N_symbolic+1-i_symbolic)
assert sp.cancel(p_increment-(2*N_symbolic+1)/((2*N_symbolic-i_symbolic)*(2*N_symbolic+1-i_symbolic))) == 0
assert sp.cancel(q_increment-2*N_symbolic/((2*N_symbolic-i_symbolic)*(2*N_symbolic+1-i_symbolic))) == 0
assert sp.cancel(1-N_symbolic/(N_symbolic+1)-1/(N_symbolic+1)) == 0
assert sp.cancel(1-(N_symbolic-1)/(N_symbolic+1)-2/(N_symbolic+1)) == 0
print("Interior star increments and terminal coefficient corrections verified exactly.")"""),
    nbf.v4.new_markdown_cell("## Symbolic Step Recursion Verification"),
    nbf.v4.new_markdown_cell(r"""For $1\leq k\leq N-2$, the equation checked is
$$\Phi_{k+1}-\Phi_k=\frac{2N+1}{(2N-k-1)(2N-k)}I^f_{x_\star,x_{k+1}}+\frac{2N}{(2N-k-1)(2N-k)}I^g_{x_\star,x_{k+1}}+\frac{k+1}{2N-k}I^f_{x_k,x_{k+1}}+\frac{k}{2N-k}I^g_{x_k,x_{k+1}}-S_{k+1}.$$
The anchored initial-distance term cancels. The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in every Gram, function-value and constant coordinate."""),
    nbf.v4.new_code_cell(step_code),
    nbf.v4.new_markdown_cell("## Base Case and Boundary Symbolic Verification"),
    nbf.v4.new_markdown_cell(r"""For $N\geq2$, the initial equation is
$$V_1=\frac{1}{2N}I^f_{x_\star,x_0}+\frac{2N+1}{(2N-1)(2N)}I^f_{x_\star,x_1}+\frac{1}{2N-1}I^g_{x_\star,x_1}+\frac{1}{2N}I^f_{x_0,x_1}-S_1.$$
Here $V_1=\Phi_1-L\|d_0\|^2/(4N)$ and $V_0=0$. No $g(x_0)$ is introduced. The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero."""),
    nbf.v4.new_code_cell(base_code),
    nbf.v4.new_markdown_cell("### Boundary Identity Symbolic Verification"),
    nbf.v4.new_markdown_cell(r"""For $N\geq2$, the terminal equation is
$$V_N-V_{N-1}=\frac{1}{N+1}I^f_{x_\star,x_N}+\frac{2}{N+1}I^g_{x_\star,x_N}+\frac{N}{N+1}I^f_{x_{N-1},x_N}+\frac{N-1}{N+1}I^g_{x_{N-1},x_N}-S_N.$$
Equivalently, the left side is $h(x_N)-h(x_\star)-\Phi_{N-1}$. The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero."""),
    nbf.v4.new_code_cell(boundary_code),
    nbf.v4.new_markdown_cell("### Exceptional one-step horizon"),
    nbf.v4.new_markdown_cell(r"""At $N=1$, verify the separate identity
$$h(x_1)-h(x_\star)-\frac{L}{4}\|d_0\|^2=\frac12 I^f_{x_\star,x_0}+\frac12 I^f_{x_\star,x_1}+I^g_{x_\star,x_1}+\frac12 I^f_{x_0,x_1}-S_1\big|_{N=1}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish exactly; this also avoids extending the interior formula outside its domain."""),
    nbf.v4.new_code_cell(one_code),
    nbf.v4.new_markdown_cell(
        "### Signs, domains, normalization, and full-PEP identity"
    ),
    nbf.v4.new_markdown_cell(r"""For $1\leq i\leq N$, every denominator in the residual multipliers and SOS coefficients is positive because $L>0$, $2N-i\geq N\geq1$, and $2N+1-i\geq N+1$. The only possibly zero numerator is $i-1$, which is nonnegative. Thus all residual multipliers are nonnegative and $S_i\geq0$. Smooth-convex and convex interpolation make their residuals nonpositive, so the exact identities imply $V_i\leq V_{i-1}$. No positivity of $V_i$ is assumed or required.
The exact telescoping identity for every $N\geq1$ is
$$h(x_N)-h(x_\star)-\frac{L}{4N}\|d_0\|^2=p_0I^f_{x_\star,x_0}+\sum_{i=1}^{N}\left(p_iI^f_{x_\star,x_i}+q_iI^g_{x_\star,x_i}+\alpha_iI^f_{x_{i-1},x_i}-S_i\right)+\sum_{i=2}^{N}\beta_iI^g_{x_{i-1},x_i}.$$
There is exactly one copy of each supplied $S_i$, and these weights coincide with the B2 candidate formulas. Combining the initial residual $I_0=\|d_0\|^2-R^2\leq0$ with multiplier $L/(4N)$ therefore yields the global full-PEP certificate. The exact normalization identity below retains the radius term explicitly."""),
    nbf.v4.new_code_cell("""Rpar = pf.Parameter("R")
R_symbolic = sp.Symbol("R", nonnegative=True)
x_initial = pf.Vector(is_basis=True, tags=["x_{initial,normalization}"])
metric_symbolic = H_symbolic(xplus_symbolic)-H_symbolic(star_symbolic)
terminal_potential = metric_symbolic-Lpar/(4*Npar)*(x_initial-star_symbolic)**2
initial_residual = (x_initial-star_symbolic)**2-Rpar**2
LHS = metric_symbolic-Lpar*Rpar**2/(4*Npar)
RHS = terminal_potential+Lpar/(4*Npar)*initial_residual
normalization_parameters = dict(symbolic_parameters)
normalization_parameters["R"] = R_symbolic
symbolic_checks["normalization"] = assert_identity("Radius normalization",LHS,RHS,ctx_symbolic,normalization_parameters,display=True)
assert all(check["passed"] for check in symbolic_checks.values())
print("Exact base, step, terminal, N=1 and radius identities all pass.")
print("Sign argument: nonpositive interpolation residuals, nonnegative multipliers and subtracted SOS imply V_i <= V_(i-1).")
print("Therefore h(x_N)-h(x_star) <= L ||x_0-x_star||^2/(4N) <= L R^2/(4N).")
print("Summing the local identities gives the complete global candidate certificate for arbitrary N.")"""),
    nbf.v4.new_markdown_cell("### Sharpness"),
    nbf.v4.new_markdown_cell(
        r"""For $R>0$, take the one-dimensional instance $f(x)=0$ and $g(x)=c|x|$, with $c=LR/(2N)$ and $x_0=R$. The proximal step subtracts $c/L=R/(2N)$ while the iterate is positive, so $x_k=R(1-k/(2N))$ for $0\leq k\leq N$. Therefore $x_N=R/2$, $x_\star=0$, and $h(x_N)-h(x_\star)=LR^2/(4N)$. This admissible instance attains the bound. At $R=0$, the initial point is a minimizer and the bound is zero."""
    ),
    nbf.v4.new_code_cell("""sharp_c = L_symbolic*R_symbolic/(2*N_symbolic)
sharp_xN = R_symbolic/2
assert sp.cancel(sharp_c*sharp_xN-L_symbolic*R_symbolic**2/(4*N_symbolic)) == 0
print("Sharp example objective matches the theorem constant exactly.")"""),
]
nb.cells[start:] = cells
# Preserve the history, but make stage-specific numerical statuses unambiguous.
for cell in nb.cells:
    if cell.cell_type == "code":
        cell.source = cell.source.replace(
            "Numerical certificate verified; analytic full-PEP and Lyapunov proof statuses remain false.",
            "At the B2 handoff: numerical certificate verified; analytic proofs were still pending.",
        )
nbf.write(nb, path)
print("Final proof and exact symbolic notebook cells saved")
