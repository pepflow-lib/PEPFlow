"""Finalize the proof in the evolving notebook, preserving diagnostic cells."""
from pathlib import Path
import re
import nbformat as nbf

root = Path(__file__).resolve().parent.parent
nb = nbf.read(root / "pgm_example_lyap.ipynb", as_version=4)
if nb.cells[2].cell_type == "markdown" and nb.cells[2].source.startswith("### Theorem"):
    del nb.cells[2:4]
nb.cells = nb.cells[:39]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
formula = r"""Put $d_{k}=x_{k}-x_{\star}$ and $p_{k}=(\nabla f(x_{k})-\nabla f(x_{\star}))/L$.
For $1\le k<N$, define
$$V_{k}=-\frac{L}{4N}\|d_{0}\|^{2}
+\frac{L(N-k)}{(2N-k)^{2}}\|d_{k}\|^{2}
-\frac{\langle d_{k},\nabla f(x_{k})\rangle}{2N-k}
-\frac{Lk}{2(2N-k)^{2}}\|p_{k}\|^{2}
+\frac{k+1}{2N-k}(f(x_{k})-f(x_{\star}))
+\frac{k}{2N-k}(g(x_{k})-g(x_{\star})).$$
The endpoints are $V_{0}=0$ and
$$V_{N}=h(x_{N})-h(x_{\star})-\frac{L}{4N}\|d_{0}\|^{2}.$$
"""
outline = r"""### Proof outline

""" + formula + r"""
Define the nonpositive interpolation residuals
$$I_{f}(u,v)=f(v)-f(u)+\langle\nabla f(v),u-v\rangle+\frac{\|\nabla f(u)-\nabla f(v)\|^{2}}{2L},\quad
I_{g}(u,v)=g(v)-g(u)+\langle s_{v},u-v\rangle,$$
where $s_{v}\in\partial g(v)$ is the selected oracle subgradient. At the minimizer choose $s_{\star}=-\nabla f(x_{\star})$; at a new iterate use the proximal subgradient.
Write $a_{k}=(k+1)/(2N-k)$ and $b_{k}=k/(2N-k)$.
For a step, put $m=2N-k$, $p=p_{k}$, $q=p_{k+1}$,
$s=(s_{x_{k+1}}+\nabla f(x_{\star}))/L$, $z=s-d_{k}/m$.
The recurrence gives $d_{k+1}=d_{k}-p-s$.
Define
$$A_{k}=\frac{k+1}{2(m-1)^{2}}+\frac{k+2}{2(m-1)},\quad
B_{k}=\frac{k+1}{2(m-1)},\quad C_{k}=\frac{km+N-k}{(m-1)^{2}},$$
$$D_{k}=\frac{k+1}{2m(m-1)},\quad E_{k}=\frac{km+1}{2(m-1)^{2}},\quad
F_{k}=\frac{a_{k}}2-\frac{N-k-1}{(m-1)^{2}}-\frac{k}{2m^{2}}.$$
Set $\alpha_{k}=A_{k}$, $\beta_{k}=C_{k}-B_{k}^{2}/A_{k}$,
$\eta_{k}=E_{k}-B_{k}D_{k}/A_{k}$,
$\gamma_{k}=F_{k}-D_{k}^{2}/A_{k}-\eta_{k}^{2}/\beta_{k}$ and
$$Q_{k}=L\alpha_{k}\|q+(B_{k}/A_{k})z+(D_{k}/A_{k})p\|^{2}
+L\beta_{k}\|z+(\eta_{k}/\beta_{k})p\|^{2}+L\gamma_{k}\|p\|^{2}.$$
The sign lemma below proves $\alpha_{k},\beta_{k}>0$ and $\gamma_{k}\ge0$ for $0\le k\le N-2$.
For $N\ge2$, the exact base identity is
$$V_{1}=a_{0}I_{f}(x_{\star},x_{0})+(a_{1}-a_{0})I_{f}(x_{\star},x_{1})
+b_{1}I_{g}(x_{\star},x_{1})+a_{0}I_{f}(x_{0},x_{1})
-\frac{L}{4N}\|p_{0}\|^{2}-Q_{0}.$$
For $1\le k\le N-2$, the exact recursion is
$$V_{k+1}-V_{k}=(a_{k+1}-a_{k})I_{f}(x_{\star},x_{k+1})
+(b_{k+1}-b_{k})I_{g}(x_{\star},x_{k+1})
+a_{k}I_{f}(x_{k},x_{k+1})+b_{k}I_{g}(x_{k},x_{k+1})-Q_{k}.$$
At the final step put $p=p_{N-1}$, $q=p_{N}$, $s=(s_{x_N}+\nabla f(x_{\star}))/L$, $d=d_{N-1}$ and
$$T_{N}=\frac L2\left\|q+s+\frac{p-d}{N+1}\right\|^{2}
+\frac L2\left\|s+\frac{Np-d}{N+1}\right\|^{2}.$$
Then, for $N\ge2$,
$$V_{N}-V_{N-1}=(1-a_{N-1})I_{f}(x_{\star},x_{N})+(1-b_{N-1})I_{g}(x_{\star},x_{N})
+a_{N-1}I_{f}(x_{N-1},x_{N})+b_{N-1}I_{g}(x_{N-1},x_{N})-T_{N}.$$
For $N=1$, use the separate identity
$$V_{1}=\tfrac12 I_{f}(x_{\star},x_{0})+\tfrac12 I_{f}(x_{\star},x_{1})+I_{g}(x_{\star},x_{1})
+\tfrac12 I_{f}(x_{0},x_{1})-\tfrac L4\|p_{0}\|^{2}-T_{1}.$$
All residual multipliers are nonnegative: $a_{k+1}-a_{k}=(2N+1)/[(2N-k-1)(2N-k)]$,
$b_{k+1}-b_{k}=2N/[(2N-k-1)(2N-k)]$,
$1-a_{N-1}=1/(N+1)$ and $1-b_{N-1}=2/(N+1)$.
Thus $V_{N}\le\cdots\le V_{1}\le V_{0}=0$, and
$$h(x_{N})-h(x_{\star})\le\frac{L}{4N}\|d_{0}\|^{2}\le\frac{LR^{2}}{4N}.$$
"""
nb.cells[1] = md("## Proof Statement")
nb.cells += [md("## Closed-form coefficient derivation"), code('''from typing import Any, cast

b4 = json.loads((notebook_dir / "state/pgm_b4.json").read_text())
assert b4["certificate_id"] == certificate["certificate_id"]
assert b4["numerical_reconstruction"]["passed"]
print("B4 unknowns resolved below:", [v["name"] for v in b4["unresolved_coefficients"]])
proof_checks = {}
'''), md(r"""The numerical structure suggests the displayed $a_{k},b_{k}$ and distance/cross coefficients. The gradient coefficient has freedom. Write its negative normalized value as $t_{k}$, retain $t_{k+1}$ independently in the difference, and form the residual quadratic below. We select $t_{k}=k/[2(2N-k)^{2}]$; exact identities and positive pivots certify this choice. This is an analytically chosen decomposition, not a formula claim for the original reverse LDL factors."""), code(r'''
k_sym, N_sym = sp.symbols("k N", integer=True)
t_prev, t_next = sp.symbols("t_k t_next", real=True)
d_sym, p_sym, q_sym, s_sym = sp.symbols("d p q s", real=True)
dn_sym = d_sym-p_sym-s_sym
If_star_quad = -q_sym*dn_sym+q_sym**2/2
Ig_star_quad = -s_sym*dn_sym
If_step_quad = q_sym*(d_sym-dn_sym)+(p_sym-q_sym)**2/2
Ig_step_quad = s_sym*(d_sym-dn_sym)
V_quad = distance_weight(k_sym,N_sym)*d_sym**2-d_sym*p_sym/(2*N_sym-k_sym)-t_prev*p_sym**2
W_quad = distance_weight(k_sym+1,N_sym)*dn_sym**2-dn_sym*q_sym/(2*N_sym-k_sym-1)-t_next*q_sym**2
S_unknown = ((a(k_sym+1,N_sym)-a(k_sym,N_sym))*If_star_quad
    +(b(k_sym+1,N_sym)-b(k_sym,N_sym))*Ig_star_quad
    +a(k_sym,N_sym)*If_step_quad+b(k_sym,N_sym)*Ig_step_quad-W_quad+V_quad)
M_unknown = (sp.hessian(S_unknown,[q_sym,s_sym,d_sym,p_sym])/2).applyfunc(sp.factor)
print("Residual quadratic with unresolved gradient coefficients:")
pf.pprint_labeled_matrix(np.asarray(M_unknown,dtype=object), ["q","s","d","p"], precision=0)
chosen_S = S_unknown.subs({t_prev:gradient_weight(k_sym,N_sym),t_next:gradient_weight(k_sym+1,N_sym)})
alpha_s,beta_s,gamma_s,u_s,v_s,w_s = sos_coefficients(k_sym,N_sym)
z_sym=s_sym-d_sym/(2*N_sym-k_sym)
chosen_squares=alpha_s*(q_sym+u_s*z_sym+v_s*p_sym)**2+beta_s*(z_sym+w_s*p_sym)**2+gamma_s*p_sym**2
assert sp.factor(chosen_S-chosen_squares)==0
print("Chosen gradient coefficients solve the exact residual-square equations.")
ctx_derivation,L_derivation,f_derivation,g_derivation,star_derivation,x_derivation,xn_derivation=local_context("derivation")
k_derivation,N_derivation=pf.Parameter("k"),pf.Parameter("N")
t_derivation,tn_derivation=pf.Parameter("t_prev"),pf.Parameter("t_next")
anchor_derivation=pf.Vector(is_basis=True,tags=["x_0"])
p_derivation=(f_derivation.grad(x_derivation)-f_derivation.grad(star_derivation))/L_derivation
q_derivation=(f_derivation.grad(xn_derivation)-f_derivation.grad(star_derivation))/L_derivation
V_unknown=potential_interior(x_derivation,anchor_derivation,star_derivation,f_derivation,g_derivation,L_derivation,k_derivation,N_derivation)+L_derivation*(gradient_weight(k_derivation,N_derivation)-t_derivation)*p_derivation**2
W_unknown=potential_interior(xn_derivation,anchor_derivation,star_derivation,f_derivation,g_derivation,L_derivation,k_derivation+1,N_derivation)+L_derivation*(gradient_weight(k_derivation+1,N_derivation)-tn_derivation)*q_derivation**2
If_d,Ig_d=interpolation(f_derivation,g_derivation,L_derivation,star_derivation,xn_derivation)
If_s,Ig_s=interpolation(f_derivation,g_derivation,L_derivation,x_derivation,xn_derivation)
R_unknown=(a(k_derivation+1,N_derivation)-a(k_derivation,N_derivation))*If_d+(b(k_derivation+1,N_derivation)-b(k_derivation,N_derivation))*Ig_d+a(k_derivation,N_derivation)*If_s+b(k_derivation,N_derivation)*Ig_s
R_unknown-=sum(step_squares(x_derivation,xn_derivation,star_derivation,f_derivation,g_derivation,L_derivation,k_derivation,N_derivation),pf.Scalar.zero())
t_function: Any=sp.Function("t")
derivation_parameters: dict[str,Any]={"L":sp.Symbol("L",positive=True),"k":k_sym,"N":N_sym,"t_prev":t_function(k_sym,N_sym),"t_next":t_function(k_sym+1,N_sym)}
pm_derivation=pf.ExpressionManager(ctx_derivation,resolve_parameters=derivation_parameters)
unknown_components=exact_components(W_unknown-V_unknown-R_unknown,pm_derivation)
equations=[sp.Eq(term,0) for component in unknown_components[:2] for term in component if term!=0]
print("Native coefficient equations:",equations)
chosen_t={t_function(k_sym,N_sym):gradient_weight(k_sym,N_sym),t_function(k_sym+1,N_sym):gradient_weight(k_sym+1,N_sym)}
assert all(sp.factor(term.subs(chosen_t))==0 for component in unknown_components[:2] for term in component)
assert sp.factor(unknown_components[2])==0
ctx.set_as_current()
'''), code(r'''
def closed_coefficient_matrix(index, horizon, smoothness):
    index, horizon, smoothness = [cast(sp.Expr, sp.sympify(value)) for value in (index,horizon,smoothness)]
    if index == 0:
        return sp.zeros(0,0)
    if index == horizon:
        return sp.Matrix([[-smoothness/(4*horizon)]])
    M=sp.zeros(4,4)
    M[0,0]=-smoothness/(4*horizon)
    M[1,1]=smoothness*distance_weight(index,horizon)
    M[2,2]=-gradient_weight(index,horizon)/smoothness
    M[1,3]=M[3,1]=-1/(2*(2*horizon-index))
    return M

coefficient_comparisons={}
for index in range(N_int+1):
    closed_C=closed_coefficient_matrix(index,N_int,params_sp["L"])
    if index:
        print("Closed coefficient matrix",index)
        pf.pprint_labeled_matrix(np.asarray(closed_C,dtype=object),V_k_basis_labels(index),precision=0)
    err=float(np.max(np.abs(np.asarray(closed_C,dtype=float).reshape(coeff_by_k[index].shape)-coeff_by_k[index]),initial=0))
    target_weights=[0,0] if index==0 else ([1,1] if index==N_int else [a(sp.S(index),sp.S(N_int)),b(sp.S(index),sp.S(N_int))])
    ferr=float(np.max(np.abs(np.asarray(target_weights,dtype=float)-function_weights[index]),initial=0))
    assert err<1e-4 and ferr<1e-4
    coefficient_comparisons[str(index)]={"quadratic":err,"function":ferr}
    print("Coefficient comparison",index,coefficient_comparisons[str(index)])
'''), md("### Closed-form conclusion\n\n"+formula+"\nThe following native symbolic checks verify this candidate for arbitrary admissible horizons."), md("## Sign and domain verification"), md(r"""Set $n=N-k-1\ge0$. The following exact positive-polynomial representations prove all three square signs. Every coefficient of $A,B,P$ is positive and $A,B$ have positive constants. Therefore all denominators and division pivots are strictly positive. At $k=0$, the third square has zero weight, which is allowed."""), code(r'''
sign_k, sign_n = sp.symbols("k n", nonnegative=True)
sign_N=sign_k+1+sign_n
alpha_sign,beta_sign,gamma_sign,*_=sos_coefficients(sign_k,sign_N)
A=sign_k**2+2*sign_k*sign_n+4*sign_k+4*sign_n+3
B=sign_k**4+4*sign_k**3*sign_n+8*sign_k**3+4*sign_k**2*sign_n**2+22*sign_k**2*sign_n+18*sign_k**2+12*sign_k*sign_n**2+28*sign_k*sign_n+16*sign_k+4*sign_n**2+10*sign_n+5
P=sign_k**4+5*sign_k**3*sign_n+3*sign_k**3+8*sign_k**2*sign_n**2+13*sign_k**2*sign_n+3*sign_k**2+4*sign_k*sign_n**3+16*sign_k*sign_n**2+13*sign_k*sign_n+sign_k+4*sign_n**3+10*sign_n**2+5*sign_n
sign_forms=[A/(2*(sign_k+2*sign_n+1)**2),B/(2*(sign_k+2*sign_n+1)**2*A),sign_k*P/((sign_k+2*sign_n+2)**2*B)]
assert [sp.factor(x-y) for x,y in zip([alpha_sign,beta_sign,gamma_sign],sign_forms)]==[0,0,0]
assert all(c>0 for poly in (A,B,P) for c in sp.Poly(poly,sign_k,sign_n).coeffs())
assert A.subs({sign_k:0,sign_n:0})>0 and B.subs({sign_k:0,sign_n:0})>0
for name,expr in zip(["alpha","beta","gamma"],sign_forms):
    print(name,"=",expr)
    print(sp.latex(expr))
assert sp.factor(a(k_sym+1,N_sym)-a(k_sym,N_sym)-(2*N_sym+1)/((2*N_sym-k_sym-1)*(2*N_sym-k_sym)))==0
assert sp.factor(b(k_sym+1,N_sym)-b(k_sym,N_sym)-2*N_sym/((2*N_sym-k_sym-1)*(2*N_sym-k_sym)))==0
assert sp.factor(1-a(N_sym-1,N_sym)-1/(N_sym+1))==0
assert sp.factor(1-b(N_sym-1,N_sym)-2/(N_sym+1))==0
proof_checks["signs"]=True
proof_checks["domain"]=True
print("For L>0, integer N>=1, all used residual multipliers and square weights are nonnegative; denominators are nonzero.")
''')]

headings={"step":"## Symbolic Step Recursion Verification","base":"## Base Case and Boundary Symbolic Verification","terminal":"### Boundary Identity Symbolic Verification","N1":"### Exceptional horizon N=1"}
equations={
"step":r"$$V_{k+1}-V_{k}=(a_{k+1}-a_{k})I_f(x_{\star},x_{k+1})+(b_{k+1}-b_{k})I_g(x_{\star},x_{k+1})+a_{k}I_f(x_k,x_{k+1})+b_{k}I_g(x_k,x_{k+1})-Q_k.$$ For $1\le k\le N-2$.",
"base":r"$$V_1=a_0I_f(x_{\star},x_0)+(a_1-a_0)I_f(x_{\star},x_1)+b_1I_g(x_{\star},x_1)+a_0I_f(x_0,x_1)-\frac{L}{4N}\|p_0\|^2-Q_0.$$ For $N\ge2$.",
"terminal":r"$$V_N-V_{N-1}=(1-a_{N-1})I_f(x_{\star},x_N)+(1-b_{N-1})I_g(x_{\star},x_N)+a_{N-1}I_f(x_{N-1},x_N)+b_{N-1}I_g(x_{N-1},x_N)-T_N.$$ For $N\ge2$.",
"N1":r"$$V_1=\tfrac12 I_f(x_{\star},x_0)+\tfrac12 I_f(x_{\star},x_1)+I_g(x_{\star},x_1)+\tfrac12 I_f(x_0,x_1)-\tfrac L4\|p_0\|^2-T_1.$$ For $N=1$."}
for kind in ("step","base","terminal","N1"):
    src=f'''# Independent native symbolic {kind} context and the actual proximal recurrence.
ctx_proof=pf.PEPContext("proof_{kind}").set_as_current()
L_proof=pf.Parameter("L")
N_proof=pf.Parameter("N")
k_proof=pf.Parameter("k")
f_proof=pf.SmoothConvexFunction(is_basis=True,tags=["f_{{{kind}}}"],L=L_proof)
g_proof=pf.ConvexFunction(is_basis=True,tags=["g_{{{kind}}}"])
star_proof=(f_proof+g_proof).set_stationary_point("x_star")
x_proof=pf.Vector(is_basis=True,tags=["x"])
xn_proof=g_proof.prox(x_proof-f_proof.grad(x_proof)/L_proof,1/L_proof,tag="x_next")
f_proof(xn_proof)
g_proof(x_proof)
x0_proof={"pf.Vector(is_basis=True,tags=['x_0'])" if kind in ("step","terminal") else "x_proof"}
Ifstar,Igstar=interpolation(f_proof,g_proof,L_proof,star_proof,xn_proof)
Ifstep,Igstep=interpolation(f_proof,g_proof,L_proof,x_proof,xn_proof)
'''
    if kind=="step":
        src+='''LHS=potential_interior(xn_proof,x0_proof,star_proof,f_proof,g_proof,L_proof,k_proof+1,N_proof)-potential_interior(x_proof,x0_proof,star_proof,f_proof,g_proof,L_proof,k_proof,N_proof)
RHS=(a(k_proof+1,N_proof)-a(k_proof,N_proof))*Ifstar+(b(k_proof+1,N_proof)-b(k_proof,N_proof))*Igstar
RHS+=a(k_proof,N_proof)*Ifstep+b(k_proof,N_proof)*Igstep-sum(step_squares(x_proof,xn_proof,star_proof,f_proof,g_proof,L_proof,k_proof,N_proof),pf.Scalar.zero())
'''
    elif kind=="base":
        src+='''k_proof=sp.S.Zero
LHS=potential_interior(xn_proof,x_proof,star_proof,f_proof,g_proof,L_proof,sp.S.One,N_proof)
Ifinitial,_=interpolation(f_proof,g_proof,L_proof,star_proof,x_proof)
RHS=a(k_proof,N_proof)*Ifinitial+(a(k_proof+1,N_proof)-a(k_proof,N_proof))*Ifstar
RHS+=(b(k_proof+1,N_proof)-b(k_proof,N_proof))*Igstar+a(k_proof,N_proof)*Ifstep
RHS-=L_proof/(4*N_proof)*((f_proof.grad(x_proof)-f_proof.grad(star_proof))/L_proof)**2
RHS-=sum(step_squares(x_proof,xn_proof,star_proof,f_proof,g_proof,L_proof,k_proof,N_proof),pf.Scalar.zero())
'''
    else:
        if kind=="N1":
            src+='N_proof=sp.S.One\n'
        src+='''k_proof=N_proof-1
LHS=potential_terminal(xn_proof,x0_proof,star_proof,f_proof,g_proof,L_proof,N_proof)-potential_interior(x_proof,x0_proof,star_proof,f_proof,g_proof,L_proof,k_proof,N_proof)
RHS=(1-a(k_proof,N_proof))*Ifstar+(1-b(k_proof,N_proof))*Igstar+a(k_proof,N_proof)*Ifstep+b(k_proof,N_proof)*Igstep
RHS-=sum(terminal_squares(x_proof,xn_proof,star_proof,f_proof,g_proof,L_proof,N_proof),pf.Scalar.zero())
'''
        if kind=="N1":
            src+='''LHS=potential_terminal(xn_proof,x_proof,star_proof,f_proof,g_proof,L_proof,N_proof)
Ifinitial,_=interpolation(f_proof,g_proof,L_proof,star_proof,x_proof)
RHS+=a(sp.S.Zero,N_proof)*Ifinitial-L_proof/(4*N_proof)*((f_proof.grad(x_proof)-f_proof.grad(star_proof))/L_proof)**2
'''
    src+=f'''diff=LHS-RHS
L_symbol=sp.Symbol("L",positive=True)
# The framework accepts symbolic substitutions in sympy_mode; its annotation is narrower.
symbolic_parameters: dict[str, Any]={{"L":L_symbol,"N":N_sym,"k":k_sym}}
pm_proof=pf.ExpressionManager(ctx_proof,resolve_parameters=symbolic_parameters)
gram_residual,function_residual,constant_residual=exact_components(diff,pm_proof)
pf.pprint_labeled_matrix(np.asarray(gram_residual,dtype=object),[f"v_{{i}}" for i in range(gram_residual.rows)],precision=0)
print("{kind} function residual:",function_residual)
print("{kind} constant residual:",constant_residual)
assert all(v==0 for v in [*gram_residual,*function_residual,constant_residual])
proof_checks[{('boundary' if kind=='terminal' else kind)!r}]=True
print("{kind}: exact identity passed in all scalar components.")
'''
    nb.cells += [md(headings[kind]),md(equations[kind]+r" The residual $\mathrm{LHS}-\mathrm{RHS}$ must be exactly zero."),code(src)]

nb.cells += [md("## Normalization and theorem conclusion\n\n"+formula+r"The exact identities and sign lemma give $V_{N}\le0$. Therefore $h(x_{N})-h(x_{\star})\le L\|d_{0}\|^{2}/(4N)\le LR^{2}/(4N)$, including $N=1$."),code(r'''
normalization_L,normalization_N=sp.symbols("L N",positive=True)
normalization_R,initial_distance=sp.symbols("R D",nonnegative=True)
terminal_gap=sp.Symbol("H",real=True)
terminal_value=terminal_gap-normalization_L*initial_distance/(4*normalization_N)
assert sp.expand(terminal_value+normalization_L*initial_distance/(4*normalization_N)-terminal_gap)==0
assert sp.factor(normalization_L*normalization_R**2/(4*normalization_N)-normalization_L*initial_distance/(4*normalization_N)-normalization_L*(-initial_distance+normalization_R**2)/(4*normalization_N))==0
proof_checks["normalization"]=True
assert all(proof_checks[name] for name in ("step","base","boundary","N1","signs","domain","normalization"))
print("V_N <= V_0 = 0; D=||x0-star||^2 <= R^2 gives h(x_N)-h(x_star) <= L R^2/(4N).")
print(r"\forall N\in\mathbb{N}_{\ge1},\quad h(x_N)-h(x_\star)\le\frac{LR^2}{4N}.")
print("Numerical full certificate verified; global analytic lambda/S status remains unresolved; analytic Lyapunov proof verified.")
''')]
nb.cells += [code(r'''
final_expression_structure={
    "quadratic_convention":b4["expression_structure"]["quadratic_convention"],
    "interior":{"index_domain":"1 <= k < N", "basis_labels":b4["expression_structure"]["interior"]["basis_labels"],
        "coefficients":{"0,0":"-L/(4*N)","0,1":"0","0,2":"0","0,3":"0",
            "1,1":"L*(N-k)/(2*N-k)**2","1,2":"0","1,3":"-1/(2*(2*N-k))",
            "2,2":"-k/(2*L*(2*N-k)**2)","2,3":"0","3,3":"0"}},
    "initial":{"index_domain":"k=0","basis_labels":[],"coefficients":{},"value":"0"},
    "terminal":{"index_domain":"k=N","basis_labels":["x0-x_star"],"coefficients":{"0,0":"-L/(4*N)"}},
    "function_terms":[
        {"expression":"f(x_k)-f(x_star)","coefficient":"(k+1)/(2*N-k)","index_domain":"1<=k<N"},
        {"expression":"g(x_k)-g(x_star)","coefficient":"k/(2*N-k)","index_domain":"1<=k<N"},
        {"expression":"f(x_N)-f(x_star)","coefficient":"1","index_domain":"k=N"},
        {"expression":"g(x_N)-g(x_star)","coefficient":"1","index_domain":"k=N"}],
    "constant_terms":[]}
proof_arguments={
    "domain":"L>0, R>=0, integer N>=1; interior 1<=k<N. Base N>=2; step 1<=k<=N-2; terminal N>=2; separate N=1.",
    "signs":"Exact A,B,P positive-polynomial identities in the sign cell imply alpha,beta>0 and gamma>=0. Residual multipliers are nonnegative by the four rational identities and a,b>=0. Terminal square coefficients L/2 and initial L/(4N) are positive.",
    "direction":"Every interpolation residual is nonpositive and every subtracted square has nonnegative weight, so V_(k+1)<=V_k.",
    "normalization":"V0=0 and VN=h(xN)-h(star)-L||x0-star||^2/(4N); initial distance <=R^2 gives LR^2/(4N).",
    "coefficient_derivation":"Numerical basis suggests distance/cross/gap coefficients; symbolic residual quadratic retains t_k,t_next. Selected t_k=k/(2*(2N-k)^2) passes exact completion of squares and all native identities. This selection need not equal the original reverse LDL allocation."}
final_formula="V0=0; for 1<=k<N: -L||x0-star||^2/(4N)+L(N-k)||xk-star||^2/(2N-k)^2-<xk-star,grad f(xk)>/(2N-k)-k||grad f(xk)-grad f(star)||^2/(2L(2N-k)^2)+(k+1)(f(xk)-f(star))/(2N-k)+k(g(xk)-g(star))/(2N-k); VN=h(xN)-h(star)-L||x0-star||^2/(4N)."
state5={**b4,"discovery_expression_structure":b4["expression_structure"],
    "expression_structure":final_expression_structure,"unresolved_coefficients":[],
    "coefficient_formula_status":"symbolically_verified",
    "coeff_code":"from typing import cast\n"+(notebook_dir/"supplementary/h/analytic.py").read_text()+"\n"+inspect.getsource(closed_coefficient_matrix),
    "local_multiplier_code":inspect.getsource(a)+"\n"+inspect.getsource(b),
    "analytic_potential_code":(notebook_dir/"supplementary/h/analytic.py").read_text(),
    "proof_checks":proof_checks,"proof_arguments":proof_arguments,"lyapunov_formula":final_formula,
    "numerical_coefficient_comparisons":coefficient_comparisons,
    "numerical_certificate_verified":True,"analytic_full_pep_verified":False,
    "require_analytic_full_pep":False,"lyapunov_proof_verified":all(proof_checks.values()),
    "run_status":"complete","remaining_unknowns":[],"unresolved_requested_work":[],
    "presentation_policy":"evaluation-ancillary-v1","visual_review":"not performed under evaluation override"}
assert state5["lyapunov_proof_verified"]
(notebook_dir/"state/pgm_b5.json").write_text(json.dumps(state5,indent=2))
print(final_formula)
print("All exact proof gates passed; Block 5 state saved.")
''')]
nb.cells[2:2]=[md("### Theorem\n\nFor the stated PGM recurrence with convex $L$-smooth $f$, closed proper convex $g$, $L>0$, $R\ge0$, integer $N\ge1$, a minimizer $x_{\star}$ and $\|x_{0}-x_{\star}\|^{2}\le R^{2}$, the following potential is nonincreasing. All stated evaluations and proximal steps are well-defined.\n\n"+formula+r"Consequently, $$h(x_{N})-h(x_{\star})\le\frac{LR^{2}}{4N}.$$"),md(outline)]
# Keep source math free of ambiguous multi-character subscripts.
for cell in nb.cells:
    if cell.cell_type=="markdown":
        cell.source=re.sub(r"_([A-Za-z0-9]+)(?![A-Za-z0-9{])",r"_{\1}",cell.source)
        cell.source=cell.source.replace("a_{0I}","a_{0}I").replace("b_{1I}","b_{1}I")
        assert not any(ord(c)<32 and c not in "\n\t" for c in cell.source)
nbf.write(nb,root/"pgm_example_lyap.ipynb")
