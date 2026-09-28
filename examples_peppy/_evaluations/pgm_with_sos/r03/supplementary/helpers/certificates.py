"""Coherent certificate capture and independent coordinate checks."""

import hashlib
import json
import uuid

import numpy as np
import sympy as sp
from pgm_setup import L, f, get_pep_setup
from runtime import NOTEBOOK_DIR, solve_explicit

import pepflow as pf
from pepflow.constraint import ScalarConstraint
from pepflow.utils import Comparator


def inventory(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        owner.get_interpolation_constraints(ctx)
        groups = ctx.get_constraint_data(owner)
        entries.extend(
            (c, "interpolation", str(owner), str(group))
            for group, constraints in groups.sc_dict.items()
            for c in constraints
        )
        assert not groups.psd_dict
    assert len({c.name for c, *_ in entries}) == len(entries)
    return entries


def residual(c):
    q = c.lhs - c.rhs
    return -q if c.cmp in (Comparator.GE, Comparator.SEQ) else q


def maxabs(a):
    return float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0))


def capture(n, dropped=()):
    source_hashes = fingerprint()
    params = {"L": sp.S.One, "R": sp.S.One}
    ctx, pb, obj = get_pep_setup(n, params)
    pb.set_relaxed_constraints(list(dropped))
    result, log = solve_explicit(ctx, pb, params)
    entries = inventory(ctx, pb)
    meta, vals = {}, {}
    for c, origin, owner, group in entries:
        assert isinstance(c, ScalarConstraint)
        v = result.get_dual_value(c.name)
        drop = c.name in dropped
        assert v is not None or drop
        meta[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=drop,
        )
        vals[c.name] = None if drop else float(v)
    sm = result.get_gram_dual_matrix()
    lm = result.get_scalar_constraint_dual_value_in_numpy(obj)

    def display(m):
        return dict(
            matrix=np.asarray(m.matrix).tolist(),
            row_names=list(m.row_names),
            col_names=list(m.col_names),
        )

    if isinstance(lm, dict):
        displays = {"lambda_groups": {k: display(v) for k, v in lm.items()}}
    else:
        displays = dict(
            lambda_matrix=lm.matrix.tolist(),
            lambda_row_names=list(lm.row_names),
            lambda_col_names=list(lm.col_names),
        )
    data = dict(
        N=n,
        N_verify=n,
        opt_value=float(result.opt_value),
        tau_sol=float(result.get_dual_value("initial_condition")),
        tau_name="initial_condition",
        relaxed_constraints=list(dropped),
        S_matrix=np.asarray(sm.matrix, dtype=float).tolist(),
        S_row_names=list(sm.row_names),
        S_col_names=list(sm.col_names),
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        named_dual_values=vals,
        constraint_metadata=meta,
        certificate_provenance={
            "solve_id": str(uuid.uuid4()),
            "pep_type": "primal",
            "solver_status": str(result.solver_status),
            "solver": log,
            "source_hashes": source_hashes,
        },
        **displays,
    )
    assert fingerprint() == source_hashes
    return ctx, pb, result, data


def aid_terms(ctx, n):
    """Exact supplied aid, with original normalization."""
    n = sp.S(n)
    astar = f.grad(ctx["x_star"])
    terms = []
    for ii in range(1, int(n) + 1):
        i = sp.S(ii)
        xp, x = ctx[f"x_{ii - 1}"], ctx[f"x_{ii}"]
        ap, a = f.grad(xp), f.grad(x)
        si = L * (xp - x) - ap
        c1 = n / ((2 * n + 1 - i) * (2 * n - i) * L)
        u1 = i / (2 * n) * a + (2 * n - i) / (2 * n) * ap - astar
        c2 = (
            (i - 1) / (2 * n - i) * (2 * n + 2) / (2 * n + 1)
            + 2 * n / ((2 * n - i) ** 2 * (2 * n + 1))
        ) / (2 * L)
        u2 = ap + si - L / (2 * n + 1 - i) * (xp - ctx["x_star"])
        c3 = i / (2 * n + 1 - i) * 2 * n / (2 * n + 1) / (2 * L)
        u3 = (
            (2 * n + 1) / (2 * n) * (a + si)
            - (ap + si) / (2 * n)
            - L / (2 * n - i) * (x - ctx["x_star"])
        )
        terms.extend([(ii, 1, c1, u1), (ii, 2, c2, u2), (ii, 3, c3, u3)])
    return terms


def verify(ctx, pb, data, dense_value):
    pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
    matrix = np.asarray(data["S_matrix"])
    basis = ctx.basis_vectors()
    snum = sum(
        (
            float(matrix[i, j]) * basis[i] * basis[j]
            for i, j in np.ndindex(matrix.shape)
        ),
        pf.Scalar.zero(),
    )
    weighted = pf.Scalar.zero()
    entries = inventory(ctx, pb)
    assert set(data["named_dual_values"]) == {c.name for c, *_ in entries}
    for c, *_ in entries:
        v = data["named_dual_values"][c.name]
        if v is not None:
            weighted += v * residual(c)
    diff = pm.eval_scalar(pb.performance_metric - data["opt_value"] - weighted + snum)
    checks = dict(
        identity_gram_max_abs=maxabs(diff.inner_prod_coords),
        identity_func_max_abs=maxabs(diff.func_coords),
        identity_offset_abs=maxabs(diff.offset),
        dense_relaxed_gap=abs(data["opt_value"] - dense_value),
        minimum_scalar_inequality_dual=min(
            v for v in data["named_dual_values"].values() if v is not None
        ),
        minimum_S_eigenvalue=float(np.linalg.eigvalsh(matrix).min()),
        minimum_matrix_inequality_eigenvalue=0.0,
    )
    assert (
        max(
            checks[k]
            for k in (
                "identity_gram_max_abs",
                "identity_func_max_abs",
                "identity_offset_abs",
                "dense_relaxed_gap",
            )
        )
        <= 1e-5
    ), checks
    assert checks["minimum_scalar_inequality_dual"] >= -1e-6
    assert checks["minimum_S_eigenvalue"] >= -1e-6
    assert data["certificate_provenance"]["solver_status"] == "optimal"
    assert np.allclose(matrix, matrix.T, atol=1e-6, rtol=0)
    return checks, diff


def save(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False), encoding="utf-8")


def fingerprint():
    allow = json.loads(
        (NOTEBOOK_DIR / "supplementary/approved/allowlist.json").read_text()
    )
    paths = [
        NOTEBOOK_DIR / "pgm_setup.py",
        NOTEBOOK_DIR / "supplementary/helpers/runtime.py",
        NOTEBOOK_DIR / "supplementary/helpers/certificates.py",
    ]
    paths += [
        __import__("pathlib").Path(p)
        for p in allow["exact_read_files"]
        if "/pepflow/" in p.replace("\\", "/")
    ]
    return {
        str(p.relative_to(NOTEBOOK_DIR)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths
    }


def lambda_candidate(name, n):
    n = sp.S(n)
    if name == "initial_condition":
        return sp.S.One / (4 * n)
    owner, pair = name.split(":")
    a, b = pair.split(",")
    if a == "x_star":
        j = int(b[2:])
        if owner == "g":
            return 2 * n / ((2 * n - j) * (2 * n + 1 - j))
        if j == 0:
            return sp.S.One / (2 * n)
        if j == n:
            return sp.S.One / (n + 1)
        return (2 * n + 1) / ((2 * n - j) * (2 * n + 1 - j))
    if b != "x_star" and int(b[2:]) == int(a[2:]) + 1:
        i = int(a[2:])
        return (i + 1) / (2 * n - i) if owner == "f" else i / (2 * n - i)
    return sp.S.Zero
