"""Revalidate selected certificate, then expose all weighted contributions."""
assert certificate_id(certificate) == certificate['certificate_id']
assert certificate['closed_form_search']['completed']
assert certificate['certificate_provenance']['pep_type'] == 'primal'
assert N_int == certificate['N_verify']
assert params_sp == {key: sp.S(value) for key, value in json.loads(certificate['params_json']).items()}
for path, expected in certificate['certificate_provenance']['source_hashes'].items():
    assert hashlib.sha256((notebook_dir / path).read_bytes()).hexdigest() == expected
assert Path(pf.__file__).resolve().is_relative_to(REPO_ROOT)
assert set(pb.relaxed_constraints) == set(certificate['relaxed_constraints'])
assert certificate['S_row_names'] == certificate['S_col_names'] == [str(v) for v in ctx.basis_vectors()]
assert certificate['normalization']['tau_name'] == certificate['tau_name'] == 'initial_condition'
assert certificate['tau_sol'] == certificate['named_dual_values']['initial_condition']
assert certificate['normalization']['bound_value'] == certificate['opt_value']
assert certificate['normalization']['initial_condition'] == 'D_h(x_star,x_0) <= R'
assert certificate['normalization']['performance_metric'] == 'f(x_N)-f(x_star)'
checks, certificate_residual = verify_certificate(ctx, pb, params_sp, certificate, certificate['dense_opt_value'])
assert checks['passed']
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
basis = list(ctx.basis_vectors())
S_array = np.asarray(certificate['S_matrix'], dtype=float)
S_scalar = scalar_from_gram(ctx, S_array)
weighted_terms = {}
interpolation_terms = {}
extra_duals = {}
saved_duals = certificate['named_dual_values']
tau_name = certificate['tau_name']
for constraint, origin, owner, group in inventory(ctx, pb):
    meta = certificate['constraint_metadata'][constraint.name]
    assert meta['kind'] == 'scalar' and meta['shape'] == []
    assert meta['relaxed'] == (constraint.name in pb.relaxed_constraints)
    value = saved_duals[constraint.name]
    if meta['relaxed']:
        assert value is None
        continue
    assert value is not None and np.isfinite(value)
    assert constraint.cmp == pf.Comparator.LE
    assert value >= -1e-6
    contribution = value * (pf.Scalar.zero() + constraint.lhs - constraint.rhs)
    weighted_terms[constraint.name] = contribution
    if origin == 'interpolation':
        interpolation_terms[constraint.name] = contribution
    elif constraint.name != tau_name:
        extra_duals[constraint.name] = value
assert not extra_duals
certificate_checked = True
tol = certificate['numerical_checks']['tolerances']
print('Saved certificate revalidated:', checks['residuals'])
