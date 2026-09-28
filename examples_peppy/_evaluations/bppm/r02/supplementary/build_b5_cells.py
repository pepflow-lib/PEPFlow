import json
from pathlib import Path

root = Path.cwd()
cells = [
    {
        "kind": "markdown",
        "source": "## Closed-form Lyapunov derivation\nB4's four-vector expression simplifies exactly to a shifted Bregman potential. The coefficients are candidates until the symbolic identities below hold; no finite-horizon fit is used as proof.",
    },
    {
        "kind": "code",
        "source": """b4 = json.loads((notebook_dir / "state/bppm_b4.json").read_text())
assert b4["certificate_id"] == certificate["certificate_id"]
assert b4["numerical_reconstruction"]["required_indices"] == list(range(N_int+1))
assert all(max(row.values()) <= 1e-4 for row in component_residuals.values())
proof_checks = {name: False for name in ("step","base","boundary","signs","domain","normalization")}
proof_residuals = {}
j_symbol, N_symbol = sp.symbols("j N", integer=True, positive=True)
a_symbol = sp.Symbol("alpha", positive=True)
R_symbol = sp.Symbol("R", nonnegative=True)
a_parameter = pf.Parameter("alpha")
j_parameter = pf.Parameter("j")
N_parameter = pf.Parameter("N")
R_parameter = pf.Parameter("R")

def divergence(kernel,u,v):
    return kernel(u)-kernel(v)-kernel.grad(v)*(u-v)

def convex_residual(function,u,v):
    return function(v)-function(u)+function.grad(v)*(u-v)

def shifted_potential(function,kernel,x,x0,xs,index):
    return index/N_parameter*(function(x)-function(xs))+(divergence(kernel,xs,x)-divergence(kernel,xs,x0))/(a_parameter*N_parameter)

def verify_exact(name,expression,manager,context):
    value=manager.eval_scalar(pf.Scalar.zero()+expression,sympy_mode=True)
    gram=sp.Matrix(value.inner_prod_coords).applyfunc(sp.simplify)
    functions=sp.Matrix(list(value.func_coords)).applyfunc(sp.simplify)
    offset=sp.simplify(sp.sympify(value.offset))
    assert all(term==0 for term in [*gram,*functions,offset]), name
    labels=[str(v) for v in context.basis_vectors()]
    pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(gram,dtype=object),labels,labels))
    print(name,"function residual:",functions.T,"; offset:",offset)
    proof_residuals[name]={"gram_exact_zero":True,"function_exact_zero":True,"offset_exact_zero":True}
    return True""",
    },
    {
        "kind": "markdown",
        "source": r"""The exact candidate, valid for $0\le k\le N$, is
$$V_{k}=\frac{k}{N}(f(x_{k})-f(x_{\star}))+
\frac{D_h(x_{\star},x_{k})-D_h(x_{\star},x_{0})}{\alpha N}.$$
Indeed, expanding the difference of Bregman distances gives exactly the four-vector numerator from B4. Adding the constant $D_h(x_{\star},x_{0})/(\alpha N)$ gives the equivalent unshifted potential
$$\Phi_{k}=\frac{k}{N}(f(x_{k})-f(x_{\star}))+\frac{D_h(x_{\star},x_{k})}{\alpha N}.$$
The next calculation verifies the coefficient identity and all terms of the one-step recursion for symbolic $j,N,\alpha$.""",
    },
    {"kind": "markdown", "source": "## Symbolic Step Recursion Verification"},
    {
        "kind": "markdown",
        "source": r"""For $1\le j\le N$, define $C^q_{u,v}=q(v)-q(u)+\langle\nabla q(v),u-v\rangle\le0$. The exact identity is
$$V_{j}-V_{j-1}=\frac1N C^f_{x_{\star},x_j}+\frac{j-1}{N}C^f_{x_{j-1},x_j}
+\frac{j}{\alpha N}C^h_{x_j,x_{j-1}}+\frac{j-1}{\alpha N}C^h_{x_{j-1},x_j}.$$
There is no square remainder. The code substitutes the exact Bregman optimality relation and checks that $\mathrm{LHS}-\mathrm{RHS}$ vanishes in every coordinate.""",
    },
    {
        "kind": "code",
        "source": """ctx_step = pf.PEPContext("bppm_symbolic_step").set_as_current()
f_step = pf.ConvexFunction(is_basis=True,tags=["f_{step}"])
h_step = pf.ConvexFunction(is_basis=True,tags=["h_{step}"])
x0_step = pf.Vector(is_basis=True,tags=["x_{0}"])
xprev_step = pf.Vector(is_basis=True,tags=["x_{j-1}"])
xs_step = f_step.set_stationary_point("x_{star}")
xnext_step = f_step.bregman_prox(xprev_step,cast(Number,a_parameter),h_step,tag="x_{j}")
V_prev = shifted_potential(f_step,h_step,xprev_step,x0_step,xs_step,j_parameter-1)
V_next = shifted_potential(f_step,h_step,xnext_step,x0_step,xs_step,j_parameter)
step_LHS = V_next-V_prev
step_RHS = (convex_residual(f_step,xs_step,xnext_step)/N_parameter
    +(j_parameter-1)/N_parameter*convex_residual(f_step,xprev_step,xnext_step)
    +j_parameter/(a_parameter*N_parameter)*convex_residual(h_step,xnext_step,xprev_step)
    +(j_parameter-1)/(a_parameter*N_parameter)*convex_residual(h_step,xprev_step,xnext_step))
diff_step = step_LHS-step_RHS
q_step = h_step.grad(x0_step)-h_step.grad(xnext_step)
p_step = xs_step-xnext_step
r_step = xnext_step-x0_step
t_step = h_step.grad(x0_step)
expanded_V_next = (q_step*p_step+r_step*t_step+h_step(x0_step)-h_step(xnext_step))/(a_parameter*N_parameter)+j_parameter/N_parameter*(f_step(xnext_step)-f_step(xs_step))
step_parameters = {"alpha":a_symbol,"j":j_symbol,"N":N_symbol}
pm_step = pf.ExpressionManager(ctx_step,resolve_parameters=cast(dict[str,pf.NUMERICAL_TYPE],step_parameters))
verify_exact("Four-vector formula",expanded_V_next-V_next,pm_step,ctx_step)
proof_checks["step"] = verify_exact("Step",diff_step,pm_step,ctx_step)""",
    },
    {"kind": "markdown", "source": "## Base Case and Boundary Symbolic Verification"},
    {
        "kind": "markdown",
        "source": r"""In a separate initial-step context we check
$$V_{0}=0,\qquad V_{1}-V_{0}=\frac1N C^f_{x_{\star},x_1}+\frac1{\alpha N}C^h_{x_1,x_0}.$$
For the unshifted potential the initial normalization is
$$\Phi_{0}-\frac{R}{\alpha N}=\frac{D_h(x_{\star},x_0)-R}{\alpha N}\le0.$$
Each displayed identity is checked as a zero residual, with $N,\alpha,R$ symbolic. This separate first-step check also covers $N=1$.""",
    },
    {
        "kind": "code",
        "source": """ctx_base = pf.PEPContext("bppm_symbolic_base").set_as_current()
f_base = pf.ConvexFunction(is_basis=True,tags=["f_{base}"])
h_base = pf.ConvexFunction(is_basis=True,tags=["h_{base}"])
x0_base = pf.Vector(is_basis=True,tags=["x_{0}"])
xs_base = f_base.set_stationary_point("x_{star}")
x1_base = f_base.bregman_prox(x0_base,cast(Number,a_parameter),h_base,tag="x_{1}")
V0_base = shifted_potential(f_base,h_base,x0_base,x0_base,xs_base,0)
V1_base = shifted_potential(f_base,h_base,x1_base,x0_base,xs_base,1)
base_LHS = V1_base-V0_base
base_RHS = convex_residual(f_base,xs_base,x1_base)/N_parameter+convex_residual(h_base,x1_base,x0_base)/(a_parameter*N_parameter)
diff_base = base_LHS-base_RHS
Phi0_base = divergence(h_base,xs_base,x0_base)/(a_parameter*N_parameter)
initial_residual = divergence(h_base,xs_base,x0_base)-R_parameter
normalization_LHS = Phi0_base-R_parameter/(a_parameter*N_parameter)
normalization_RHS = initial_residual/(a_parameter*N_parameter)
base_parameters = {"alpha":a_symbol,"N":N_symbol,"R":R_symbol}
pm_base = pf.ExpressionManager(ctx_base,resolve_parameters=cast(dict[str,pf.NUMERICAL_TYPE],base_parameters))
initial_zero = verify_exact("Initial V0",V0_base-pf.Scalar.zero(),pm_base,ctx_base)
first_step_zero = verify_exact("Base first step",diff_base,pm_base,ctx_base)
proof_checks["base"] = initial_zero and first_step_zero
proof_checks["normalization"] = verify_exact("Initial normalization",normalization_LHS-normalization_RHS,pm_base,ctx_base)""",
    },
    {"kind": "markdown", "source": "### Boundary Identity Symbolic Verification"},
    {
        "kind": "markdown",
        "source": r"""At the terminal point, with no extra recurrence assumed,
$$f(x_N)-f(x_{\star})-\frac{R}{\alpha N}=V_N+
\frac{D_h(x_{\star},x_0)-R}{\alpha N}
+\frac{C^h_{x_{\star},x_N}}{\alpha N}.$$
The last residual is $C^h_{x_{\star},x_N}=-D_h(x_{\star},x_N)\le0$. The code checks $\mathrm{LHS}-\mathrm{RHS}=0$ in the terminal symbolic context, including its constant term.""",
    },
    {
        "kind": "code",
        "source": """ctx_boundary = pf.PEPContext("bppm_symbolic_boundary").set_as_current()
f_boundary = pf.ConvexFunction(is_basis=True,tags=["f_{boundary}"])
h_boundary = pf.ConvexFunction(is_basis=True,tags=["h_{boundary}"])
x0_boundary = pf.Vector(is_basis=True,tags=["x_{0}"])
xN_boundary = pf.Vector(is_basis=True,tags=["x_{N}"])
xs_boundary = f_boundary.set_stationary_point("x_{star}")
VN_boundary = shifted_potential(f_boundary,h_boundary,xN_boundary,x0_boundary,xs_boundary,N_parameter)
metric_boundary = f_boundary(xN_boundary)-f_boundary(xs_boundary)
terminal_interpolation = convex_residual(h_boundary,xs_boundary,xN_boundary)
initial_boundary = divergence(h_boundary,xs_boundary,x0_boundary)-R_parameter
boundary_LHS = metric_boundary-R_parameter/(a_parameter*N_parameter)
boundary_RHS = VN_boundary+initial_boundary/(a_parameter*N_parameter)+terminal_interpolation/(a_parameter*N_parameter)
diff_boundary = boundary_LHS-boundary_RHS
boundary_parameters = {"alpha":a_symbol,"N":N_symbol,"R":R_symbol}
pm_boundary = pf.ExpressionManager(ctx_boundary,resolve_parameters=cast(dict[str,pf.NUMERICAL_TYPE],boundary_parameters))
proof_checks["boundary"] = verify_exact("Boundary",diff_boundary,pm_boundary,ctx_boundary)
verify_exact("Terminal residual sign identity",terminal_interpolation+divergence(h_boundary,xs_boundary,xN_boundary),pm_boundary,ctx_boundary)""",
    },
    {
        "kind": "markdown",
        "source": r"""### Signs, domain, and telescoping conclusion
All four local weights are nonnegative because $j\ge1$, $N\ge1$, and $\alpha>0$; $\alpha N$ is strictly positive. Convexity makes every $C^f$ and $C^h$ nonpositive. Exact proximal optimality supplies $\nabla h(x_j)=\nabla h(x_{j-1})-\alpha\nabla f(x_j)$, the only algorithmic relation used by the step calculation. Thus $V_j\le V_{j-1}$, so $V_N\le V_0=0$.

The initial residual is nonpositive by the supplied radius assumption and the terminal residual is nonpositive by convexity of $h$. The verified boundary identity therefore proves
$$0\le f(x_N)-f(x_{\star})\le\frac{R}{\alpha N}.$$
The lower bound uses that $x_{\star}$ minimizes $f$. This includes $R=0$ and $N=1$ without division by $R$ or by $N-1$. Equivalently, $f(x_N)-f(x_{\star})\le\Phi_N\le\Phi_0\le R/(\alpha N)$.""",
    },
    {
        "kind": "code",
        "source": """local_weights = [1/N_symbol,(j_symbol-1)/N_symbol,j_symbol/(a_symbol*N_symbol),(j_symbol-1)/(a_symbol*N_symbol)]
assert all(sp.simplify(weight).is_nonnegative is True for weight in local_weights)
assert (a_symbol*N_symbol).is_positive is True
proof_checks["signs"] = True
proof_checks["domain"] = True
assert all(proof_checks.values())
print("Exact proof checks:",proof_checks)
print("All step, initial, first-step and terminal identities are zero in every scalar component.")
print("Lyapunov: V_k = k/N*(f(x_k)-f_star) + (D_h(x_star,x_k)-D_h(x_star,x_0))/(alpha*N).")
print("Theorem: 0 <= f(x_N)-f_star <= R/(alpha*N), for N>=1, alpha>0, R>=0.")
print(sp.latex(sp.Le(sp.Symbol("f_N")-sp.Symbol("f_star"),R_symbol/(a_symbol*N_symbol))))""",
    },
]
(root / "supplementary/b5_cells.json").write_text(json.dumps(cells, indent=2))
print("Created symbolic proof cells.")
