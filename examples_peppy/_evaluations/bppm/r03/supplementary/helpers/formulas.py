"""Fresh candidate formulas inferred from this attempt's certificate."""

def candidate_duals(N, alpha):
    values = {'initial_condition': 1 / (alpha * N), f'h:x_star,x_{N}': 1 / (alpha * N)}
    for i in range(1, N + 1):
        values[f'f:x_star,x_{i}'] = 1 / N
        values[f'h:x_{i},x_{i-1}'] = i / (alpha * N)
        if i > 1:
            values[f'f:x_{i-1},x_{i}'] = (i - 1) / N
            values[f'h:x_{i-1},x_{i}'] = (i - 1) / (alpha * N)
    return values
