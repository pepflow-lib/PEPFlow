# Choose the nonzero scale nu_k=2(k+1)^2/N^2 to target the desired bound.
nu_choice=2*(k_symbol+1)**2/N_symbol**2
resolved={name:sp.simplify(solution[0].get(symbol, symbol).subs(unknown_symbols['nu'],nu_choice)) for name,symbol in unknown_symbols.items()}
print('Resolved coefficients and local multipliers:',resolved)
expected={'a_k':2*k_symbol**2/N_symbol**2,'b_k':2*k_symbol*L_symbol/N_symbol**2,'c_k':sp.Integer(0),'a_next':2*(k_symbol+1)**2/N_symbol**2,'b_next':2*(k_symbol+1)*L_symbol/N_symbol**2,'c_next':sp.Integer(0),'mu':4*k_symbol*(k_symbol+1)*L_symbol/N_symbol**2,'nu':nu_choice}
assert all(sp.simplify(resolved[name]-formula)==0 for name,formula in expected.items())
assert sp.simplify(resolved['a_next']-resolved['a_k'].subs(k_symbol,k_symbol+1))==0
assert sp.simplify(resolved['b_next']-resolved['b_k'].subs(k_symbol,k_symbol+1))==0
# Original unknown Scalar identity is re-evaluated after the derived substitution.
pm_step=pf.ExpressionManager(ctx_step,resolve_parameters={'k_symbolic':k_symbol,'N_symbolic':N_symbol,'L_symbolic':L_symbol,**resolved})
step_LHS=V_next_unknown-V_unknown
step_RHS=unknown_parameters['mu']*mon_step+unknown_parameters['nu']*lip_step
step_diff=step_LHS-step_RHS
step_verified=verify_exact('Symbolic step',step_diff,pm_step,ctx_step)
