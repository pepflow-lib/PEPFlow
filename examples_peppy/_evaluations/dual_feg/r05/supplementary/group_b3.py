"""Rebuild and check certificate, then construct actual partial sums without solving."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supplementary"))
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
import sympy as sp  # noqa: E402 - imports follow runtime or notebook setup
from certificate_capture import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup

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


def recheck(certificate):
    payload = {k: certificate[k] for k in CERTIFICATE_KEYS}
    digest = hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()
    assert digest == certificate["certificate_id"]
    for p, h in certificate["certificate_provenance"]["source_hashes"].items():
        source = (ROOT / p).resolve()
        assert source.is_relative_to(ROOT)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == h
    assert (
        Path(pf.__file__).resolve()
        == ROOT / "supplementary/approved/pepflow/__init__.py"
    )
    assert certificate["certificate_provenance"]["pep_type"] == "primal"
    assert certificate["solver_status"] == "optimal"
    assert certificate["closed_form_search"]["completed"]
    N = certificate["N_verify"]
    params = {
        str(k): sp.Rational(v)
        for k, v in json.loads(certificate["params_json"]).items()
    }
    ctx, pb, obj = get_pep_setup(N, params)
    pb.set_relaxed_constraints(certificate["relaxed_constraints"])
    pm = pf.ExpressionManager(ctx, resolve_parameters={k: v for k, v in params.items()})
    assert (
        [str(v) for v in ctx.basis_vectors()]
        == certificate["basis_vectors"]
        == certificate["S_row_names"]
        == certificate["S_col_names"]
    )
    assert [str(v) for v in ctx.basis_scalars()] == certificate["basis_scalars"]
    groups = ctx.get_constraint_data(obj)
    assert not groups.psd_dict and not ctx.func_to_triplets
    records = [(c, "initial", None, None) for c in pb.init_conditions]
    records += [
        (c, "interpolation", str(obj), str(g))
        for g, cs in groups.sc_dict.items()
        for c in cs
    ]
    assert len(records) == len({c.name for c, *_ in records})
    assert (
        {c.name for c, *_ in records}
        == set(certificate["named_dual_values"])
        == set(certificate["constraint_metadata"])
    )
    terms = {}
    for c, origin, owner, group in records:
        meta = {
            "origin": origin,
            "owner": owner,
            "group": group,
            "kind": "scalar",
            "comparator": c.cmp.value,
            "shape": [],
            "relaxed": c.name in pb.relaxed_constraints,
        }
        assert meta == certificate["constraint_metadata"][c.name]
        val = certificate["named_dual_values"][c.name]
        residual = c.lhs - c.rhs
        if c.cmp.value in ("GE", "SEQ"):
            residual = -residual
        e = pm.eval_scalar(pf.Scalar.zero() + residual)
        coords = certificate["constraint_coordinates"][c.name]
        assert np.allclose(e.inner_prod_coords, coords["gram"], atol=1e-12, rtol=0)
        assert np.allclose(e.func_coords, coords["func"], atol=1e-12, rtol=0)
        assert abs(float(e.offset) - coords["offset"]) <= 1e-12
        if meta["relaxed"]:
            assert val is None
        else:
            assert (
                val is not None
                and np.isfinite(val)
                and (c.cmp.value == "EQ" or val >= -1e-6)
            )
            terms[c.name] = val * (pf.Scalar.zero() + residual)
    assert set(pb.relaxed_constraints).issubset(certificate["constraint_metadata"])
    assert (
        certificate["normalization"]["tau_name"]
        == certificate["tau_name"]
        == "initial_condition"
    )
    assert certificate["normalization"]["bound_value"] == certificate["opt_value"]
    assert (
        certificate["named_dual_values"]["initial_condition"] == certificate["tau_sol"]
    )
    S = np.asarray(certificate["S_matrix"])
    assert np.isfinite(S).all() and np.allclose(S, S.T, atol=1e-6, rtol=0)
    assert np.linalg.eigvalsh(S).min() >= -1e-6
    dec = certificate["numerical_decomposition"]
    E, D = np.asarray(dec["ell_coords"]), np.asarray(dec["D"])
    assert dec["basis_labels"] == certificate["basis_vectors"]
    assert np.allclose(E.T @ D @ E, S, atol=1e-4, rtol=1e-5)
    basis = ctx.basis_vectors()
    S_scalar = sum(
        (float(S[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S.shape)),
        pf.Scalar.zero(),
    )
    diff = pm.eval_scalar(
        pb.performance_metric
        - certificate["opt_value"]
        - sum(terms.values(), pf.Scalar.zero())
        + S_scalar
    )
    residuals = [
        float(np.max(np.abs(diff.inner_prod_coords))),
        float(np.max(np.abs(diff.func_coords), initial=0)),
        abs(float(diff.offset)),
    ]
    assert max(residuals) <= 1e-5
    return ctx, pb, obj, pm, terms, S_scalar, residuals


def group(certificate):
    ctx, pb, obj, pm, terms, S_scalar, residuals = recheck(certificate)
    N = certificate["N_verify"]
    term_assignment = {}
    group_terms = {n: v for n, v in terms.items() if n != "initial_condition"}
    for name in group_terms:
        if name == f"A monotone:x_{N},x_star":
            term_assignment[name] = "boundary"
        elif name.startswith("A monotone:"):
            term_assignment[name] = int(name.split(",y_")[1])
        elif name == f"A Lipschitz:x_{N - 1},x_{N}":
            term_assignment[name] = N - 1
        else:
            term_assignment[name] = int(name.split(",y_")[1])
    S_piece_terms = {"whole_S": S_scalar}
    S_assignment = {name: "boundary" for name in S_piece_terms}
    lyap = [pf.Scalar.zero()]
    partial_sum = pf.Scalar.zero()
    for k in range(N):
        partial_sum += sum(
            (v for n, v in group_terms.items() if term_assignment[n] == k),
            pf.Scalar.zero(),
        )
        lyap.append(partial_sum)
    evaluated = [pm.eval_scalar(v) for v in lyap]
    matrices = [np.asarray(v.inner_prod_coords, dtype=float) for v in evaluated]
    svs = [np.linalg.svd(M, compute_uv=False) for M in matrices]
    ranks = [int(np.count_nonzero(s > 1e-4)) for s in svs]
    boundary = (
        sum(
            (v for n, v in group_terms.items() if term_assignment[n] == "boundary"),
            pf.Scalar.zero(),
        )
        - S_scalar
    )
    coverage = pm.eval_scalar(
        lyap[N] + boundary - (sum(group_terms.values(), pf.Scalar.zero()) - S_scalar)
    )
    coverage_res = [
        float(np.max(np.abs(coverage.inner_prod_coords))),
        float(np.max(np.abs(coverage.func_coords), initial=0)),
        abs(float(coverage.offset)),
    ]
    assert max(coverage_res) <= 1e-5
    for k in range(N):
        inc = sum(
            (v for n, v in group_terms.items() if term_assignment[n] == k),
            pf.Scalar.zero(),
        )
        chk = pm.eval_scalar(lyap[k + 1] - lyap[k] - inc)
        assert np.max(np.abs(chk.inner_prod_coords)) <= 1e-5
        assert (
            np.max(np.abs(chk.func_coords), initial=0) <= 1e-5
            and abs(float(chk.offset)) <= 1e-5
        )
    assert sum(v == "boundary" for v in term_assignment.values()) <= 1
    report = {
        "N": N,
        "certificate_id": certificate["certificate_id"],
        "recipe_id": "forward_lip_mon_terminal_whole_S_boundary",
        "rank_profile": ranks,
        "singular_values": [s.tolist() for s in svs],
        "rank_convention": {
            "tolerance": 1e-4,
            "scaling": "unscaled Gram matrix",
            "coordinate_order": "setup basis, earlier iterates first",
        },
        "rank_credible": bool(all(not np.any((s >= 5e-5) & (s <= 2e-4)) for s in svs)),
        "certificate_checked": True,
        "grouping_checked": True,
        "identity_residuals": residuals,
        "coverage_residuals": coverage_res,
        "constraint_assignment": term_assignment,
        "S_assignment": S_assignment,
        "lyap_inner_prod_coords": [m.tolist() for m in matrices],
        "lyap_func_coords": [
            np.asarray(v.func_coords, dtype=float).tolist() for v in evaluated
        ],
        "lyap_offsets": [float(v.offset) for v in evaluated],
    }
    return report


if __name__ == "__main__":
    certificate = json.loads((ROOT / "state/dual_feg_b2.json").read_text())
    report = group(certificate)
    (ROOT / "supplementary/rank_N6.json").write_text(json.dumps(report, indent=2))
    print("Ranks", report["rank_profile"], "credible", report["rank_credible"])
    print("Singular values", report["singular_values"])
