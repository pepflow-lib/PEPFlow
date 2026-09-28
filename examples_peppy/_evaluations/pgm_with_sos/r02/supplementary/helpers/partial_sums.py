"""Revalidate a complete saved certificate and form signed Lyapunov partial sums."""

import hashlib
import json
from pathlib import Path

import numpy as np
import sympy as sp
from aligned_sos import aligned_squares
from candidates import sos_pieces
from certificate import inventory, residual_of, verify
from runtime import APPROVED, ROOT

import pepflow as pf

CERTIFICATE_KEYS = (
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


def replay(certificate):
    digest = hashlib.sha256(
        json.dumps(
            {key: certificate[key] for key in CERTIFICATE_KEYS},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    assert digest == certificate["certificate_id"]
    assert certificate["closed_form_search"]["completed"]
    assert certificate["certificate_provenance"]["pep_type"] == "primal"
    assert Path(pf.__file__).resolve().is_relative_to(APPROVED)
    for name, expected in certificate["certificate_provenance"][
        "source_hashes"
    ].items():
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    checks, ctx, pb, _ = verify(
        certificate, certificate["opt_value"], certificate["numerical_decomposition"]
    )
    assert checks["passed"]
    assert certificate["N"] == certificate["N_verify"]
    assert (
        certificate["S_row_names"]
        == certificate["basis_vectors"]
        == certificate["S_col_names"]
    )
    entries = inventory(ctx, pb)
    assert len(entries) == len({c.name for c, *_ in entries})
    assert set(certificate["named_dual_values"]) == set(
        certificate["constraint_metadata"]
    )
    for c, origin, owner, group in entries:
        expected = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=c.name in pb.relaxed_constraints,
        )
        assert certificate["constraint_metadata"][c.name] == expected
    assert (
        certificate["normalization"]["tau_name"]
        == certificate["tau_name"]
        == "initial_condition"
    )
    assert (
        abs(
            certificate["tau_sol"]
            - certificate["named_dual_values"]["initial_condition"]
        )
        <= 1e-6
    )
    assert (
        abs(certificate["normalization"]["bound_value"] - certificate["opt_value"])
        <= 1e-5
    )
    return ctx, pb, checks


def construct(certificate, variant="canonical"):
    ctx, pb, certificate_checks = replay(certificate)
    n = certificate["N"]
    pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
    group_terms = {}
    term_assignment = {}
    for constraint, origin, owner, group in inventory(ctx, pb):
        value = certificate["named_dual_values"][constraint.name]
        if origin == "initial" or value is None:
            continue
        group_terms[constraint.name] = float(value) * residual_of(constraint)
        left, right = constraint.name.split(":")[1].split(",")
        j = int(right[2:])
        if left == "x_star" and j == 0:
            term_assignment[constraint.name] = -1
        else:
            term_assignment[constraint.name] = j - 1
    S_piece_terms = {
        f"{family}_{i}": coefficient * vector**2
        for i, family, coefficient, vector in sos_pieces(ctx, n)
    }
    if variant == "polar-aligned":
        S_piece_terms, alignment = aligned_squares(certificate, ctx)
    elif variant == "blend-3/10":
        aligned_pieces, alignment = aligned_squares(certificate, ctx)
        S_piece_terms = {
            name: sp.Rational(7, 10) * piece + sp.Rational(3, 10) * aligned_pieces[name]
            for name, piece in S_piece_terms.items()
        }
    S_assignment = {name: int(name.split("_")[1]) - 1 for name in S_piece_terms}
    lyap = [pf.Scalar.zero()]
    partial_sum = sum(
        (term for name, term in group_terms.items() if term_assignment[name] == -1),
        pf.Scalar.zero(),
    )
    for k in range(n):
        partial_sum += sum(
            (term for name, term in group_terms.items() if term_assignment[name] == k),
            pf.Scalar.zero(),
        )
        partial_sum -= sum(
            (term for name, term in S_piece_terms.items() if S_assignment[name] == k),
            pf.Scalar.zero(),
        )
        lyap.append(partial_sum)
    evaluated = [pm.eval_scalar(v) for v in lyap]
    spectra = [
        np.linalg.svd(np.asarray(v.inner_prod_coords, dtype=float), compute_uv=False)
        for v in evaluated
    ]
    ranks = [int(np.sum(s > 1e-4)) for s in spectra]
    basis = ctx.basis_vectors()
    S = np.asarray(certificate["S_matrix"], dtype=float)
    S_scalar = sum(
        (float(S[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S.shape)),
        pf.Scalar.zero(),
    )
    checks = {}
    for label, expression in [
        (
            "coverage",
            lyap[n] - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar),
        ),
        ("pieces", sum(S_piece_terms.values(), pf.Scalar.zero()) - S_scalar),
    ]:
        value = pm.eval_scalar(expression)
        residual = max(
            float(np.max(np.abs(np.asarray(arr, dtype=float)), initial=0))
            for arr in (
                value.inner_prod_coords,
                value.func_coords,
                np.asarray(value.offset),
            )
        )
        checks[label] = residual
        assert residual <= 1e-5
    min_piece_eigen = 0.0
    for piece in S_piece_terms.values():
        value = pm.eval_scalar(piece)
        M = np.asarray(value.inner_prod_coords, dtype=float)
        min_piece_eigen = min(
            min_piece_eigen, float(np.linalg.eigvalsh((M + M.T) / 2).min())
        )
        assert (
            np.max(abs(value.func_coords), initial=0) <= 1e-5
            and abs(value.offset) <= 1e-5
        )
    assert min_piece_eigen >= -1e-6
    increment_errors = []
    for k in range(n):
        steps = (-1, 0) if k == 0 else (k,)
        inc = sum(
            (
                term
                for name, term in group_terms.items()
                if term_assignment[name] in steps
            ),
            pf.Scalar.zero(),
        )
        inc -= sum(
            (
                term
                for name, term in S_piece_terms.items()
                if S_assignment[name] in steps
            ),
            pf.Scalar.zero(),
        )
        value = pm.eval_scalar(lyap[k + 1] - lyap[k] - inc)
        error = max(
            float(np.max(np.abs(np.asarray(arr, dtype=float)), initial=0))
            for arr in (
                value.inner_prod_coords,
                value.func_coords,
                np.asarray(value.offset),
            )
        )
        increment_errors.append(error)
        assert error <= 1e-5
    checks.update(
        minimum_piece_eigenvalue=min_piece_eigen,
        maximum_increment_error=max(increment_errors),
        boundary_constraints=[],
        boundary_S=[],
        omitted_constraints=[],
    )
    observation = dict(
        N=n,
        certificate_id=certificate["certificate_id"],
        recipe_id=variant,
        rank_profile=ranks,
        rank_convention=dict(
            tolerance=1e-4,
            scaling="absolute, unscaled native Gram coordinates",
            coordinate_order="context basis creation order",
        ),
        singular_values=[s.tolist() for s in spectra],
        rank_credible=all(not np.any((s >= 5e-5) & (s <= 2e-4)) for s in spectra),
        certificate_checked=True,
        grouping_checked=True,
        checks=checks,
    )
    return dict(
        ctx=ctx,
        pb=pb,
        pm=pm,
        lyap=lyap,
        observation=observation,
        term_assignment=term_assignment,
        S_assignment=S_assignment,
        group_terms=group_terms,
        S_piece_terms=S_piece_terms,
        certificate_checks=certificate_checks,
    )
