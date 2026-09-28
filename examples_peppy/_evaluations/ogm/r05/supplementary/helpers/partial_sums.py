"""Replay a certificate and group chronological smooth interpolation terms."""
import hashlib
import json

import numpy as np
import pepflow as pf

from certificate import digest_state, inventory, scalar_coordinates, verify_certificate
from runtime import NOTEBOOK_DIR


def rebuild(certificate):
    from ogm_setup import get_pep_setup

    assert certificate['closed_form_search']['completed']
    assert digest_state(certificate) == certificate['certificate_id']
    for relative, expected in certificate['certificate_provenance']['source_hashes'].items():
        assert hashlib.sha256((NOTEBOOK_DIR / relative).read_bytes()).hexdigest() == expected
    N = certificate['N_verify']
    params = json.loads(certificate['params_json'])
    ctx, pb, obj = get_pep_setup(N, params)
    pb.set_relaxed_constraints(certificate['relaxed_constraints'])
    checks, _ = verify_certificate(ctx, pb, certificate, certificate['opt_value'])
    assert checks['passed']
    assert certificate['S_row_names'] == certificate['S_col_names'] == certificate['basis_vectors']
    assert certificate['normalization']['bound_value'] == certificate['opt_value']
    assert certificate['named_dual_values']['initial_condition'] == certificate['tau_sol']
    return ctx, pb, obj, pf.ExpressionManager(ctx, resolve_parameters=params)


def construct(certificate, verbose=True):
    ctx, pb, obj, pm = rebuild(certificate)
    N = certificate['N_verify']
    basis = ctx.basis_vectors()
    group_terms, term_assignment = {}, {}
    for c, origin, owner, group in inventory(ctx, pb):
        value = certificate['named_dual_values'][c.name]
        if origin == 'initial' or value is None:
            continue
        residual = c.lhs - c.rhs
        if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
            residual = -residual
        group_terms[c.name] = value * (pf.Scalar.zero() + residual)
        left, right = c.name.split(':')[1].split(',')
        j = 0 if right == 'z_0' else int(right.split('_')[1])
        assert left == 'x_star' or left == ('z_0' if j == 1 else f'x_{j-1}')
        term_assignment[c.name] = j - 1
    S = np.asarray(certificate['S_matrix'], dtype=float)
    S_scalar = sum((float(S[i, j]) * basis[i] * basis[j]
                    for i, j in np.ndindex(S.shape)), pf.Scalar.zero())
    # The candidate rank-one square is accurate to 1e-4. Retain the complete
    # saved PSD block, including small numerical components, at the last step.
    S_piece_terms = {'terminal_full_S': S_scalar}
    S_assignment = {'terminal_full_S': N - 1}
    assert np.linalg.eigvalsh(S).min() >= -1e-6
    lyap = [pf.Scalar.zero()]
    partial_sum = sum((term for name, term in group_terms.items()
                       if term_assignment[name] == -1), pf.Scalar.zero())
    for k in range(N):
        partial_sum += sum((term for name, term in group_terms.items()
                           if term_assignment[name] == k), pf.Scalar.zero())
        partial_sum -= sum((piece for name, piece in S_piece_terms.items()
                           if S_assignment[name] == k), pf.Scalar.zero())
        lyap.append(partial_sum)
    coords = [scalar_coordinates(pm, v) for v in lyap]
    singular_values = [np.linalg.svd(np.asarray(c['gram']), compute_uv=False).tolist() for c in coords]
    ranks = [int(np.sum(np.array(s) > 1e-4)) for s in singular_values]
    if verbose:
        for k, rank in enumerate(ranks):
            print(f'rank V_{k}: {rank}')
            if k == 0:
                print()
        print('Interior rank is constant at this N:', len(ranks[1:-1]) >= 3 and len(set(ranks[1:-1])) == 1,
              'boundary exclusions:', (1, 1))
    coverage = scalar_coordinates(pm, lyap[N] - sum(group_terms.values(), pf.Scalar.zero()) + S_scalar)
    def maximum(c):
        return max(float(np.max(np.abs(c['gram']), initial=0)),
                   float(np.max(np.abs(c['func']), initial=0)), abs(c['offset']))
    assert maximum(coverage) <= 1e-5
    increment_errors = []
    for k in range(N):
        assigned = {-1, 0} if k == 0 else {k}
        increment = sum((v for name, v in group_terms.items() if term_assignment[name] in assigned), pf.Scalar.zero())
        increment -= sum((v for name, v in S_piece_terms.items() if S_assignment[name] in assigned), pf.Scalar.zero())
        error = maximum(scalar_coordinates(pm, lyap[k+1] - lyap[k] - increment))
        assert error <= 1e-5
        increment_errors.append(error)
    result = {
        'N': N, 'certificate_id': certificate['certificate_id'],
        'recipe_id': 'chronological_star_and_forward_pairs_terminal_full_S',
        'rank_profile': ranks, 'singular_values': singular_values,
        'rank_convention': {'tolerance': 1e-4, 'scaling': 'none, raw Gram coordinate matrix',
                            'coordinate_order': 'x0, xstar, gradients chronologically'},
        'rank_credible': all(not any(5e-5 <= s <= 2e-4 for s in values) for values in singular_values),
        'certificate_checked': True, 'grouping_checked': True,
        'coverage_coordinates': coverage, 'coverage_max_abs': maximum(coverage),
        'increment_errors': increment_errors, 'lyap_coordinates': coords,
        'constraint_assignment': term_assignment, 'S_assignment': S_assignment,
        'boundary_constraints': [], 'boundary_S': [], 'omitted_constraints': [],
        'sign_convention': 'Residuals <=0 with nonnegative duals; subtract PSD S only at terminal. Hence V_(k+1)<=V_k, including combined initial contributions.'}
    return result
