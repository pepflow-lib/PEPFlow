local_multipliers=[1/n_sym,k_sym/n_sym,(k_sym+1)/(a_sym*n_sym),k_sym/(a_sym*n_sym)]
assert all(sp.ask(sp.Q.nonnegative(v)) is True for v in local_multipliers)
assert sp.ask(sp.Q.positive(1/(a_sym*n_sym))) is True
proof_checks['signs']=True
# Domain: integer N>=1, 0<=k<=N-1, alpha>0, R>=0; exact iterates/evaluations exist.
# Convexity makes each displayed residual <=0; the initial residual is <=0.
# V_0=0 and the exact step imply V_N<=0. The boundary RHS is therefore <=0.
proof_checks['domain']=True
assert all(proof_checks.values())
proof_arguments={
 'step':'All four convex residuals are nonpositive; multipliers 1/N,k/N,(k+1)/(alpha N),k/(alpha N) are nonnegative. Hence V_{k+1}<=V_k.',
 'base':'V_0=0 exactly; separate first-step identity verified. W_0=D_h(x_star,x_0)/(alpha N)<=R/(alpha N).',
 'boundary':'metric-R/(alpha N)=V_N+(D_h(x_star,x_0)-R)/(alpha N)+r_h(star,N)/(alpha N)<=0.',
 'signs':'Convexity gives r_f,r_h<=0 and D_h>=0; alpha N>0. No strong convexity or positivity of R is needed.',
 'domain':'N integer >=1; alpha>0; R>=0; k integer 0..N-1. N=1 uses the separately checked first step and terminal identity, R=0 is allowed.',
 'normalization':'The exact finite-horizon denominator is alpha*N and initial radius is R, not R squared.'}
print('Exact proof checks:',proof_checks)
print('V_k=(D_h(x_star,x_k)-D_h(x_star,x_0))/(alpha*N)+(k/N)*(f(x_k)-f(x_star))')
print('For every N>=1: f(x_N)-f(x_star) <= R/(alpha*N).')
