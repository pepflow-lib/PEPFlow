def analytic_coefficients(k, horizon, lipschitz):
    if k == 0:
        return sp.zeros(0, 0)
    if k == horizon:
        return sp.Matrix([[2, -2*lipschitz/horizon], [-2*lipschitz/horizon, 0]])
    t = horizon - k
    return sp.Matrix([[0, -2*lipschitz/horizon, 2*lipschitz/t, -2],
                      [-2*lipschitz/horizon, 0, 0, 0],
                      [2*lipschitz/t, 0, 0, 2*lipschitz/t],
                      [-2, 0, 2*lipschitz/t, -2]])


def local_multipliers(k, horizon, lipschitz):
    if k == horizon - 1:
        return {'lipschitz': sp.Integer(2), 'monotonicity': sp.Integer(0)}
    t = horizon - k
    return {'lipschitz': sp.Integer(2)/t**2, 'monotonicity': 4*lipschitz/(t*(t-1))}
