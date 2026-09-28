"""Reconstruct and group the current certificate, without solving."""

import hashlib
import json

import numpy as np
from certificates import certificate_digest, revalidate

import pepflow as pf


def check_certificate(certificate, notebook_dir):
    assert certificate_digest(certificate) == certificate["certificate_id"]
    assert certificate["closed_form_search"]["completed"]
    assert certificate["certificate_provenance"]["pep_type"] == "primal"
    for path, expected in certificate["certificate_provenance"][
        "source_hashes"
    ].items():
        source = (notebook_dir / path).resolve()
        assert source.is_relative_to(notebook_dir)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
    assert json.loads(certificate["params_json"]) == {"L": 1, "R": 1}
    assert certificate["N"] == certificate["N_verify"]
    ctx, pb, obj, pm, checked, residuals = revalidate(certificate)
    pb.set_relaxed_constraints(certificate["relaxed_constraints"])
    basis = ctx.basis_vectors()
    labels = [str(v) for v in basis]
    assert labels == certificate["S_row_names"] == certificate["S_col_names"]
    S = np.asarray(certificate["S_matrix"], dtype=float)
    assert S.shape == (len(basis), len(basis)) and np.all(np.isfinite(S))
    assert np.allclose(S, S.T, atol=1e-6, rtol=0)
    decomposition = certificate["numerical_decomposition"]
    D, E = np.asarray(decomposition["D"]), np.asarray(decomposition["ell_coords"])
    assert decomposition["basis_labels"] == labels
    assert np.all(np.isfinite(D)) and np.all(np.isfinite(E))
    assert np.allclose(E.T @ D @ E, S, atol=1e-4, rtol=1e-5)
    constraints = [*pb.init_conditions, *obj.get_interpolation_constraints(ctx)]
    groups = ctx.get_constraint_data(obj)
    group_names = {
        c.name: str(group) for group, family in groups.sc_dict.items() for c in family
    }
    assert (
        not groups.psd_dict
        and not ctx.oper_to_duplets
        and len(ctx.func_to_triplets) == 1
    )
    weighted_terms = {}
    for constraint in constraints:
        initial = constraint.name == certificate["tau_name"]
        expected = dict(
            origin="initial" if initial else "interpolation",
            owner=None if initial else str(obj),
            group=group_names.get(constraint.name),
            kind="scalar",
            comparator=constraint.cmp.value,
            shape=[],
            relaxed=constraint.name in certificate["relaxed_constraints"],
        )
        assert expected == certificate["constraint_metadata"][constraint.name]
        value = certificate["named_dual_values"][constraint.name]
        if expected["relaxed"]:
            assert value is None
            continue
        assert value is not None and value >= -1e-6
        residual = constraint.lhs - constraint.rhs
        if constraint.cmp == pf.Comparator.GE:
            residual = -residual
        weighted_terms[constraint.name] = value * residual
    assert (
        certificate["tau_sol"]
        == certificate["named_dual_values"][certificate["tau_name"]]
    )
    assert certificate["normalization"]["bound_value"] == certificate["opt_value"]
    return ctx, pb, obj, pm, weighted_terms, residuals


def build_partial_sums(certificate, notebook_dir):
    ctx, pb, obj, pm, weighted_terms, residuals = check_certificate(
        certificate, notebook_dir
    )
    n = certificate["N"]
    basis = ctx.basis_vectors()
    matrix = np.asarray(certificate["S_matrix"])
    S_scalar = sum(
        (
            float(matrix[i, j]) * basis[i] * basis[j]
            for i, j in np.ndindex(matrix.shape)
        ),
        pf.Scalar.zero(),
    )
    # Keep the complete numerical PSD block as the single terminal S piece.
    S_piece_terms = {"terminal_S": S_scalar}
    S_assignment = {"terminal_S": "boundary"}
    group_terms = {
        name: term
        for name, term in weighted_terms.items()
        if name != certificate["tau_name"]
    }
    term_assignment = {}
    for k in range(n):
        tag = "z_0" if k == 0 else f"x_{k}"
        term_assignment[f"f:x_star,{tag}"] = k
        term_assignment[f"f:{tag},x_{k + 1}"] = k
    term_assignment[f"f:x_star,x_{n}"] = "boundary"
    assert set(term_assignment) == set(group_terms)
    lyap = [pf.Scalar.zero()]
    partial_sum = pf.Scalar.zero()
    for k in range(n):
        increment = sum(
            (group_terms[name] for name, step in term_assignment.items() if step == k),
            pf.Scalar.zero(),
        )
        partial_sum += increment
        lyap.append(partial_sum)
    ranks, singular_values, evaluated = [], [], []
    for k, Vk in enumerate(lyap):
        value = pm.eval_scalar(Vk)
        evaluated.append(value)
        singular = np.linalg.svd(
            np.asarray(value.inner_prod_coords, dtype=float), compute_uv=False
        )
        singular_values.append(singular.tolist())
        rank = int(np.count_nonzero(singular > 1e-4))
        ranks.append(rank)
        print(f"rank V_{k}: {rank}")
        if k == 0:
            print()
    print(
        "Interior rank is constant at this N:",
        len(set(ranks[2 : n + 1])) == 1 and n - 1 >= 3,
        "boundary exclusions:",
        (2, 0),
    )
    leftover = group_terms[f"f:x_star,x_{n}"] - S_scalar
    coverage = (
        lyap[n] + leftover - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
    )
    expressions = [coverage, sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar]
    for k in range(n):
        increment = sum(
            (group_terms[name] for name, step in term_assignment.items() if step == k),
            pf.Scalar.zero(),
        )
        expressions.append(lyap[k + 1] - lyap[k] - increment)
    coverage_max = 0.0
    for expression in expressions:
        value = pm.eval_scalar(expression)
        for coords in (
            value.inner_prod_coords,
            value.func_coords,
            np.asarray(value.offset),
        ):
            error = float(np.max(np.abs(np.asarray(coords, dtype=float)), initial=0))
            coverage_max = max(coverage_max, error)
            assert error <= 1e-5
    assert np.linalg.eigvalsh(matrix).min() >= -1e-6
    rank_credible = all(
        not any(1e-5 < s < 1e-3 for s in singular) for singular in singular_values
    )
    observation = dict(
        N=n,
        certificate_id=certificate["certificate_id"],
        recipe_id="star-and-forward-pair-whole-S-boundary",
        rank_profile=ranks,
        singular_values=singular_values,
        rank_convention=dict(
            tolerance=1e-4,
            scaling="absolute, no rescaling",
            coordinate_order="setup basis creation order",
        ),
        rank_credible=rank_credible,
        certificate_checked=True,
        grouping_checked=True,
        coverage_max_abs=coverage_max,
    )
    coordinates = dict(
        lyap_inner_prod_coords=[
            np.asarray(v.inner_prod_coords, dtype=float).tolist() for v in evaluated
        ],
        lyap_func_coords=[
            np.asarray(v.func_coords, dtype=float).tolist() for v in evaluated
        ],
        lyap_offsets=[float(v.offset) for v in evaluated],
    )
    coverage_record = dict(
        constraint_assignment=term_assignment,
        S_assignment=S_assignment,
        normalization_constraint=certificate["tau_name"],
        boundary_constraints=[f"f:x_star,x_{n}"],
        boundary_S=["terminal_S"],
        omitted_constraints=[],
        checked=True,
    )
    return observation, coordinates, coverage_record
