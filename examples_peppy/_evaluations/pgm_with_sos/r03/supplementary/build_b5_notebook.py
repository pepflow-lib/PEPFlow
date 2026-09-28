"""Finalize the evolving notebook; execution occurs after static checks."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
from runtime import NOTEBOOK_DIR, configure  # ty: ignore[unresolved-import]

configure()
import inspect  # noqa: E402 - imports follow runtime or notebook setup

import derive_coefficients  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
import nbformat as nbf  # ty: ignore[unresolved-import]  # optional notebook-generation dependency  # noqa: E402 - imports follow runtime or notebook setup

path = NOTEBOOK_DIR / "pgm_example_lyap.ipynb"
nb = nbf.read(path, as_version=4)
nb.cells = nb.cells[:36]
nb.cells[35].source = (
    nb.cells[35].source.split("## Closed-form")[0]
    + "\nThe following section resolves these analytic unknowns."
)
theorem = r"""### Theorem

Let $f$ be convex and $L$-smooth, $g$ closed, proper, and convex, and $h=f+g$. Suppose $L>0$, $R\geq0$, $N\geq1$ is an integer, $x_{\star}$ minimizes $h$, and $\|x_{0}-x_{\star}\|^2\leq R^2$. Assume the prescribed proximal updates are well-defined. For
$$x_{k+1}=\operatorname{prox}_{g/L}(x_{k}-\nabla f(x_{k})/L),$$
write $d_{k}=x_{k}-x_{\star}$ and $a_{k}=\nabla f(x_{k})$. Define $V_{0}=0$,
$$
\begin{aligned}
V_{k}={}&-\frac{L}{4N}\|d_{0}\|^2
+\frac{L(N-k)}{(2N-k)^2}\|d_{k}\|^2
-\frac{\langle d_{k},a_{k}\rangle}{2N-k}
+\frac{\|a_{k}-a_{\star}\|^2}{2L(2N-k)}\\
&+\frac{k+1}{2N-k}(f(x_{k})-f(x_{\star}))
+\frac{k}{2N-k}(g(x_{k})-g(x_{\star})),
\qquad 1\leq k<N,
\end{aligned}
$$
and
$$V_{N}=h(x_{N})-h(x_{\star})-\frac{L}{4N}\|d_{0}\|^2.$$
Then $V_{N}\leq\cdots\leq V_{1}\leq V_{0}=0$, including the separate $N=1$ case. Consequently,
$$\boxed{h(x_{N})-h(x_{\star})\leq\frac{L}{4N}\|d_{0}\|^2\leq\frac{LR^2}{4N}.}$$
"""
outline = r"""### Proof outline

The interior potential combines the anchor $-L\|d_{0}\|^2/(4N)$ with
$$
\frac{L(N-k)}{(2N-k)^2}\|d_{k}\|^2
-\frac{\langle d_{k},a_{k}\rangle}{2N-k}
+\frac{\|a_{k}-a_{\star}\|^2}{2L(2N-k)}
+\frac{k+1}{2N-k}(f(x_{k})-f_{\star})
+\frac{k}{2N-k}(g(x_{k})-g_{\star}).
$$
Use $V_{0}=0$ and $V_{N}=h(x_{N})-h_{\star}-L\|d_{0}\|^2/(4N)$ at the endpoints.

Choose $s_{i}=L(x_{i-1}-x_{i})-a_{i-1}\in\partial g(x_{i})$ for $i\geq1$ and $s_{\star}=-a_{\star}\in\partial g(x_{\star})$. Convex interpolation gives
$$I^{f}_{u,v}=f(v)-f(u)+\langle\nabla f(v),u-v\rangle
+\frac{\|\nabla f(u)-\nabla f(v)\|^2}{2L}\leq0,$$
$$I^{g}_{u,v}=g(v)-g(u)+\langle s_{v},u-v\rangle\leq0.$$
The proof never evaluates $g(x_{0})$.

For $1\leq i\leq N$, define
$$\alpha_{i-1}=\frac{i}{2N+1-i},\quad
\beta_{i-1}=\frac{i-1}{2N+1-i},\quad
\delta_{i}=\frac{2N}{(2N-i)(2N+1-i)},$$
$$\gamma_{i}=
\begin{cases}
\frac{2N+1}{(2N-i)(2N+1-i)},&i<N,\\
\frac1{N+1},&i=N.
\end{cases}$$
Set
$$
\begin{aligned}
c_{1,i}&=\frac{N}{(2N+1-i)(2N-i)L},&
u_{1,i}&=\frac{i}{2N}a_{i}+\frac{2N-i}{2N}a_{i-1}-a_{\star},\\
c_{2,i}&=\frac1{2L}\left(
\frac{(i-1)(2N+2)}{(2N-i)(2N+1)}
+\frac{2N}{(2N-i)^2(2N+1)}\right),&
u_{2,i}&=a_{i-1}+s_{i}-\frac{L}{2N+1-i}d_{i-1},\\
c_{3,i}&=\frac{i}{2N+1-i}\frac{2N}{2N+1}\frac1{2L},&
u_{3,i}&=\frac{2N+1}{2N}(a_{i}+s_{i})
-\frac{a_{i-1}+s_{i}}{2N}-\frac{L}{2N-i}d_{i},
\end{aligned}
$$
and $Q_{i}=c_{1,i}\|u_{1,i}\|^2+c_{2,i}\|u_{2,i}\|^2+c_{3,i}\|u_{3,i}\|^2$.
These square families are the declared supplied assistance; their use is justified by the exact local identities below.

For every $i=1,\ldots,N$ the complete increment is
$$
\begin{aligned}
V_{i}-V_{i-1}={}&
\alpha_{i-1}I^{f}_{x_{i-1},x_{i}}
+\mathbf1_{\{i\geq2\}}\beta_{i-1}I^{g}_{x_{i-1},x_{i}}
+\gamma_{i}I^{f}_{x_{\star},x_{i}}
+\delta_{i}I^{g}_{x_{\star},x_{i}}\\
&+\mathbf1_{\{i=1\}}\frac1{2N}I^{f}_{x_{\star},x_{0}}
-Q_{i}.
\end{aligned}
$$
The term involving $I^{g}_{x_{0},x_{1}}$ is absent, not an evaluation multiplied by zero. Exact symbolic checks cover the interior, first step, final step, and $N=1$ separately.

All interpolation multipliers are nonnegative. Since $2N-i\geq N\geq1$, $2N+1-i\geq N+1>0$, and $L>0$, each square coefficient is positive; for $c_{2,1}$ its second summand is strictly positive. Thus every increment is nonpositive. Telescoping yields $V_{N}\leq V_{0}=0$, and the displayed terminal definition and initial radius bound give the claimed rate. No positivity of $V_{k}$ is required.
"""
nb.cells[1:2] = [
    nbf.v4.new_markdown_cell("## Proof Statement"),
    nbf.v4.new_markdown_cell(theorem),
    nbf.v4.new_markdown_cell(outline),
]


def md(s):
    nb.cells.append(nbf.v4.new_markdown_cell(s))


def code(s):
    nb.cells.append(nbf.v4.new_code_cell(s))


md("""## Closed-form coefficient derivation

B4 supplied a complete numerical basis and function-gap structure. We now introduce all ten independent symmetric quadratic coefficients at each of two consecutive indices, plus both function-gap coefficients, as unknowns. The supplied square family and the previously inferred interpolation multipliers enter as candidates. All Gram, function, and constant coefficients of the local difference must vanish.

The transport used in B3 was a numerical decomposition of the saved solver slack. The analytic proof below uses the original exact square family, checked independently for symbolic horizons; the comparison to B4 is numerical evidence, not the analytic justification.
""")
code("""b4 = json.loads((notebook_dir / "state/pgm_b4.json").read_text())
assert b4["numerical_reconstruction"]["certificate_id"] == b4["certificate_id"]
assert b4["numerical_reconstruction"]["passed"]
print("Analytic unknown count:", len(b4["unresolved_coefficients"]))
""")
# All symbolic definitions are visible here, including auxiliary context construction.
code((NOTEBOOK_DIR / "supplementary/helpers/exact_proof.py").read_text())
code(
    "\n\n".join(
        inspect.getsource(fn)
        for fn in [
            derive_coefficients.coefficient_ansatz,
            derive_coefficients.closed_coefficients,
            derive_coefficients.derive,
        ]
    )
    + """
derivation_context, unknowns, coefficient_equations, solved, free, chosen = derive()
print("Scalar coefficient equations:",len(coefficient_equations))
print("Unknown coefficients:",len(unknowns))
print("Unfixed symbols:",sorted(map(str,free)))
for unknown,value in zip(unknowns,solved):
    print(unknown,"=",sp.factor(value))
print("Chosen coefficient formulas satisfy every equation exactly.")
"""
)
md(r"""The solution leaves only three time-independent additions: a multiple of $\|d_{0}\|^2$, a multiple of $\langle d_{0},a_{\star}\rangle$, and a multiple of $\|a_{\star}\|^2$. The base identity fixes these additions. The following exact equations impose the first-step condition on deviations from the selected formula; they force all three deviations to zero. This fixes the anchor coefficient to $-L/(4N)$ and the other two additions to zero.
""")
code("""e_gauge = local_context("gauge",base=True)
A_gauge, B_gauge, C_gauge = pf.Parameter("A_gauge"),pf.Parameter("B_gauge"),pf.Parameter("C_gauge")
A_symbol,B_symbol,C_symbol = sp.symbols("A_gauge B_gauge C_gauge")
gauge_values = {**symbolic_values,"A_gauge":A_symbol,"B_gauge":B_symbol,"C_gauge":C_symbol}
d_initial=e_gauge["x0"]-e_gauge["xs"]
a_stationary=e_gauge["f"].grad(e_gauge["xs"])
gauge_expression=(potential(e_gauge,e_gauge["y"],1)
    +A_gauge*d_initial**2+B_gauge*d_initial*a_stationary+C_gauge*a_stationary**2
    -base_rhs(e_gauge))
gauge_gram,gauge_functions,gauge_offset=components(gauge_expression,e_gauge["ctx"],gauge_values)
gauge_equations=[v for v in [*gauge_gram,*gauge_functions,gauge_offset] if v!=0]
gauge_solution=sp.solve(gauge_equations,[A_symbol,B_symbol,C_symbol],dict=True)
assert gauge_solution==[{A_symbol:0,B_symbol:0,C_symbol:0}]
print("Base normalization fixes the three constant additions:",gauge_solution)
""")
md(r"""In the basis $[d_{0},d_{k},a_{k},a_{\star}-a_{k}]$, the resulting matrix is
$$C_{k}=
\begin{pmatrix}
-\frac{L}{4N}&0&0&0\\
0&\frac{L(N-k)}{(2N-k)^2}&-\frac1{2(2N-k)}&0\\
0&-\frac1{2(2N-k)}&0&0\\
0&0&0&\frac1{2L(2N-k)}
\end{pmatrix},\qquad1\leq k<N.$$
The function-gap coefficients are $p_{k}=(k+1)/(2N-k)$ and $q_{k}=k/(2N-k)$. The terminal matrix is $[-L/(4N)]$ and its two function-gap coefficients are one; the initial quadratic basis is empty.
""")
code("""for j in range(n+1):
    labels=V_k_basis_labels(j,n)
    if j==0:
        exact_C=sp.zeros(0)
        exact_p=exact_q=sp.S.Zero
    elif j==n:
        exact_C=sp.Matrix([[-sp.Rational(1,4*n)]])
        exact_p=exact_q=sp.S.One
    else:
        exact_C,exact_p,exact_q=closed_coefficients(j,n,sp.S.One)
    numerical_C=np.asarray(b4["coeff_by_k"][str(j)],dtype=float)
    if j==0:
        numerical_C=np.zeros((0,0))
    if labels:
        print("Numerical coefficients, k =",j)
        pf.pprint_labeled_matrix(pf.MatrixWithNames(numerical_C,labels,labels))
        print("Closed-form coefficients, k =",j)
        pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(exact_C,dtype=object),labels,labels))
    error=maxabs(numerical_C-np.asarray(exact_C,dtype=float))
    row=b4["sample_structure_coefficients"][j]
    gap_error=max(abs(row["f_gap_coefficient"]-float(exact_p)),
                  abs(row["g_gap_coefficient"]-float(exact_q)))
    assert error<=1e-4 and gap_error<=1e-4
    print("Coefficient error:",error,"function-gap error:",gap_error)
""")
md(r"""### Closed-form potential

For $1\leq k<N$,
$$
V_{k}=-\frac{L}{4N}\|d_{0}\|^2
+\frac{L(N-k)}{(2N-k)^2}\|d_{k}\|^2
-\frac{\langle d_{k},a_{k}\rangle}{2N-k}
+\frac{\|a_{k}-a_{\star}\|^2}{2L(2N-k)}
+\frac{k+1}{2N-k}(f(x_{k})-f_{\star})
+\frac{k}{2N-k}(g(x_{k})-g_{\star}).
$$
Use $V_{0}=0$ and $V_{N}=h(x_{N})-h_{\star}-L\|d_{0}\|^2/(4N)$. The next sections verify the local identities over symbolic indices and parameters, including both exceptional endpoints.
""")


def context_code(label, base=False):
    return (
        f'''ctx_exact = pf.PEPContext("{label}").set_as_current()
ff_exact = pf.SmoothConvexFunction(is_basis=True,tags=["f_{{{label}}}"],L=LL)
gg_exact = pf.ConvexFunction(is_basis=True,tags=["g_{{{label}}}"])
hh_exact = ff_exact+gg_exact
xs_exact = hh_exact.set_stationary_point("x_{{star}}")
x_exact = pf.Vector(is_basis=True,tags=["x_{{k}}"])
x0_exact = '''
        + ("x_exact" if base else 'pf.Vector(is_basis=True,tags=["x_{0}"])')
        + """
ff_exact(x_exact)
"""
        + ("" if base else "gg_exact(x_exact)\n")
        + """y_exact = gg_exact.prox(x_exact-ff_exact.grad(x_exact)/LL,1/LL,tag="x_{k+1}")
ff_exact(y_exact)
e_exact = {"ctx":ctx_exact,"f":ff_exact,"g":gg_exact,"xs":xs_exact,
           "x":x_exact,"y":y_exact,"x0":x0_exact}
"""
    )


md("## Symbolic Step Recursion Verification")
md(r"""For $1\leq k\leq N-2$, verify
$$V_{k+1}-V_{k}=
\frac{2N+1}{(2N-k-1)(2N-k)}I^{f}_{x_{\star},x_{k+1}}
+\frac{2N}{(2N-k-1)(2N-k)}I^{g}_{x_{\star},x_{k+1}}
+\frac{k+1}{2N-k}I^{f}_{x_{k},x_{k+1}}
+\frac{k}{2N-k}I^{g}_{x_{k},x_{k+1}}-Q_{k+1}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must vanish in every coordinate. This range is empty for $N\leq2$.
""")
code(
    context_code("step")
    + """
LHS = potential(e_exact,y_exact,K+1)-potential(e_exact,x_exact,K)
RHS = step_rhs(e_exact,K)
diff = LHS-RHS
proof_results = [check_identity("Interior step",LHS,RHS,e_exact)]
"""
)
md("## Base Case and Boundary Symbolic Verification")
md(r"""For $N\geq2$, verify
$$V_{1}-V_{0}=
\frac1{2N}I^{f}_{x_{\star},x_{0}}
+\frac{2N+1}{(2N-1)2N}I^{f}_{x_{\star},x_{1}}
+\frac1{2N}I^{f}_{x_{0},x_{1}}
+\frac1{2N-1}I^{g}_{x_{\star},x_{1}}-Q_{1}.$$
The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero. Nonpositive residuals and positive coefficients imply $V_{1}\leq V_{0}=0$.
""")
code(
    context_code("base", True)
    + """
LHS = potential(e_exact,y_exact,1)
RHS = base_rhs(e_exact)
diff = LHS-RHS
proof_results.append(check_identity("Base",LHS,RHS,e_exact))
"""
)
md("### Boundary Identity Symbolic Verification")
md(r"""For $N\geq2$, verify
$$V_{N}-V_{N-1}=
\frac1{N+1}I^{f}_{x_{\star},x_{N}}
+\frac2{N+1}I^{g}_{x_{\star},x_{N}}
+\frac{N}{N+1}I^{f}_{x_{N-1},x_{N}}
+\frac{N-1}{N+1}I^{g}_{x_{N-1},x_{N}}-Q_{N}.$$
Here $V_{N}=h(x_{N})-h_{\star}-L\|d_{0}\|^2/(4N)$. The residual $\mathrm{LHS}-\mathrm{RHS}$ must simplify to zero.
""")
code(
    context_code("boundary")
    + """
LHS = terminal_potential(e_exact)-potential(e_exact,x_exact,NN-1)
RHS = terminal_rhs(e_exact)
diff = LHS-RHS
proof_results.append(check_identity("Boundary",LHS,RHS,e_exact))
"""
)
md("### Single-step horizon")
md(r"""For $N=1$, the first and last step coincide:
$$V_{1}-V_{0}=
\frac12 I^{f}_{x_{\star},x_{0}}
+\frac12 I^{f}_{x_{\star},x_{1}}
+\frac12 I^{f}_{x_{0},x_{1}}
+I^{g}_{x_{\star},x_{1}}-Q_{1}.$$
Here $V_{1}=h(x_{1})-h_{\star}-L\|d_{0}\|^2/4$. Verify all components of $\mathrm{LHS}-\mathrm{RHS}=0$ after substituting $N=1$.
""")
code(
    context_code("single", True)
    + """
LHS = terminal_potential(e_exact)
RHS = single_rhs(e_exact)
diff = LHS-RHS
proof_results.append(check_identity("N=1",LHS,RHS,e_exact,
    values={**symbolic_values,"N":sp.S.One}))
"""
)
md(r"""### Signs, domains, and telescoping

For $1\leq i\leq N$, the denominators $2N-i$, $2N+1-i$, $2N+1$, $2N$, and $L$ are strictly positive. The numerators of $\alpha$, $\gamma$, and $\delta$ are positive; $\beta_{0}=0$ and all used $\beta$ are positive. Each $c_{1,i}$ and $c_{3,i}$ is positive. Both summands in $c_{2,i}$ are nonnegative and its second summand is positive. These elementary domain facts establish every sign used above.

The PEPFlow identities are exact rational identities in symbolic $N,k,L$; no finite-horizon sampling is used to establish them. Combining those identities with convex interpolation gives $V_{i}-V_{i-1}\leq0$. Therefore
$$
h(x_{N})-h_{\star}
=V_{N}+\frac{L}{4N}\|d_{0}\|^2
\leq\frac{L}{4N}\|d_{0}\|^2
\leq\frac{LR^2}{4N}.
$$
This also covers $R=0$; no division by $R$ occurs. For $N=2$ the generic interior range is empty and the separate base and terminal identities suffice.

The numerical certificate and analytic Lyapunov proof are separately verified. A symbolic global matrix certificate was not separately certified; its status remains distinct from the completed local proof.
""")
code("""assert all(result["gram_zero"] and result["function_zero"] and result["offset_zero"]
           for result in proof_results)
print("Exact step/base/boundary/N=1 identities verified in all scalar coordinates.")
print("By the stated domain signs, each increment is nonpositive.")
print("Theorem:", "h(x_N)-h(x_star) <= L*R**2/(4*N)")
print("LaTeX theorem:",r"h(x_{N})-h(x_{\\star})\\leq\\frac{LR^{2}}{4N}")
""")
nbf.write(nb, path)
print("Final notebook source written:", path)
