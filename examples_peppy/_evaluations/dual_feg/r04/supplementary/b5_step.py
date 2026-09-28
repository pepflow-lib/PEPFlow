step_ctx = pf.PEPContext('dual_feg_exact_step').set_as_current()
A_step = pf.LipschitzMonotoneOperator(is_basis=True, tags=['A_{step}'], L=Lp)
x_step = pf.Vector(is_basis=True, tags=['x_{k}'])
z_step = pf.Vector(is_basis=True, tags=['z_{k}'])
x0_step = pf.Vector(is_basis=True, tags=['x_{0}'])
xN_step = pf.Vector(is_basis=True, tags=['x_{N}'])
g_step = A_step(xN_step)
a_step = A_step(x_step)
y_step = (x_step - z_step / Lp - a_step / Lp).add_tag('x_{k+1/2}')
b_step = A_step(y_step)
xp_step = (y_step - (tp - 1) / tp / Lp * (b_step - a_step)).add_tag('x_{k+1}')
zp_step = ((tp - 1) / tp * z_step - b_step / tp).add_tag('z_{k+1}')
V_before = potential_exact(tp, x_step, z_step, g_step, x0_step, xN_step, Lp, Np)
V_after = potential_exact(tp - 1, xp_step, zp_step, g_step, x0_step, xN_step, Lp, Np)
I_lip_step = (b_step - a_step)**2 - Lp**2 * ((y_step - x_step)**2)
I_mon_step = -((b_step - g_step) * (y_step - xN_step))
step_LHS = V_after - V_before
# Derive the two local multipliers by matching every symbolic component.
mu_lip_p, mu_mon_p = pf.Parameter('mu_lip'), pf.Parameter('mu_mon')
mu_lip_s, mu_mon_s = sp.symbols('mu_lip mu_mon', real=True)
equation_values: dict[str, Any] = {**symbolic_values, 'mu_lip': mu_lip_s, 'mu_mon': mu_mon_s}
equation_manager = pf.ExpressionManager(step_ctx, resolve_parameters=equation_values)
coefficient_gram, coefficient_func, coefficient_offset = exact_components(
    step_LHS - mu_lip_p * I_lip_step - mu_mon_p * I_mon_step, equation_manager)
equations = [value for value in [*coefficient_gram, *coefficient_func, coefficient_offset] if value != 0]
multiplier_solutions = sp.solve(equations, [mu_lip_s, mu_mon_s], dict=True)
assert len(multiplier_solutions) == 1
assert sp.simplify(multiplier_solutions[0][mu_lip_s] - 2 / t_symbol**2) == 0
assert sp.simplify(multiplier_solutions[0][mu_mon_s] - 4 * L_symbol / (t_symbol * (t_symbol - 1))) == 0
print('Derived local multiplier solution:', multiplier_solutions[0])
step_RHS = 2 / tp**2 * I_lip_step + 4 * Lp / (tp * (tp - 1)) * I_mon_step
step_diff = step_LHS - step_RHS
step_manager = pf.ExpressionManager(step_ctx, resolve_parameters=symbolic_values)
proof_checks['step'] = verify_exact('Interior step (t=N-k>=2)', step_diff, step_manager, step_ctx)
