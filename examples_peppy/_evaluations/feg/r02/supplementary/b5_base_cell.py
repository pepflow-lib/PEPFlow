ctx_base=pf.PEPContext('feg_symbolic_base').set_as_current()
A_base=pf.LipschitzMonotoneOperator(is_basis=True,tags=['A_{base}'],L=Lp)
x0_base=pf.Vector(is_basis=True,tags=['x_{0}'])
xhalf_base=x0_base
xhalf_base.add_tag('x_{1/2}')
g0_base=A_base(x0_base)
x1_base=x0_base-g0_base/Lp
x1_base.add_tag('x_{1}')
g1_base=A_base(x1_base)
base_LHS=2/Np**2*g1_base**2+4*Lp/Np**2*g1_base*(x1_base-x0_base)
base_RHS=2/Np**2*((g1_base-g0_base)**2-Lp**2*(x1_base-x0_base)**2)
base_diff=base_LHS-base_RHS
pm_base=pf.ExpressionManager(ctx_base,resolve_parameters={'N_symbolic':N_symbol,'L_symbolic':L_symbol})
assert xhalf_base is x0_base
base_verified=verify_exact('Symbolic base',base_diff,pm_base,ctx_base)
