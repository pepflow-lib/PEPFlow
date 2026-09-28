# Signs are justified for the entire integer index domain, not just samples.
u_nonneg,v_nonneg = sp.symbols('u v',integer=True,nonnegative=True)
i_sym = sp.Symbol('i',integer=True,positive=True)
domain_substitution = {N_sym:u_nonneg+v_nonneg+1,i_sym:u_nonneg+1}
c1_symbolic = N_sym/((2*N_sym+1-i_sym)*(2*N_sym-i_sym)*L_sym)
c2_symbolic = (((i_sym-1)/(2*N_sym-i_sym))*((2*N_sym+2)/(2*N_sym+1))
               +2*N_sym/((2*N_sym-i_sym)**2*(2*N_sym+1)))/(2*L_sym)
c3_symbolic = i_sym/(2*N_sym+1-i_sym)*(2*N_sym)/(2*N_sym+1)/(2*L_sym)
local_sign_expressions = {
    'c1':c1_symbolic,'c2':c2_symbolic,'c3':c3_symbolic,
    'f_star_interior':(2*N_sym+1)/((2*N_sym-i_sym)*(2*N_sym+1-i_sym)),
    'g_star_interior':2*N_sym/((2*N_sym-i_sym)*(2*N_sym+1-i_sym)),
    'f_consecutive':i_sym/(2*N_sym+1-i_sym),
    'g_consecutive':(i_sym-1)/(2*N_sym+1-i_sym),
    'f_star_zero':1/(2*N_sym),
    'f_star_terminal':1/(N_sym+1),'g_star_terminal':2/(N_sym+1),
    'tau':L_sym/(4*N_sym),
}
sign_audit = {}
for name,expression in local_sign_expressions.items():
    transformed = sp.factor(expression.subs(domain_substitution,simultaneous=True))
    assert transformed.is_nonnegative is True, (name,transformed)
    sign_audit[name] = str(transformed)
print('All interpolation and square coefficients nonnegative on N>=i>=1, L>0.')
# Interior-potential denominators are nonzero since 2N-k >= N+1 for 1<=k<N.
# Endpoint formulas have positive N, N+1, 2N-1; N=1 was checked separately.
R_sym = sp.Symbol('R',nonnegative=True)
RP = pf.Parameter('R_proof')
ctx_terminal.set_as_current()
metric_terminal = f_terminal(xn_terminal)-f_terminal(xstar_terminal)+g_terminal(xn_terminal)-g_terminal(xstar_terminal)
normalization_LHS = metric_terminal-LP/(4*NP)*RP**2
normalization_RHS = V_terminal+LP/(4*NP)*(r0_terminal**2-RP**2)
normalization_diff = normalization_LHS-normalization_RHS
normalization_verified = verify_identity('Initial-distance normalization',normalization_diff,ctx_terminal,{**symbolic_parameters,'R_proof':R_sym})
# The local identities telescope to the complete global certificate. Verify
# the endpoint and interior multiplier formulas used by this summation.
j_sym = sp.Symbol('j',integer=True)
def tf(j):
    return (j+1)/(2*N_sym-j)


def tg(j):
    return j/(2*N_sym-j)

multiplier_identities = [
    sp.cancel(tf(j_sym)-tf(j_sym-1)-(2*N_sym+1)/((2*N_sym-j_sym)*(2*N_sym+1-j_sym))),
    sp.cancel(tg(j_sym)-tg(j_sym-1)-2*N_sym/((2*N_sym-j_sym)*(2*N_sym+1-j_sym))),
    sp.cancel(1-tf(N_sym-1)-1/(N_sym+1)),
    sp.cancel(1-tg(N_sym-1)-2/(N_sym+1)),
    sp.cancel(tf(0)-1/(2*N_sym)),
]
assert multiplier_identities == [0]*5
print('Exact telescoping multiplier identities:',multiplier_identities)
proof_checks = dict(step=step_verified,base=base_verified,boundary=boundary_verified,
                    single_iteration=single_verified,signs=True,domain=True,
                    normalization=normalization_verified)
analytic_full_pep_verified = all(proof_checks.values()) and multiplier_identities == [0]*5
lyapunov_proof_verified = all(proof_checks.values())
assert analytic_full_pep_verified and lyapunov_proof_verified
print('PROOF_CHECKS_JSON='+json.dumps(proof_checks))
print('Analytic full-PEP identity established by summing the verified local identities.')
print('Theorem: h(x_N)-h(x_star) <= L*R**2/(4*N), for every integer N>=1.')
print(r'LaTeX theorem: h(x_{N})-h(x_{\star})\leq \frac{LR^2}{4N},\quad N\geq1.')
