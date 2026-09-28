"""Replay saved certificates and group all three supplied square families."""

import hashlib
import json

import numpy as np
import sympy as sp
from certificates import aid_terms, inventory, maxabs, residual, verify
from pgm_setup import get_pep_setup
from runtime import NOTEBOOK_DIR, REPO_ROOT

import pepflow as pf


def replay(certificate):
    keys = (
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
    digest = hashlib.sha256(
        json.dumps(
            {k: certificate[k] for k in keys},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    assert digest == certificate["certificate_id"]
    assert certificate["closed_form_search"]["completed"]
    assert certificate["certificate_provenance"]["pep_type"] == "primal"
    for p, h in certificate["certificate_provenance"]["source_hashes"].items():
        assert hashlib.sha256((NOTEBOOK_DIR / p).read_bytes()).hexdigest() == h
    assert (
        __import__("pathlib").Path(pf.__file__).resolve()
        == REPO_ROOT / "pepflow/__init__.py"
    )
    params = {k: sp.S(v) for k, v in json.loads(certificate["params_json"]).items()}
    assert params == {"L": sp.S.One, "R": sp.S.One}
    n = certificate["N_verify"]
    ctx, pb, _ = get_pep_setup(n, params)
    pb.set_relaxed_constraints(certificate["relaxed_constraints"])
    basis = ctx.basis_vectors()
    labels = [str(v) for v in basis]
    assert (
        labels
        == certificate["basis_vectors"]
        == certificate["S_row_names"]
        == certificate["S_col_names"]
    )
    assert [str(v) for v in ctx.basis_scalars()] == certificate["basis_scalars"]
    records = inventory(ctx, pb)
    assert {c.name for c, *_ in records} == set(certificate["constraint_metadata"])
    for c, origin, owner, group in records:
        meta = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=c.name in pb.relaxed_constraints,
        )
        assert meta == certificate["constraint_metadata"][c.name]
        if meta["relaxed"]:
            assert certificate["named_dual_values"][c.name] is None
    assert (
        certificate["tau_sol"] == certificate["named_dual_values"]["initial_condition"]
    )
    assert certificate["normalization"]["bound_value"] == certificate["opt_value"]
    assert abs(certificate["opt_value"] - 1 / (4 * n)) < 1e-5
    checks, _ = verify(ctx, pb, certificate, certificate["opt_value"])
    d = certificate["numerical_decomposition"]
    assert d["basis_labels"] == labels
    D, E = np.array(d["D"]), np.array(d["ell_coords"])
    assert np.allclose(E.T @ D @ E, certificate["S_matrix"], atol=1e-4, rtol=1e-5)
    return ctx, pb, checks


def construct(certificate, verbose=True):
    ctx, pb, checks = replay(certificate)
    n = certificate["N_verify"]
    pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
    group_terms = {}
    term_assignment = {}
    for c, origin, _, _ in inventory(ctx, pb):
        v = certificate["named_dual_values"][c.name]
        if origin == "initial" or v is None:
            continue
        group_terms[c.name] = v * residual(c)
        _, pair = c.name.split(":")
        a, b = pair.split(",")
        j = int(b[2:])
        assert a == "x_star" or int(a[2:]) + 1 == j
        term_assignment[c.name] = j - 1
    pieces = {f"S{i}_{family}": c * u**2 for i, family, c, u in aid_terms(ctx, n)}
    S_assignment = {name: int(name.split("_")[0][1:]) - 1 for name in pieces}
    total_S = sum(pieces.values(), pf.Scalar.zero())
    basis = ctx.basis_vectors()
    mat = np.array(certificate["S_matrix"])
    S_scalar = sum(
        (float(mat[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(mat.shape)),
        pf.Scalar.zero(),
    )
    piece_diff = pm.eval_scalar(total_S - S_scalar)
    piece_residual = max(
        maxabs(piece_diff.inner_prod_coords),
        maxabs(piece_diff.func_coords),
        maxabs(piece_diff.offset),
    )
    assert piece_residual <= 1e-5
    for piece in pieces.values():
        q = pm.eval_scalar(piece)
        assert maxabs(q.func_coords) == 0 and maxabs(q.offset) == 0
        assert (
            np.linalg.eigvalsh(np.array(q.inner_prod_coords, dtype=float)).min()
            >= -1e-6
        )
    lyap = [pf.Scalar.zero()]
    partial_sum = sum(
        (t for name, t in group_terms.items() if term_assignment[name] == -1),
        pf.Scalar.zero(),
    )
    for k in range(n):
        increment = sum(
            (t for name, t in group_terms.items() if term_assignment[name] == k),
            pf.Scalar.zero(),
        )
        increment -= sum(
            (t for name, t in pieces.items() if S_assignment[name] == k),
            pf.Scalar.zero(),
        )
        partial_sum += increment
        lyap.append(partial_sum)
    ranks = []
    singular_values = []
    coords = []
    for k, V in enumerate(lyap):
        q = pm.eval_scalar(V)
        matrix = np.array(q.inner_prod_coords, dtype=float)
        sv = np.linalg.svd(matrix, compute_uv=False)
        rank = int(np.sum(sv > 1e-4))
        ranks.append(rank)
        singular_values.append(sv.tolist())
        coords.append(
            dict(
                gram=matrix.tolist(),
                func=np.array(q.func_coords, dtype=float).tolist(),
                offset=float(q.offset),
            )
        )
        if verbose:
            print(f"rank V_{k}: {rank}")
            if k == 0:
                print()
    if verbose:
        print(
            "Interior rank is constant at this N:",
            len(set(ranks[1:-1])) == 1 and n - 1 >= 3,
            "boundary exclusions:",
            (1, 1),
        )
    coverage = pm.eval_scalar(
        lyap[-1] - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
    )
    coverage_residual = max(
        maxabs(coverage.inner_prod_coords),
        maxabs(coverage.func_coords),
        maxabs(coverage.offset),
    )
    assert coverage_residual <= 1e-5
    step_residuals = []
    for k in range(n):
        included = {-1, 0} if k == 0 else {k}
        inc = sum(
            (t for name, t in group_terms.items() if term_assignment[name] in included),
            pf.Scalar.zero(),
        )
        inc -= sum(
            (t for name, t in pieces.items() if S_assignment[name] in included),
            pf.Scalar.zero(),
        )
        q = pm.eval_scalar(lyap[k + 1] - lyap[k] - inc)
        step_residuals.append(
            max(maxabs(q.inner_prod_coords), maxabs(q.func_coords), maxabs(q.offset))
        )
    assert max(step_residuals) <= 1e-5
    sample = dict(
        N=n,
        certificate_id=certificate["certificate_id"],
        recipe_id="forward-star-all-three-SOS",
        rank_profile=ranks,
        singular_values=singular_values,
        rank_convention={
            "tolerance": 1e-4,
            "scaling": "none; absolute singular values",
            "coordinates": "Original PEP basis in setup order",
        },
        rank_credible=all(
            not any(0.5e-4 < v < 2e-4 for v in sv) for sv in singular_values
        ),
        certificate_checked=True,
        grouping_checked=True,
        certificate_checks=checks,
        coverage_residual=coverage_residual,
        piece_residual=piece_residual,
        step_residuals=step_residuals,
        constraint_assignment=term_assignment,
        S_assignment=S_assignment,
        boundary_constraints=[],
        boundary_S=[],
        omitted_constraints=[],
        coordinates=coords,
        monotonicity="Each increment is a sum of nonnegative multipliers times residuals <=0 minus positive SOS pieces. V_0=0; initial interpolation joins step zero.",
    )
    return ctx, pb, lyap, sample
