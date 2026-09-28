# Interior: t=N-k>=2. Write t=u+1 with u>=1, so all denominators are nonzero.
u_positive = sp.Symbol('u', integer=True, positive=True)
sign_expressions = {'interior_lipschitz': 2 / (u_positive + 1)**2,
                    'interior_monotonicity': 4 * L_symbol / ((u_positive + 1) * u_positive),
                    'last_lipschitz': sp.Integer(2), 'boundary_monotonicity': 4 * L_symbol / N_symbol,
                    'initial_constraint': 4 * L_symbol**2 / N_symbol**2}
assert all(sp.ask(sp.Q.positive(value)) is True for value in sign_expressions.values())
proof_checks['signs'] = True
proof_checks['domain'] = True
assert all(proof_checks.values())
print('All required multipliers are positive on their stated domains; no vanishing denominators remain.')
print('Monotonicity and Lipschitz residuals are nonpositive; squared remainder is nonnegative.')
print('Therefore V_N <= V_0 = 0 and ||A(x_N)||^2 <= 4 L^2 R^2 / N^2 for every integer N>=1.')
