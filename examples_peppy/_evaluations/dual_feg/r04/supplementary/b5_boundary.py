boundary_ctx = pf.PEPContext('dual_feg_exact_boundary').set_as_current()
A_boundary = pf.LipschitzMonotoneOperator(is_basis=True, tags=['A_{boundary}'], L=Lp)
x0_boundary = pf.Vector(is_basis=True, tags=['x_{0}'])
xN_boundary = pf.Vector(is_basis=True, tags=['x_{N}'])
xs_boundary = A_boundary.set_zero_point('x_{star}')
g_boundary = A_boundary(xN_boundary)
VN_boundary = terminal_exact(g_boundary, x0_boundary, xN_boundary, Lp, Np)
I_mon_boundary = -(g_boundary * (xN_boundary - xs_boundary))
I_initial = (x0_boundary - xs_boundary)**2 - Rp**2
S_boundary = (g_boundary - 2 * Lp / Np * (x0_boundary - xs_boundary))**2
boundary_LHS = g_boundary**2 - 4 * Lp**2 / Np**2 * Rp**2
boundary_RHS = VN_boundary + 4 * Lp / Np * I_mon_boundary - S_boundary + 4 * Lp**2 / Np**2 * I_initial
boundary_diff = boundary_LHS - boundary_RHS
boundary_manager = pf.ExpressionManager(boundary_ctx, resolve_parameters=symbolic_values)
proof_checks['boundary'] = verify_exact('Terminal metric and normalization', boundary_diff, boundary_manager, boundary_ctx)
proof_checks['normalization'] = proof_checks['boundary']
