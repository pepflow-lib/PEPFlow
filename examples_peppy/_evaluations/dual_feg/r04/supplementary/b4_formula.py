def coeff_pattern(k, n):
    if k == 0:
        return np.zeros((0, 0))
    if k == n:
        return np.array([[2.0, -2.0/n], [-2.0/n, 0.0]])
    t = n - k
    return np.array([[0.0, -2.0/n, 2.0/t, -2.0],
                     [-2.0/n, 0.0, 0.0, 0.0],
                     [2.0/t, 0.0, 0.0, 2.0/t],
                     [-2.0, 0.0, 2.0/t, -2.0]])
