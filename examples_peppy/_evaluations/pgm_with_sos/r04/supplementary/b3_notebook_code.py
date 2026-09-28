def reconstruct_partial_sums(certificate):
    import json
    N_int = certificate['N_verify']
    params_sp = json.loads(certificate['params_json'])
    ctx, pb, obj = get_pep_setup(N_int, params_sp)
    pb.set_relaxed_constraints(certificate['relaxed_constraints'])
    REPO_ROOT = notebook_dir

    import hashlib
    import json
    from pathlib import Path
    import numpy as np
    import sympy as sp
    import pepflow as pf
    from pepflow.constraint import ScalarConstraint
    from pepflow.operator import LinearOperatorTranspose

    from pepflow.utils import name_to_vector_tuple

    certificate_checked = False
    if not certificate.get("numerical_certificate_verified", False):
        raise ValueError("Recover or verify the complete numerical certificate in Block 2")
    if not certificate.get("closed_form_search", {}).get("completed", False):
        raise ValueError("Complete or recover Block 2's initial closed-form attempt")
    certificate_keys = (
        "N_verify", "params_json", "relaxed_constraints",
        "S_matrix", "S_row_names", "S_col_names", "basis_vectors", "basis_scalars",
        "opt_value", "tau_sol", "tau_name", "named_dual_values", "constraint_metadata",
        "normalization", "certificate_provenance", "numerical_checks",
        "numerical_decomposition",
    )
    payload = {key: certificate[key] for key in certificate_keys}
    digest = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()
    if digest != certificate["certificate_id"]:
        raise ValueError("Certificate components changed; recover one coherent certificate")
    provenance = certificate["certificate_provenance"]
    if provenance["pep_type"] not in ("primal", "dual"):
        raise ValueError("Recover and verify the certificate's actual dual sign convention")
    for relative_path, expected_hash in provenance["source_hashes"].items():
        source_path = (REPO_ROOT / relative_path).resolve()
        if not source_path.is_relative_to(REPO_ROOT):
            raise ValueError("Certificate source path must stay in the selected repository")
        if hashlib.sha256(source_path.read_bytes()).hexdigest() != expected_hash:
            raise ValueError(f"Certificate source changed: {relative_path}")
    if not Path(pf.__file__).resolve().is_relative_to(REPO_ROOT):
        raise ValueError("The imported PEPFlow source is not the selected repository")
    if N_int != certificate["N_verify"]:
        raise ValueError("Certificate horizon differs from the rebuilt setup")
    saved_params = json.loads(certificate["params_json"])
    expected_params = {
        key: (sp.Rational(value) if isinstance(value, str) else
              sp.nsimplify(value, rational=True, tolerance=1e-9)
              if isinstance(value, float) else sp.S(value))
        for key, value in saved_params.items()
    }
    if params_sp != expected_params:
        raise ValueError("Certificate parameters differ from the rebuilt setup")
    if not certificate["numerical_checks"]["passed"]:
        raise ValueError("Block 2 numerical checks did not pass")
    if provenance['pep_type'] == 'dual':
        # This sample contains only scalar LE primal residuals, whose signs agree.
        assert all(meta['kind'] == 'scalar' and meta['comparator'] == 'LE' for meta in certificate['constraint_metadata'].values())
        assert certificate.get('sign_convention')
    tol = certificate["numerical_checks" ]["tolerances"]

    records = [(c, "initial", None, None) for c in pb.init_conditions]
    owners = list(ctx.func_to_triplets) + [
        owner for owner in ctx.oper_to_duplets
        if not isinstance(owner, LinearOperatorTranspose)
    ]
    for owner in owners:
        data = ctx.get_constraint_data(owner)
        for group, family in data.sc_dict.items():
            records.extend((c, "interpolation", str(owner), str(group)) for c in family)
        records.extend((c, "interpolation", str(owner), str(group))
                       for group, c in data.psd_dict.items())
    constraints_by_name = {c.name: c for c, _, _, _ in records}
    if len(constraints_by_name) != len(records):
        raise ValueError("Constraint names must identify one unique contribution")
    saved_meta = certificate["constraint_metadata"]
    saved_duals = certificate["named_dual_values"]
    if set(constraints_by_name) != set(saved_meta) or set(saved_duals) != set(saved_meta):
        raise ValueError("The saved certificate does not cover the rebuilt constraints")
    relaxed = set(certificate["relaxed_constraints"])
    if set(pb.relaxed_constraints) != relaxed or not relaxed.issubset(constraints_by_name):
        raise ValueError("The selected relaxation differs from the saved certificate")
    if pb.ctx is not ctx:
        raise ValueError("The builder and expression context differ")
    basis = list(ctx.basis_vectors())
    basis_labels = [repr(v) for v in basis]
    scalar_labels = [repr(v) for v in ctx.basis_scalars()]
    if basis_labels != certificate["basis_vectors"] or scalar_labels != certificate["basis_scalars"]:
        raise ValueError("Certificate coordinate order differs from the rebuilt context")
    if certificate["S_row_names"] != basis_labels or certificate["S_col_names"] != basis_labels:
        raise ValueError("S labels do not match the rebuilt basis")
    S_array = np.asarray(certificate["S_matrix"], dtype=float)
    if S_array.shape != (len(basis), len(basis)) or not np.all(np.isfinite(S_array)):
        raise ValueError("Invalid S shape or entries")
    if not np.allclose(S_array, S_array.T, atol=tol["psd_tol"], rtol=0):
        raise ValueError("S is not numerically symmetric")
    if len(basis) and np.linalg.eigvalsh((S_array + S_array.T) / 2).min() < -tol["psd_tol"]:
        raise ValueError("S failed the recorded PSD tolerance")

    pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
    S_scalar = sum((float(S_array[i, j]) * basis[i] * basis[j]
                    for i, j in np.ndindex(S_array.shape)), pf.Scalar.zero())

    weighted_terms = {}
    interpolation_terms = {}
    interpolation_pairs = {}
    extra_terms = {}
    extra_duals = {}
    for constraint, origin, owner, group in records:
        name = constraint.name
        kind = "scalar" if isinstance(constraint, ScalarConstraint) else "psd"
        residual = constraint.lhs - constraint.rhs
        shape = [] if kind == "scalar" else list(np.shape(residual))
        expected_meta = dict(origin=origin, owner=owner, group=group, kind=kind,
                             comparator=constraint.cmp.value, shape=shape,
                             relaxed=name in relaxed)
        if any(saved_meta[name].get(key) != value for key, value in expected_meta.items()):
            raise ValueError(f"Constraint metadata changed: {name}")
        value = saved_duals[name]
        if name in relaxed:
            if value is not None:
                raise ValueError(f"A relaxed constraint must have no retained multiplier: {name}")
            continue
        if value is None:
            raise ValueError(f"Missing unrelaxed dual: {name}")
        dual = np.asarray(value, dtype=float)
        if list(dual.shape) != shape or not np.all(np.isfinite(dual)):
            raise ValueError(f"Invalid saved dual: {name}")
        # Normalize inequalities to residual <= 0; primal equality duals keep their sign.
        if constraint.cmp.name in ("GE", "SEQ"):
            residual = -residual
        if kind == "scalar":
            if constraint.cmp.name != "EQ" and float(dual) < -tol["dual_tol"]:
                raise ValueError(f"Negative inequality multiplier: {name}")
            contribution = pf.Scalar.zero() + float(dual) * residual
        else:
            if constraint.cmp.name != "EQ" and not np.allclose(dual, dual.T, atol=tol["psd_tol"], rtol=0):
                raise ValueError(f"Nonsymmetric matrix dual: {name}")
            if constraint.cmp.name != "EQ" and dual.size and np.linalg.eigvalsh((dual + dual.T) / 2).min() < -tol["psd_tol"]:
                raise ValueError(f"Matrix dual is not PSD: {name}")
            contribution = sum((float(dual[i, j]) * residual[j, i]
                                for i, j in np.ndindex(dual.shape)), pf.Scalar.zero())
        weighted_terms[name] = contribution
        if origin == "interpolation" and kind == "scalar":
            interpolation_terms[name] = contribution
            try:
                interpolation_pairs[name] = name_to_vector_tuple(name)
            except (ValueError, IndexError):
                interpolation_pairs[name] = None  # Assign this term explicitly when grouping.
        elif name != certificate["tau_name"]:
            extra_terms[name] = contribution
            extra_duals[name] = value

    tau_name = certificate["tau_name"]
    if (tau_name not in weighted_terms or saved_meta[tau_name]["origin"] != "initial"
            or saved_meta[tau_name]["kind"] != "scalar" or tau_name in relaxed
            or certificate["normalization"]["tau_name"] != tau_name):
        raise ValueError("Missing or inconsistent bound normalization constraint")
    if not np.allclose(saved_duals[tau_name], certificate["tau_sol"], atol=tol["dual_tol"], rtol=0):
        raise ValueError("The saved normalization dual is inconsistent")
    if not np.isfinite(certificate["opt_value"]) or not np.allclose(
        certificate["normalization"]["bound_value"], certificate["opt_value"],
        atol=tol["identity_atol"], rtol=tol["identity_rtol"]
    ):
        raise ValueError("The saved bound/normalization is inconsistent")
    certificate_diff = (pb.performance_metric - float(certificate["opt_value"])
                        - sum(weighted_terms.values(), pf.Scalar.zero()) + S_scalar)
    evaluated_diff = pm.eval_scalar(certificate_diff)
    for label, coords in (
        ("Gram", evaluated_diff.inner_prod_coords),
        ("function", evaluated_diff.func_coords),
        ("offset", np.asarray(evaluated_diff.offset)),
    ):
        if not np.allclose(np.asarray(coords, dtype=float), 0,
                           atol=tol["identity_atol"], rtol=tol["identity_rtol"]):
            raise ValueError(f"Numerical certificate {label} identity failed")
    decomposition = certificate["numerical_decomposition"]
    D_saved = np.asarray(decomposition["D"], dtype=float)
    E_saved = np.asarray(decomposition["ell_coords"], dtype=float)
    if decomposition["basis_labels"] != basis_labels or E_saved.ndim != 2:
        raise ValueError("Numerical S decomposition basis differs")
    if E_saved.shape[1] != len(basis) or D_saved.shape != (E_saved.shape[0], E_saved.shape[0]):
        raise ValueError("Numerical S decomposition shape differs")
    if not np.all(np.isfinite(D_saved)) or not np.all(np.isfinite(E_saved)):
        raise ValueError("Numerical S decomposition contains nonfinite values")
    if not np.allclose(E_saved.T @ D_saved @ E_saved, S_array,
                       atol=tol["reconstruction_atol"], rtol=tol["reconstruction_rtol"]):
        raise ValueError("Numerical S decomposition does not reconstruct this certificate")
    certificate_checked = True
    print("Numerical certificate checked for this N and parameter sample.")


    # Direct pieces from the B2 aid, each a sum of three nonnegative squares.
    pieces, coefficients, vectors = supplied_sos(ctx, N_int, 1)
    S_piece_terms = {f'S_{i+1}':piece for i,piece in enumerate(pieces)}
    S_assignment = {name:i for i,name in enumerate(S_piece_terms)}
    # With interpolation residuals <= 0, every assigned contribution minus its
    # nonnegative S piece gives a nonpositive increment.
    group_terms = {name:term for name,term in weighted_terms.items() if name != tau_name}
    term_assignment = {}
    for name in group_terms:
        left, right = name.split(':')[1].split(',')
        term_assignment[name] = int(right[2:])-1
    assert set(term_assignment) == set(group_terms)
    assert set(S_assignment) == set(S_piece_terms)
    lyap = [pf.Scalar.zero()]
    partial_sum = sum((term for name,term in group_terms.items() if term_assignment[name] == -1), pf.Scalar.zero())
    for step in range(N_int):
        partial_sum += sum((term for name,term in group_terms.items() if term_assignment[name] == step), pf.Scalar.zero())
        partial_sum -= S_piece_terms[f'S_{step+1}']
        lyap.append(partial_sum)
    rank_tolerance = 1e-4
    rank_left, rank_right = 1, 1
    ranks, singular_values = [], []
    for k, value in enumerate(lyap):
        matrix = pm.eval_scalar(value).inner_prod_coords.astype(float)
        singular_values.append(np.linalg.svd(matrix,compute_uv=False).tolist())
        rank = int(np.linalg.matrix_rank(matrix,tol=rank_tolerance))
        ranks.append(rank)
        print(f'rank V_{k}: {rank}')
        if k == 0:
            print()
    retained_ranks = ranks[rank_left:N_int+1-rank_right]
    print('Interior rank is constant at this N:', len(retained_ranks)>=3 and len(set(retained_ranks))==1,'boundary exclusions:',(rank_left,rank_right))
    assert len(retained_ranks)>=3 and len(set(retained_ranks))==1
    # Credibility check records all singular values, including numerical residuals.
    # No retained singular value lies in [tolerance/2, 2*tolerance].
    rank_credible = all(not any(5e-5 <= v <= 2e-4 for v in singular_values[k]) for k in range(1,N_int))
    assert rank_credible




    boundary_names = [name for name, step in term_assignment.items() if step == "boundary"]
    boundary_S = [name for name, step in S_assignment.items() if step == "boundary"]
    if sum(name in interpolation_terms for name in boundary_names) > 1 or len(boundary_S) > 1:
        raise ValueError("Revisit the permitted terminal interpolation/S leftovers")
    omitted = sum((group_terms[name] for name, step in term_assignment.items()
                   if step == "omitted"), pf.Scalar.zero())
    leftover = sum((group_terms[name] for name in boundary_names), pf.Scalar.zero())
    leftover -= sum((S_piece_terms[name] for name in boundary_S), pf.Scalar.zero())
    coverage_diff = (lyap[N_int] + leftover + omitted
                     - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar))
    piece_diff = sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar
    for label, expression in (("coverage", coverage_diff), ("S pieces", piece_diff), ("omitted", omitted)):
        value = pm.eval_scalar(expression)
        for coords in (value.inner_prod_coords, value.func_coords, np.asarray(value.offset)):
            if not np.allclose(np.asarray(coords, dtype=float), 0,
                               atol=tol["identity_atol"], rtol=tol["identity_rtol"]):
                raise ValueError(f"Full-coordinate {label} check failed")
    # Every subtracted S piece must have the nonnegative numerical sign used here.
    for name, piece in S_piece_terms.items():
        value = pm.eval_scalar(piece)
        matrix = np.asarray(value.inner_prod_coords, dtype=float)
        if not np.allclose(value.func_coords, 0, atol=tol["identity_atol"], rtol=0) or not np.allclose(value.offset, 0, atol=tol["identity_atol"], rtol=0):
            raise ValueError(f"S piece has unexpected function/offset terms: {name}")
        if matrix.size and np.linalg.eigvalsh((matrix + matrix.T) / 2).min() < -tol["psd_tol"]:
            raise ValueError(f"S piece has the wrong numerical sign: {name}")
    # Step identities follow the chosen assignments; check them, including the initial terms.
    for k in range(N_int):
        assigned_steps = {-1, 0} if k == 0 else {k}
        increment = sum((group_terms[name] for name, step in term_assignment.items()
                         if step in assigned_steps), pf.Scalar.zero())
        increment -= sum((S_piece_terms[name] for name, step in S_assignment.items()
                          if step in assigned_steps), pf.Scalar.zero())
        value = pm.eval_scalar(lyap[k + 1] - lyap[k] - increment)
        for coords in (value.inner_prod_coords, value.func_coords, np.asarray(value.offset)):
            if not np.allclose(np.asarray(coords, dtype=float), 0,
                               atol=tol["identity_atol"], rtol=tol["identity_rtol"]):
                raise ValueError(f"Partial-sum increment identity failed at k={k}")
    grouping_checked = True
    M_final = pm.eval_scalar(lyap[N_int]).inner_prod_coords.astype(float)
    rank_final = int(np.linalg.matrix_rank(M_final, tol=rank_tolerance))
    print(f"lyap[{N_int}] rank:", rank_final)
    print("Coverage checked with all scalar components and explicit boundary leftovers.")

    evaluated = [pm.eval_scalar(value) for value in lyap]
    observation = dict(N=N_int,certificate_id=certificate['certificate_id'],recipe_id='forward_star_consecutive_three_sos_refined_dual',rank_profile=ranks,rank_convention={'tolerance':1e-4,'scaling':'unscaled Gram coordinates','order':'setup basis order'},rank_credible=rank_credible,certificate_checked=certificate_checked,grouping_checked=grouping_checked,singular_values=singular_values)
    return dict(observation=observation,lyap_inner_prod_coords=[np.array(v.inner_prod_coords,dtype=float).tolist() for v in evaluated],lyap_func_coords=[np.array(v.func_coords,dtype=float).tolist() for v in evaluated],lyap_offsets=[float(v.offset) for v in evaluated],grouping_coverage=dict(constraint_assignment=term_assignment,S_assignment=S_assignment,normalization_constraint=tau_name,boundary_constraints=boundary_names,boundary_S=boundary_S,omitted_constraints=[],checked=True),extra_duals=extra_duals)

certificate = json.loads((notebook_dir/'state/pgm_b2.json').read_text())
other_certificate = json.loads((notebook_dir/'supplementary/b2-N6-certificate.json').read_text())
print('Selected horizon:', certificate['N_verify'])
selected_partial_sums = reconstruct_partial_sums(certificate)
print('Confirmation horizon:', other_certificate['N_verify'])
other_partial_sums = reconstruct_partial_sums(other_certificate)
rank_samples = [selected_partial_sums['observation'],other_partial_sums['observation']]
assert len({sample['N'] for sample in rank_samples}) == 2
assert all(sample['rank_profile'][1:sample['N']] == [4]*(sample['N']-1) for sample in rank_samples)
assert all(sample['certificate_checked'] and sample['grouping_checked'] and sample['rank_credible'] for sample in rank_samples)
print('Cross-horizon confirmation: N=4,6; interior rank 4; exclusions (1,1); unscaled tolerance 1e-4.')
