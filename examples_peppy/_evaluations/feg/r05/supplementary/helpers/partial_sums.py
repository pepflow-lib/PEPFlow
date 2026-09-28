"""Reconstruct, group and audit the selected certificate, without solving."""
import hashlib
import json
import numpy as np
import pepflow as pf
from verify_certificate import verify_saved
import runtime

KEYS = ('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')


def partial_sums(certificate, dense_value):
    digest = hashlib.sha256(json.dumps({k: certificate[k] for k in KEYS}, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    assert digest == certificate['certificate_id']
    assert certificate['closed_form_search']['completed']
    for relative, expected in certificate['certificate_provenance']['source_hashes'].items():
        assert hashlib.sha256((runtime.ROOT / relative).read_bytes()).hexdigest() == expected
    assert certificate['certificate_provenance']['pep_type'] == 'primal'
    assert certificate['params_json'] == '{"L": 1, "R": 1}'
    assert certificate['normalization']['tau_name'] == certificate['tau_name'] == 'initial_condition'
    assert certificate['normalization']['bound_value'] == certificate['opt_value']
    assert certificate['named_dual_values']['initial_condition'] == certificate['tau_sol']
    ctx, pb, obj, pm, checked, numerical_checks = verify_saved(certificate, dense_value)
    n = certificate['N_verify']
    basis = ctx.basis_vectors()
    assert certificate['S_row_names'] == certificate['S_col_names'] == [str(v) for v in basis]
    groups = ctx.get_constraint_data(obj)
    assert not groups.psd_dict and not ctx.func_to_triplets and len(ctx.oper_to_duplets) == 1
    terms = {}
    for group, constraints in groups.sc_dict.items():
        for c in constraints:
            expected = dict(origin='interpolation', owner=str(obj), group=group, kind='scalar', comparator=c.cmp.value, shape=[], relaxed=c.name in certificate['relaxed_constraints'])
            assert certificate['constraint_metadata'][c.name] == expected
            value = certificate['named_dual_values'][c.name]
            if value is not None:
                assert c.cmp.value == 'LE'
                terms[c.name] = value * (c.lhs-c.rhs)
    # A single PSD block retains every saved LDL component, including tiny terms.
    D = np.asarray(certificate['numerical_decomposition']['D'])
    E = np.asarray(certificate['numerical_decomposition']['ell_coords'])
    ell = [sum((float(coef)*v for coef, v in zip(row, basis)), pf.Vector.zero()) for row in E]
    S_block = sum((float(D[i,j])*ell[i]*ell[j] for i,j in np.ndindex(D.shape)), pf.Scalar.zero())
    S_matrix = np.asarray(certificate['S_matrix'])
    assert np.allclose(E.T @ D @ E, S_matrix, atol=1e-5, rtol=0)
    assert np.linalg.eigvalsh(S_matrix).min() >= -1e-6
    S_assignment = {'complete_S': 'boundary'}
    assignment = {}
    for name in terms:
        if name == f'A monotone:x_{n},x_star':
            assignment[name] = 'boundary'
        else:
            target = name.split(',')[1]
            assert target.startswith('x_') and target[2:].isdigit()
            assignment[name] = int(target[2:])-1
    assert sum(v == 'boundary' for v in assignment.values()) == 1
    assert all(v == 'boundary' or (isinstance(v, int) and 0 <= v < n) for v in assignment.values())
    lyap = [pf.Scalar.zero()]
    partial_sum = pf.Scalar.zero()
    for step in range(n):
        partial_sum += sum((terms[name] for name, target in assignment.items() if target == step), pf.Scalar.zero())
        lyap.append(partial_sum)
    values = [pm.eval_scalar(v) for v in lyap]
    singular_values = [np.linalg.svd(np.asarray(v.inner_prod_coords, dtype=float), compute_uv=False).tolist() for v in values]
    ranks = [int(np.sum(np.asarray(s) > 1e-4)) for s in singular_values]
    for k, rank in enumerate(ranks):
        print(f'rank V_{k}: {rank}')
        if k == 0:
            print()
    print('Interior rank is constant at this N:', len(set(ranks[1:-1])) == 1 and n-1 >= 3, 'boundary exclusions:', (1,1))
    leftover = sum((terms[name] for name, target in assignment.items() if target == 'boundary'), pf.Scalar.zero()) - S_block
    coverage = lyap[n] + leftover - (sum(terms.values(), pf.Scalar.zero()) - S_block)
    residuals = []
    for expression in [coverage, S_block-sum((float(S_matrix[i,j])*basis[i]*basis[j] for i,j in np.ndindex(S_matrix.shape)), pf.Scalar.zero())]:
        ev = pm.eval_scalar(expression)
        residuals.extend(float(np.max(np.abs(np.asarray(c, dtype=float)), initial=0)) for c in [ev.inner_prod_coords, ev.func_coords, ev.offset])
    for k in range(n):
        increment = sum((terms[name] for name, target in assignment.items() if target == k), pf.Scalar.zero())
        ev = pm.eval_scalar(lyap[k+1]-lyap[k]-increment)
        residuals.extend(float(np.max(np.abs(np.asarray(c, dtype=float)), initial=0)) for c in [ev.inner_prod_coords, ev.func_coords, ev.offset])
    assert max(residuals) <= 1e-5
    # Every increment is a nonnegative linear combination of <=0 residuals.
    assert all(value >= -1e-6 for name, value in certificate['named_dual_values'].items() if value is not None)
    observation = dict(N=n, certificate_id=certificate['certificate_id'], recipe_id='chronological_interpolation_complete_S_boundary', rank_profile=ranks,
        rank_convention=dict(tolerance=1e-4, scaling='unscaled absolute singular values', coordinate_order='setup basis order'),
        rank_credible=all(not any(0.5e-4 < s < 2e-4 for s in ss) for ss in singular_values),
        certificate_checked=True, grouping_checked=True, singular_values=singular_values,
        maximum_coverage_residual=max(residuals), numerical_checks=numerical_checks,
        constraint_assignment=assignment, S_assignment=S_assignment,
        boundary_constraints=[name for name, target in assignment.items() if target == 'boundary'],
        boundary_S=['complete_S'], omitted_constraints=[], sign_convention='V[k+1]-V[k] is a nonnegative combination of normalized <=0 interpolation residuals',
        lyap_inner_prod_coords=[np.asarray(v.inner_prod_coords, dtype=float).tolist() for v in values],
        lyap_func_coords=[np.asarray(v.func_coords, dtype=float).tolist() for v in values], lyap_offsets=[float(v.offset) for v in values])
    return ctx, pb, obj, pm, lyap, observation

