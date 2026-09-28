# This saved notebook fragment shares its caller's execution namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821


def reconstruct_and_group(certificate):
    import sympy as sp

    import pepflow as pf

    N_int = certificate["N_verify"]
    params_sp: dict[str, pf.NUMERICAL_TYPE] = {"L": sp.Integer(1), "R": sp.Integer(1)}
    ctx, pb, obj = get_pep_setup(N_int, params_sp)
    pb.set_relaxed_constraints(certificate["relaxed_constraints"])
    import hashlib
    import json
    from pathlib import Path

    import numpy as np
    import sympy as sp

    import pepflow as pf
    from pepflow.constraint import ScalarConstraint
    from pepflow.operator import LinearOperatorTranspose
    from pepflow.pep_result import MatrixWithNames
    from pepflow.utils import name_to_vector_tuple

    certificate_checked = False
    if not certificate.get("numerical_certificate_verified", False):
        raise ValueError(
            "Recover or verify the complete numerical certificate in Block 2"
        )
    if not certificate.get("closed_form_search", {}).get("completed", False):
        raise ValueError("Complete or recover Block 2's initial closed-form attempt")
    certificate_keys = (
        "N_verify",
        "params_json",
        "relaxed_constraints",
        "S_matrix",
        "S_row_names",
        "S_col_names",
        "basis_vectors",
        "basis_scalars",
        "opt_value",
        "tau_sol",
        "tau_name",
        "named_dual_values",
        "constraint_metadata",
        "normalization",
        "certificate_provenance",
        "numerical_checks",
        "numerical_decomposition",
    )
    payload = {key: certificate[key] for key in certificate_keys}
    digest = hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    ).hexdigest()
    if digest != certificate["certificate_id"]:
        raise ValueError(
            "Certificate components changed; recover one coherent certificate"
        )
    provenance = certificate["certificate_provenance"]
    if provenance["pep_type"] != "primal":
        raise ValueError(
            "Recover and verify the certificate's actual dual sign convention"
        )
    for relative_path, expected_hash in provenance["source_hashes"].items():
        source_path = (NOTEBOOK_DIR / relative_path).resolve()
        if not source_path.is_relative_to(NOTEBOOK_DIR):
            raise ValueError(
                "Certificate source path must stay in the selected repository"
            )
        if hashlib.sha256(source_path.read_bytes()).hexdigest() != expected_hash:
            raise ValueError(f"Certificate source changed: {relative_path}")
    if not Path(pf.__file__).resolve().is_relative_to(REPO_ROOT):
        raise ValueError("The imported PEPFlow source is not the selected repository")
    if N_int != certificate["N_verify"]:
        raise ValueError("Certificate horizon differs from the rebuilt setup")
    saved_params = json.loads(certificate["params_json"])
    expected_params = {
        key: (
            sp.Rational(value)
            if isinstance(value, str)
            else sp.nsimplify(value, rational=True, tolerance=1e-9)
            if isinstance(value, float)
            else sp.S(value)
        )
        for key, value in saved_params.items()
    }
    if params_sp != expected_params:
        raise ValueError("Certificate parameters differ from the rebuilt setup")
    if not certificate["numerical_checks"]["passed"]:
        raise ValueError("Block 2 numerical checks did not pass")
    tol = certificate["numerical_checks"]["tolerances"]

    records = [(c, "initial", None, None) for c in pb.init_conditions]
    owners = list(ctx.func_to_triplets) + [
        owner
        for owner in ctx.oper_to_duplets
        if not isinstance(owner, LinearOperatorTranspose)
    ]
    for owner in owners:
        data = ctx.get_constraint_data(owner)
        for group, family in data.sc_dict.items():
            records.extend((c, "interpolation", str(owner), str(group)) for c in family)
        records.extend(
            (c, "interpolation", str(owner), str(group))
            for group, c in data.psd_dict.items()
        )
    constraints_by_name = {c.name: c for c, _, _, _ in records}
    if len(constraints_by_name) != len(records):
        raise ValueError("Constraint names must identify one unique contribution")
    saved_meta = certificate["constraint_metadata"]
    saved_duals = certificate["named_dual_values"]
    if set(constraints_by_name) != set(saved_meta) or set(saved_duals) != set(
        saved_meta
    ):
        raise ValueError("The saved certificate does not cover the rebuilt constraints")
    relaxed = set(certificate["relaxed_constraints"])
    if set(pb.relaxed_constraints) != relaxed or not relaxed.issubset(
        constraints_by_name
    ):
        raise ValueError("The selected relaxation differs from the saved certificate")
    if pb.ctx is not ctx:
        raise ValueError("The builder and expression context differ")
    basis = list(ctx.basis_vectors())
    basis_labels = [repr(v) for v in basis]
    scalar_labels = [repr(v) for v in ctx.basis_scalars()]
    if (
        basis_labels != certificate["basis_vectors"]
        or scalar_labels != certificate["basis_scalars"]
    ):
        raise ValueError(
            "Certificate coordinate order differs from the rebuilt context"
        )
    if (
        certificate["S_row_names"] != basis_labels
        or certificate["S_col_names"] != basis_labels
    ):
        raise ValueError("S labels do not match the rebuilt basis")
    S_array = np.asarray(certificate["S_matrix"], dtype=float)
    if S_array.shape != (len(basis), len(basis)) or not np.all(np.isfinite(S_array)):
        raise ValueError("Invalid S shape or entries")
    if not np.allclose(S_array, S_array.T, atol=tol["psd_tol"], rtol=0):
        raise ValueError("S is not numerically symmetric")
    if (
        len(basis)
        and np.linalg.eigvalsh((S_array + S_array.T) / 2).min() < -tol["psd_tol"]
    ):
        raise ValueError("S failed the recorded PSD tolerance")
    S_sol = MatrixWithNames(S_array, basis_labels, basis_labels)
    pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
    S_scalar = sum(
        (
            float(S_array[i, j]) * basis[i] * basis[j]
            for i, j in np.ndindex(S_array.shape)
        ),
        pf.Scalar.zero(),
    )

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
        expected_meta = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind=kind,
            comparator=constraint.cmp.value,
            shape=shape,
            relaxed=name in relaxed,
        )
        if any(
            saved_meta[name].get(key) != value for key, value in expected_meta.items()
        ):
            raise ValueError(f"Constraint metadata changed: {name}")
        value = saved_duals[name]
        if name in relaxed:
            if value is not None:
                raise ValueError(
                    f"A relaxed constraint must have no retained multiplier: {name}"
                )
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
            if constraint.cmp.name != "EQ" and not np.allclose(
                dual, dual.T, atol=tol["psd_tol"], rtol=0
            ):
                raise ValueError(f"Nonsymmetric matrix dual: {name}")
            if (
                constraint.cmp.name != "EQ"
                and dual.size
                and np.linalg.eigvalsh((dual + dual.T) / 2).min() < -tol["psd_tol"]
            ):
                raise ValueError(f"Matrix dual is not PSD: {name}")
            contribution = sum(
                (float(dual[i, j]) * residual[j, i] for i, j in np.ndindex(dual.shape)),
                pf.Scalar.zero(),
            )
        weighted_terms[name] = contribution
        if origin == "interpolation" and kind == "scalar":
            interpolation_terms[name] = contribution
            try:
                interpolation_pairs[name] = name_to_vector_tuple(name)
            except (ValueError, IndexError):
                interpolation_pairs[name] = (
                    None  # Assign this term explicitly when grouping.
                )
        elif name != certificate["tau_name"]:
            extra_terms[name] = contribution
            extra_duals[name] = value

    tau_name = certificate["tau_name"]
    if (
        tau_name not in weighted_terms
        or saved_meta[tau_name]["origin"] != "initial"
        or saved_meta[tau_name]["kind"] != "scalar"
        or tau_name in relaxed
        or certificate["normalization"]["tau_name"] != tau_name
    ):
        raise ValueError("Missing or inconsistent bound normalization constraint")
    if not np.allclose(
        saved_duals[tau_name], certificate["tau_sol"], atol=tol["dual_tol"], rtol=0
    ):
        raise ValueError("The saved normalization dual is inconsistent")
    if not np.isfinite(certificate["opt_value"]) or not np.allclose(
        certificate["normalization"]["bound_value"],
        certificate["opt_value"],
        atol=tol["identity_atol"],
        rtol=tol["identity_rtol"],
    ):
        raise ValueError("The saved bound/normalization is inconsistent")
    certificate_diff = (
        pb.performance_metric
        - float(certificate["opt_value"])
        - sum(weighted_terms.values(), pf.Scalar.zero())
        + S_scalar
    )
    evaluated_diff = pm.eval_scalar(certificate_diff)
    for label, coords in (
        ("Gram", evaluated_diff.inner_prod_coords),
        ("function", evaluated_diff.func_coords),
        ("offset", np.asarray(evaluated_diff.offset)),
    ):
        if not np.allclose(
            np.asarray(coords, dtype=float),
            0,
            atol=tol["identity_atol"],
            rtol=tol["identity_rtol"],
        ):
            raise ValueError(f"Numerical certificate {label} identity failed")
    decomposition = certificate["numerical_decomposition"]
    D_saved = np.asarray(decomposition["D"], dtype=float)
    E_saved = np.asarray(decomposition["ell_coords"], dtype=float)
    if decomposition["basis_labels"] != basis_labels or E_saved.ndim != 2:
        raise ValueError("Numerical S decomposition basis differs")
    if E_saved.shape[1] != len(basis) or D_saved.shape != (
        E_saved.shape[0],
        E_saved.shape[0],
    ):
        raise ValueError("Numerical S decomposition shape differs")
    if not np.all(np.isfinite(D_saved)) or not np.all(np.isfinite(E_saved)):
        raise ValueError("Numerical S decomposition contains nonfinite values")
    if not np.allclose(
        E_saved.T @ D_saved @ E_saved,
        S_array,
        atol=tol["reconstruction_atol"],
        rtol=tol["reconstruction_rtol"],
    ):
        raise ValueError(
            "Numerical S decomposition does not reconstruct this certificate"
        )
    certificate_checked = True
    print("Numerical certificate checked for this N and parameter sample.")

    from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

    # B2 spectral terminal assignment failed rank constancy; reverse LDL is an alternative of the same S.
    D, ell = ldl_decompose_with_reversed_basis(S_sol, basis, print_output=False)
    E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
    assert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)
    S_piece_terms = {}
    a = 0
    while a < len(D):
        block = [a]
        if a + 1 < len(D) and (D[a, a + 1] != 0 or D[a + 1, a] != 0):
            block.append(a + 1)
        outside = [j for j in range(len(D)) if j not in block]
        assert not np.any(D[np.ix_(block, outside)] != 0)
        S_piece_terms[str(a)] = sum(
            (float(D[i, j]) * ell[i] * ell[j] for i in block for j in block),
            pf.Scalar.zero(),
        )
        a += len(block)

    # All interpolation residuals are <= 0; each subtracted S piece is PSD.
    # Thus these partial sums use the nonincreasing sign convention.
    rank_tolerance = 1e-4
    rank_left, rank_right = 1, 1
    group_terms = {
        name: term for name, term in weighted_terms.items() if name != tau_name
    }
    term_assignment = {name: int(name.split(",")[1][2:]) - 1 for name in group_terms}
    S_assignment = {}
    for name, piece in S_piece_terms.items():
        M = np.asarray(pm.eval_scalar(piece).inner_prod_coords, float)
        row = E[int(name)]
        support = [j for j, v in enumerate(row) if abs(v) > 1e-5]
        pivot_label = basis_labels[max(support)]
        index = (
            int(pivot_label.split("x_")[1].split(")")[0])
            if "x_" in pivot_label and "star" not in pivot_label
            else 0
        )
        S_assignment[name] = min(N_int - 1, max(-1, index - 1))
        assert np.linalg.eigvalsh((M + M.T) / 2).min() >= -1e-6
    assert set(term_assignment) == set(group_terms)
    assert set(S_assignment) == set(S_piece_terms)
    lyap = [pf.Scalar.zero()]
    partial_sum = sum(
        (term for name, term in group_terms.items() if term_assignment[name] == -1),
        pf.Scalar.zero(),
    )
    partial_sum -= sum(
        (piece for name, piece in S_piece_terms.items() if S_assignment[name] == -1),
        pf.Scalar.zero(),
    )
    for step in range(N_int):
        partial_sum += sum(
            (
                term
                for name, term in group_terms.items()
                if term_assignment[name] == step
            ),
            pf.Scalar.zero(),
        )
        partial_sum -= sum(
            (
                piece
                for name, piece in S_piece_terms.items()
                if S_assignment[name] == step
            ),
            pf.Scalar.zero(),
        )
        lyap.append(partial_sum)
    ranks = []
    singular_values = []
    for k, Vk in enumerate(lyap):
        M = np.asarray(pm.eval_scalar(Vk).inner_prod_coords, float)
        singular_values.append(np.linalg.svd(M, compute_uv=False).tolist())
        ranks.append(int(np.linalg.matrix_rank(M, tol=rank_tolerance)))
        print(f"rank V_{k}: {ranks[-1]}")
        if k == 0:
            print()
    retained = ranks[rank_left : N_int + 1 - rank_right]
    print(
        "Interior rank is constant at this N:",
        len(retained) >= 3 and len(set(retained)) == 1,
        "boundary exclusions:",
        (rank_left, rank_right),
    )
    coverage_diff = lyap[N_int] - (
        sum(group_terms.values(), pf.Scalar.zero()) - S_scalar
    )
    piece_diff = sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar
    coverage_residuals = {}
    for label, expression in [("coverage", coverage_diff), ("S pieces", piece_diff)]:
        value = pm.eval_scalar(expression)
        coords = [value.inner_prod_coords, value.func_coords, np.asarray(value.offset)]
        coverage_residuals[label] = max(
            float(np.max(np.abs(np.asarray(c, float)), initial=0)) for c in coords
        )
        assert all(
            np.allclose(np.asarray(c, float), 0, atol=1e-5, rtol=0) for c in coords
        )
    for k in range(N_int):
        assigned = {-1, 0} if k == 0 else {k}
        increment = sum(
            (
                term
                for name, term in group_terms.items()
                if term_assignment[name] in assigned
            ),
            pf.Scalar.zero(),
        )
        increment -= sum(
            (
                piece
                for name, piece in S_piece_terms.items()
                if S_assignment[name] in assigned
            ),
            pf.Scalar.zero(),
        )
        value = pm.eval_scalar(lyap[k + 1] - lyap[k] - increment)
        assert all(
            np.allclose(np.asarray(c, float), 0, atol=1e-5, rtol=0)
            for c in [
                value.inner_prod_coords,
                value.func_coords,
                np.asarray(value.offset),
            ]
        )
    boundary_names = []
    boundary_S = []
    grouping_checked = True
    print("Full-coordinate coverage and step identities:", coverage_residuals)

    return locals()


certificates = [
    json.loads((NOTEBOOK_DIR / path).read_text())
    for path in ("state/pgm_b2.json", "supplementary/pgm_b2_N6.json")
]
samples = [reconstruct_and_group(cert) for cert in certificates]
assert len({sample["N_int"] for sample in samples}) == 2
for sample in samples:
    retained = sample["ranks"][1 : sample["N_int"]]
    assert len(retained) >= 3 and set(retained) == {4}
    assert sample["certificate_checked"] and sample["grouping_checked"]
    for k in range(1, sample["N_int"]):
        assert not any(1e-5 < v < 1e-3 for v in sample["singular_values"][k])
print(
    "Cross-horizon interior rank confirmed: 4 at N=4 and N=6; exclude V_0 and V_N; absolute tolerance 1e-4, no coordinate scaling."
)
selected_sample = samples[0]
