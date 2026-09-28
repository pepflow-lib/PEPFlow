ctx_base=pf.PEPContext('bppm_symbolic_base').set_as_current()
f_base=pf.ConvexFunction(is_basis=True,tags=['f_{base}'])
h_base=pf.ConvexFunction(is_basis=True,tags=['h_{base}'])
f_base.set_stationary_point('x_{star,base}')
xs_base=ctx_base['x_{star,base}']
x0_base=pf.Vector(is_basis=True,tags=['x_{0,base}'])
a_base: Any=pf.Parameter('a_{base}')
n_base=pf.Parameter('n_{base}')
x1_base=f_base.bregman_prox(x0_base,a_base,h_base,tag='x_{1,base}')
base_distance=D_h(h_base,xs_base,x0_base)
base_V0=(base_distance-base_distance)/(a_base*n_base)
base_V1=(a_base*(f_base(x1_base)-f_base(xs_base))+D_h(h_base,xs_base,x1_base)-base_distance)/(a_base*n_base)
base_LHS=base_V1-base_V0
base_RHS=interpolation(f_base,xs_base,x1_base)/n_base + interpolation(h_base,x1_base,x0_base)/(a_base*n_base)
base_diff=base_LHS-base_RHS
base_parameters: dict[str,Any]={'a_{base}':a_symbol,'n_{base}':N_symbol}
pm_base=pf.ExpressionManager(ctx_base,resolve_parameters=base_parameters)
base_zero=verify_exact('Base V0',base_V0,pm_base)
base_step=verify_exact('Base first step',base_diff,pm_base)
proof_checks['base']=base_zero and base_step
# The same base step supplies the whole step argument when N=1.
base_one_parameters: dict[str,Any]={'a_{base}':a_symbol,'n_{base}':sp.S(1)}
pm_base_one=pf.ExpressionManager(ctx_base,resolve_parameters=base_one_parameters)
assert verify_exact('N=1 base',base_diff,pm_base_one)
