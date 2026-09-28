"""Replay a complete OGM numerical certificate, without another solve."""
import hashlib
import json

import numpy as np
import pepflow as pf
import sympy as sp
from pepflow.utils import Comparator

from ogm_setup import get_pep_setup, theta_sequence
from runtime import ROOT


def verify_certificate(state):
    for name, expected in state['certificate_provenance']['source_hashes'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
    N = state['N_verify']
    ctx, pb, obj = get_pep_setup(N, {'L': 1, 'R': 1})
    interpolation = obj.get_interpolation_constraints(ctx)
    entries = list(pb.init_conditions) + list(interpolation)
    assert set(c.name for c in entries) == set(state['constraint_metadata']) == set(state['named_dual_values'])
    assert state['basis_vectors'] == [str(v) for v in ctx.basis_vectors()]
    assert state['basis_scalars'] == [str(v) for v in ctx.basis_scalars()]
    assert state['S_row_names'] == state['basis_vectors'] == state['S_col_names']
    pm = pf.ExpressionManager(ctx, resolve_parameters={'L': sp.Integer(1), 'R': sp.Integer(1)})
    theta = theta_sequence(N)
    thetaN = theta[-1]
    # Candidate single square in the original basis, retaining its entire matrix.
    w = ctx[f'z_{N}'] - ctx['x_star'] - thetaN * ctx[f'g_{N}']
    S_numeric = w**2 / (2 * thetaN**2)
    E = np.asarray(pm.eval_vector(w).coords, dtype=float).reshape(1, -1)
    D = np.array([[1 / (2 * thetaN**2)]])
    S_reconstructed = E.T @ D @ E
    S_array = np.asarray(state['S_matrix'], dtype=float)
    weights = pf.Scalar.zero()
    inequality_values = []
    lambda_errors = []
    candidate_lambdas = {}
    def index(tag):
        return 0 if tag == 'z_0' else -1 if tag == 'x_star' else int(tag.split('_')[1])
    for con in entries:
        meta = state['constraint_metadata'][con.name]
        value = state['named_dual_values'][con.name]
        assert meta['kind'] == 'scalar' and meta['comparator'] == con.cmp.value
        assert meta['relaxed'] == (con.name in state['relaxed_constraints'])
        if meta['relaxed']:
            assert value is None
            continue
        assert value is not None and np.isfinite(value)
        residual = con.lhs - con.rhs
        if con.cmp in (Comparator.GE, Comparator.SEQ):
            residual = -residual
        weights += float(value) * (pf.Scalar.zero() + residual)
        if con.cmp != Comparator.EQ:
            inequality_values.append(float(value))
        if meta['origin'] == 'interpolation':
            left, right = con.name.split(':')[1].split(',')
            i, j = index(left), index(right)
            if i == -1:
                candidate = 1 / thetaN if j == N else 2 * theta[j] / thetaN**2
            else:
                assert j == i + 1
                candidate = 2 * theta[i]**2 / thetaN**2
            candidate_lambdas[con.name] = candidate
            lambda_errors.append(abs(value - candidate))
    diff = pb.performance_metric - state['opt_value'] - weights + S_numeric
    checked = pm.eval_scalar(diff)
    def max_abs(a):
        return float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0.0))
    residuals = dict(identity_gram_max_abs=max_abs(checked.inner_prod_coords), identity_func_max_abs=max_abs(checked.func_coords), identity_offset_abs=max_abs(checked.offset), S_reconstruction_max_abs=max_abs(S_reconstructed-S_array), minimum_scalar_inequality_dual=min(inequality_values), minimum_S_eigenvalue=float(np.linalg.eigvalsh(S_array).min()), minimum_matrix_inequality_eigenvalue=0.0, lambda_candidate_max_abs=max(lambda_errors), conjecture_gap=abs(state['opt_value'] - 1/(2*thetaN**2)))
    tolerances = dict(identity_atol=1e-5, identity_rtol=0.0, reconstruction_atol=1e-4, reconstruction_rtol=1e-5, dual_tol=1e-6, psd_tol=1e-6, dense_opt_atol=1e-5)
    assert state['certificate_provenance']['solver_status'] == 'optimal'
    assert all(residuals[k] <= tolerances['identity_atol'] for k in ('identity_gram_max_abs','identity_func_max_abs','identity_offset_abs'))
    assert np.allclose(S_array, S_array.T, atol=1e-6, rtol=0)
    assert np.allclose(S_reconstructed, S_array, atol=1e-4, rtol=1e-5)
    assert residuals['minimum_scalar_inequality_dual'] >= -1e-6
    assert residuals['minimum_S_eigenvalue'] >= -1e-6
    assert residuals['lambda_candidate_max_abs'] <= 1e-4
    assert residuals['conjecture_gap'] <= 1e-5
    decomposition = dict(method='direct', D=D.tolist(), ell_coords=E.tolist(), basis_labels=state['basis_vectors'], discarded_matrix_max_abs=residuals['S_reconstruction_max_abs'], candidate_source='w = z_N - x_star - theta_N*g_N; S_numeric = w**2/(2*theta_N**2), L=1')
    return ctx, pb, pm, checked, S_reconstructed, candidate_lambdas, decomposition, {'tolerances': tolerances, 'residuals': residuals, 'passed': True}


def certificate_digest(state):
    keys = ('N_verify', 'params_json', 'relaxed_constraints', 'S_matrix', 'S_row_names', 'S_col_names', 'basis_vectors', 'basis_scalars', 'opt_value', 'tau_sol', 'tau_name', 'named_dual_values', 'constraint_metadata', 'normalization', 'certificate_provenance', 'numerical_checks', 'numerical_decomposition')
    return hashlib.sha256(json.dumps({key: state[key] for key in keys}, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

