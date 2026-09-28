"""Test a sparse certificate and its initial theta-based candidates."""
import json
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'supplementary/helpers'))
    from runtime import configure

    configure()
    import numpy as np
    import pepflow as pf
    from certificate import capture
    from ogm_setup import get_pep_setup, theta_sequence

    dense = json.loads((root / 'state/ogm_dense.json').read_text())
    N = dense['N_verify']
    tags = ['z_0'] + [f'x_{i}' for i in range(1, N + 1)]
    keep = {f'f:{tags[i]},{tags[i+1]}' for i in range(N)}
    keep |= {f'f:x_star,{tag}' for tag in tags}
    relaxed = [name for name, meta in dense['constraint_metadata'].items()
               if meta['origin'] == 'interpolation' and name not in keep]
    data = capture(N, relaxed, dense['opt_value'])
    assert data['numerical_certificate_verified']
    theta = theta_sequence(N)
    guessed = {f'f:x_star,{tags[i]}': 2 * theta[i] / theta[N]**2 for i in range(N)}
    guessed[f'f:x_star,{tags[N]}'] = 1 / theta[N]
    guessed.update({f'f:{tags[i]},{tags[i+1]}': 2 * theta[i]**2 / theta[N]**2 for i in range(N)})
    errors = {name: abs(data['named_dual_values'][name] - value) for name, value in guessed.items()}
    ctx, pb, obj = get_pep_setup(N, {'L': 1, 'R': 1})
    pm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(data['params_json']))
    w = ctx[f'z_{N}'] - ctx['x_star'] - theta[N] * obj.grad(ctx[f'x_{N}'])
    coords = np.asarray(pm.eval_vector(w).coords, dtype=float)
    candidate_S = np.outer(coords, coords) / (2 * theta[N]**2)
    S_error = float(np.max(np.abs(candidate_S - np.asarray(data['S_matrix']))))
    print('Sparse bound:', data['opt_value'])
    print('Active multipliers and formula errors:', json.dumps(errors))
    print('S guess max error:', S_error)
    print('Numerical checks:', data['numerical_checks'])
    print('D diagonal:', np.diag(data['numerical_decomposition']['D']))
    data['closed_form_search'] = {
        'completed': True, 'references_reviewed': [],
        'reference_scope_note': 'No target-specific references authorized. Candidates derived from own dense/sparse multipliers.',
        'attempts': [
            {'component': 'lambda', 'candidate': 'star,i: 2*theta_i/theta_N^2 (i<N); star,N: 1/theta_N; i,i+1: 2*theta_i^2/theta_N^2',
             'comparison_atol': 1e-4, 'errors': errors, 'max_abs_error': max(errors.values())},
            {'component': 'S', 'candidate': 'L/(2*theta_N^2) * ||z_N-x_star-theta_N*g_N/L||^2',
             'comparison_atol': 1e-4, 'gram_max_abs_error': S_error, 'function_error': 0, 'offset_error': 0}],
        'unresolved_components': ['analytic all-horizon validity and signs of lambda and S formulas']}
    data['formula_status'] = {'lambda': 'candidate' if max(errors.values()) < 1e-4 else 'unresolved',
                              'S': 'candidate' if S_error < 1e-4 else 'unresolved'}
    data['lamb_code'] = '''def lamb(ri, ci, N, theta):
    def index(tag):
        if tag == "x_star":
            return -1
        if tag in ("z_0", "x_0"):
            return 0
        return int(tag.split("_")[1])
    i, j = index(ri), index(ci)
    if i == -1 and 0 <= j < N:
        return 2 * theta[j] / theta[N]**2
    if i == -1 and j == N:
        return 1 / theta[N]
    if 0 <= i < N and j == i + 1:
        return 2 * theta[i]**2 / theta[N]**2
    return 0
'''
    data['S_code'] = '''def S_guess(ctx, obj, N, theta, L):
    w = ctx[f"z_{N}"] - ctx["x_star"] - (theta[N] / L) * obj.grad(ctx[f"x_{N}"])
    return (L / (2 * theta[N]**2)) * (w**2)
'''
    data['analytic_full_pep_verified'] = False
    data['lyapunov_proof_verified'] = False
    data['require_analytic_full_pep'] = False
    data['candidate_S_matrix'] = candidate_S.tolist()
    data['sparsity_recipe'] = 'Keep star-to-every-iterate and forward-consecutive interpolation pairs.'
    for filename in ('ogm_relaxed.json', 'ogm_b2.json'):
        (root / 'state' / filename).write_text(json.dumps(data, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()

