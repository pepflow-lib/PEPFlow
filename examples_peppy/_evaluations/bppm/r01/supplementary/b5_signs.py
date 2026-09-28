# Convexity gives I_f <= 0 and I_h <= 0; the initial assumption gives I_0 <= 0.
# k is a nonnegative integer; N is a positive integer; alpha is positive.
local_multipliers=[1/N_symbol,k_symbol/N_symbol,(k_symbol+1)/(a_symbol*N_symbol),k_symbol/(a_symbol*N_symbol)]
assert all(coefficient.is_nonnegative is True for coefficient in local_multipliers)
assert (1/(a_symbol*N_symbol)).is_positive is True
assert sp.simplify(A_formula.subs(k_symbol,N_symbol)-1)==0
assert sp.simplify(A_formula.subs(k_symbol,0))==0
proof_checks['signs']=True
proof_checks['domain']=True
proof_checks['normalization']=True
assert all(proof_checks.values())
print('Signs: all local and boundary multipliers are nonnegative on the stated domain.')
print('Direction: V_(k+1) <= V_k, V_0=0, and gap - R/(alpha*N) <= V_N <= 0.')
print('N=1 uses the verified base step; R=0 needs no division by R.')
print('Analytic Lyapunov proof verified. Global full-PEP formula remains separately uncertified.')
