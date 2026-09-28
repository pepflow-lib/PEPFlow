"""Visible B4 search and reconstruction calculations (no solves)."""
# CELL: replay
import inspect
import itertools
import json

import numpy as np
import pepflow as pf
from pepflow.lyapunov_utils import (
    find_basis_with_sparsest_coefficients,
    find_symmetric_coefficient_matrix,
    vectors_in_column_space,
)

from certificate import scalar_coordinates
from ogm_setup import theta_sequence
from partial_sums import construct, rebuild
from runtime import NOTEBOOK_DIR

b3 = json.loads((NOTEBOOK_DIR / 'state/ogm_b3.json').read_text())
observation = construct(b3, verbose=False)
assert observation['rank_profile'] == b3['rank_profile']
rank_evidence = json.loads((NOTEBOOK_DIR / b3['rank_search']['evidence_path']).read_text())
assert rank_evidence['summary'] == b3['rank_search']
ctx4, pb4, obj4, pm4 = rebuild(b3)
N4 = b3['N_verify']
params4 = json.loads(b3['params_json'])
basis4 = ctx4.basis_vectors()
scalars4 = ctx4.basis_scalars()


def coordinate_expression(c):
    expression = pf.Scalar.zero() + c['offset']
    expression += sum((float(value) * scalar for value, scalar in zip(c['func'], scalars4)), pf.Scalar.zero())
    expression += sum((float(c['gram'][i][j]) * basis4[i] * basis4[j]
                       for i, j in np.ndindex((len(basis4), len(basis4)))), pf.Scalar.zero())
    return expression


lyap4 = [coordinate_expression(c) for c in observation['lyap_coordinates']]
for k, expression in enumerate(lyap4):
    actual = scalar_coordinates(pm4, expression)
    assert np.allclose(actual['gram'], b3['lyap_inner_prod_coords'][k], atol=1e-4, rtol=1e-5)
    assert np.allclose(actual['func'], b3['lyap_func_coords'][k], atol=1e-4, rtol=1e-5)
    assert abs(actual['offset'] - b3['lyap_offsets'][k]) <= 1e-4
print('Replayed ranks:', observation['rank_profile'], '; interior 1..N-1; endpoints 0,N.')

# CELL: candidates
candidate_pairs = [('anchor', ctx4['x_0'] - ctx4['x_star'])]
for k in range(N4):
    candidate_pairs.append((f'q_{k}', ctx4[f'z_{k+1}'] - ctx4['x_star']))
for k in range(N4 + 1):
    candidate_pairs.append((f'g_{k}', obj4.grad(ctx4[f'x_{k}'])))
points = [('x_star', ctx4['x_star'])]
points += [(f'x_{k}', ctx4[f'x_{k}']) for k in range(N4 + 1)]
points += [(f'z_{k}', ctx4[f'z_{k}']) for k in range(N4 + 1)]
points += [(f'y_{k}', ctx4[f'y_{k}']) for k in range(1, N4 + 1)]
candidate_pairs += points
candidate_pairs += [(f'{a}-{b}', u-v) for (a, u), (b, v) in itertools.combinations(points, 2)]
unique_pairs, candidate_coords = [], []
for label, vector in candidate_pairs:
    coordinates = np.asarray(pm4.eval_vector(vector).coords, dtype=float)
    if np.linalg.norm(coordinates) <= 1e-6:
        continue
    if any(np.allclose(coordinates, old, atol=1e-6, rtol=0) for old in candidate_coords):
        continue
    unique_pairs.append((label, vector))
    candidate_coords.append(coordinates)
labels_by_id = {id(v): label for label, v in unique_pairs}
in_column = {}
for k in range(1, N4 + 1):
    found = vectors_in_column_space(lyap4[k], [v for _, v in unique_pairs],
                                    pep_context=ctx4, resolve_parameters=params4, atol=1e-4, rtol=1e-4)
    in_column[k] = found
    print(f'V_{k} column-space candidates:')
    for v in found:
        print('  ', labels_by_id[id(v)])

# CELL: search
search_results = {}
for k, candidates in in_column.items():
    sparse_basis, sparse_C = find_basis_with_sparsest_coefficients(
        lyap4[k], candidates, pep_context=ctx4, resolve_parameters=params4,
        zero_tol=1e-6, indep_tol=1e-7, span_tol=1e-5)
    assert len(sparse_basis) == observation['rank_profile'][k]
    labels = [labels_by_id[id(v)] for v in sparse_basis]
    zero_count = int(np.sum(np.abs(sparse_C) < 1e-6))
    print(f'k={k}, rank={observation["rank_profile"][k]}')
    print('  sparse basis:', labels)
    print(f'  zero coefficients: {zero_count}/{sparse_C.size}')
    search_results[str(k)] = {'basis_labels': labels, 'C': sparse_C.tolist(), 'zero_count': zero_count}

# CELL: basis
def V_k_basis(k, ctx=ctx4, obj=obj4, N=N4):
    if k == 0:
        return []
    anchor = ctx['x_0'] - ctx['x_star']
    if k == N:
        return [anchor]
    return [anchor, ctx[f'z_{k+1}'] - ctx['x_star'], obj.grad(ctx[f'x_{k}'])]


def V_k_basis_labels(k, N=N4):
    if k == 0:
        return []
    if k == N:
        return ['x_0-x_star']
    return ['x_0-x_star', f'z_{k+1}-x_star', f'g_{k}']


coeff4, quadratic_residuals = {}, {}
for k in range(N4 + 1):
    vectors = V_k_basis(k)
    matrix = np.column_stack([pm4.eval_vector(v).coords for v in vectors]).astype(float) if vectors else np.zeros((len(basis4), 0))
    rank = int(np.linalg.matrix_rank(matrix, tol=1e-7)) if vectors else 0
    assert rank == len(vectors) == observation['rank_profile'][k]
    C = find_symmetric_coefficient_matrix(lyap4[k], vectors, pep_context=ctx4,
                                         resolve_parameters=params4, indep_tol=1e-7, span_tol=1e-5)
    target = np.asarray(observation['lyap_coordinates'][k]['gram'])
    error = float(np.linalg.norm(matrix @ C @ matrix.T - target, ord='fro'))
    assert error <= 1e-5 * max(1.0, np.linalg.norm(target, ord='fro'))
    coeff4[k] = C
    quadratic_residuals[str(k)] = error
    print(f'k={k}: rank {rank} basis {V_k_basis_labels(k)}; reconstruction {error:.3g}')

# CELL: coefficients
function_coefficients = {}
component_residuals = {}
for k in range(N4 + 1):
    target_func = np.asarray(observation['lyap_coordinates'][k]['func'])
    f_gap = scalar_coordinates(pm4, obj4(ctx4[f'x_{k}']) - obj4(ctx4['x_star']))
    gap_coords = np.asarray(f_gap['func'])
    a = float(target_func @ gap_coords / (gap_coords @ gap_coords)) if k else 0.0
    function_coefficients[k] = a
    assert np.allclose(a * gap_coords, target_func, atol=1e-4, rtol=1e-5)
    assert abs(observation['lyap_coordinates'][k]['offset']) <= 1e-5
    print(f'k={k}: coefficient of f(x_{k})-f_star: {a:.12g}; offset 0')
    pf.pprint_labeled_matrix(coeff4[k], V_k_basis_labels(k), precision=7)


def V_k_structure(k):
    vectors = V_k_basis(k)
    C = coeff4[k]
    quadratic = sum((float(C[i, j]) * vectors[i] * vectors[j]
                     for i, j in np.ndindex(C.shape)), pf.Scalar.zero())
    return quadratic + function_coefficients[k] * (obj4(ctx4[f'x_{k}']) - obj4(ctx4['x_star']))


for k in range(N4 + 1):
    residual = scalar_coordinates(pm4, V_k_structure(k) - lyap4[k])
    errors = {name: float(np.max(np.abs(residual[name]), initial=0)) for name in ('gram', 'func', 'offset')}
    assert max(errors.values()) <= 1e-4
    component_residuals[str(k)] = errors
print('Full-expression reconstruction:', component_residuals)

# CELL: fit
def coeff_pattern(k, N, theta, L):
    if k == 0:
        return np.zeros((0, 0)), 0.0
    if k == N:
        return np.array([[-L / (2 * theta[N]**2)]]), 1.0
    return np.diag([-L / (2 * theta[N]**2), L / (2 * theta[N]**2),
                    -theta[k]**2 / (L * theta[N]**2)]), 2 * theta[k]**2 / theta[N]**2


formula_errors = {}
for k in range(N4 + 1):
    C_candidate, a_candidate = coeff_pattern(k, N4, theta_sequence(N4), params4['L'])
    C_error = float(np.max(np.abs(C_candidate - coeff4[k]), initial=0))
    a_error = abs(a_candidate - function_coefficients[k])
    assert max(C_error, a_error) < 1e-4
    formula_errors[str(k)] = {'quadratic': C_error, 'function': a_error}
    print(f'Candidate formula k={k}: quadratic error={C_error:.3g}; function error={a_error:.3g}')

# CELL: state
expression_structure = {
    'quadratic_convention': 'sum_ij C_ij <v_i,v_j>, C symmetric, off-diagonals counted twice',
    'interior': {'index_domain': '1 <= k <= N-1', 'basis_labels': ['x_0-x_star', 'z_(k+1)-x_star', 'g_k'],
                 'candidate_C': 'diag(-L/(2 theta_N^2), L/(2 theta_N^2), -theta_k^2/(L theta_N^2))'},
    'initial': {'index_domain': 'k=0', 'basis_labels': [], 'C': []},
    'terminal': {'index_domain': 'k=N', 'basis_labels': ['x_0-x_star'], 'candidate_C': '-L/(2 theta_N^2)'},
    'function_terms': [{'index_domain': '1 <= k < N', 'expression': 'f(x_k)-f_star', 'candidate_coefficient': '2 theta_k^2/theta_N^2'},
                       {'index_domain': 'k=N', 'expression': 'f(x_N)-f_star', 'coefficient': 1}],
    'constant_terms': []}
b4 = {**b3, 'basis_templates': {'interior': expression_structure['interior'],
                               'initial': expression_structure['initial'], 'terminal': expression_structure['terminal']},
      'basis_code': inspect.getsource(V_k_basis) + '\n' + inspect.getsource(V_k_basis_labels),
      'structure_code': 'function_coefficients = ' + repr(function_coefficients) + '\n' + inspect.getsource(V_k_structure),
      'coeff_by_k': {str(k): C.tolist() for k, C in coeff4.items()},
      'coeff_code': inspect.getsource(coeff_pattern), 'coefficient_formula_status': 'candidate',
      'expression_structure': expression_structure, 'unresolved_coefficients': [],
      'candidate_formula_comparisons': formula_errors, 'basis_search_results': search_results,
      'numerical_reconstruction': {'certificate_id': b3['certificate_id'], 'required_indices': list(range(N4+1)),
                                   'quadratic_residuals': quadratic_residuals, 'component_residuals': component_residuals,
                                   'tolerances': {'indep_tol': 1e-7, 'span_tol': 1e-5, 'component_atol': 1e-4, 'component_rtol': 1e-5},
                                   'passed': True},
      'numerical_certificate_verified': True, 'analytic_full_pep_verified': False, 'lyapunov_proof_verified': False}
