"""Replay the complete saved scalar certificate without solving."""

import numpy as np
import sympy as sp
from feg_setup import get_pep_setup

import pepflow as pf
from pepflow.utils import Comparator


def verify_saved(data, dense_value):
    n = data["N_verify"]
    ctx, pb, obj = get_pep_setup(n, {"L": 1, "R": 1})
    ctx.set_as_current()
    pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S(1), "R": sp.S(1)})
    entries = [*pb.init_conditions, *obj.get_interpolation_constraints(ctx)]
    assert (
        set(c.name for c in entries)
        == set(data["named_dual_values"])
        == set(data["constraint_metadata"])
    )
    assert [str(v) for v in ctx.basis_vectors()] == data["basis_vectors"]
    assert [str(v) for v in ctx.basis_scalars()] == data["basis_scalars"]
    weighted = pf.Scalar.zero()
    active = []
    for c in entries:
        value = data["named_dual_values"][c.name]
        meta = data["constraint_metadata"][c.name]
        assert meta["comparator"] == c.cmp.value and meta["kind"] == "scalar"
        if meta["relaxed"]:
            assert value is None and c.name in data["relaxed_constraints"]
            continue
        assert value is not None and np.isfinite(value)
        residual = c.lhs - c.rhs
        if c.cmp in (Comparator.GE, Comparator.SEQ):
            residual = -residual
        weighted += value * residual
        if c.cmp != Comparator.EQ:
            active.append(value)
    basis = ctx.basis_vectors()
    S = np.asarray(data["S_matrix"], dtype=float)
    S_numeric = sum(
        (float(S[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(S.shape)),
        pf.Scalar.zero(),
    )
    diff = pb.performance_metric - data["opt_value"] - weighted + S_numeric
    checked = pm.eval_scalar(diff)
    D = np.asarray(data["numerical_decomposition"]["D"])
    E = np.asarray(data["numerical_decomposition"]["ell_coords"])

    def max_abs(a):
        return float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0.0))

    residuals = dict(
        identity_gram_max_abs=max_abs(checked.inner_prod_coords),
        identity_func_max_abs=max_abs(checked.func_coords),
        identity_offset_abs=max_abs(checked.offset),
        S_reconstruction_max_abs=max_abs(E.T @ D @ E - S),
        dense_relaxed_gap=abs(data["opt_value"] - dense_value),
        minimum_scalar_inequality_dual=min(active, default=0.0),
        minimum_S_eigenvalue=float(np.linalg.eigvalsh(S).min()),
        minimum_matrix_inequality_eigenvalue=0.0,
    )
    tolerances = dict(
        identity_atol=1e-5,
        identity_rtol=0,
        reconstruction_atol=1e-4,
        reconstruction_rtol=1e-5,
        dual_tol=1e-6,
        psd_tol=1e-6,
        dense_opt_atol=1e-5,
    )
    passed = (
        data["certificate_provenance"]["solver_status"] == "optimal"
        and all(
            residuals[k] <= 1e-5
            for k in [
                "identity_gram_max_abs",
                "identity_func_max_abs",
                "identity_offset_abs",
            ]
        )
        and np.allclose(S, S.T, atol=1e-6, rtol=0)
        and np.allclose(E.T @ D @ E, S, atol=1e-4, rtol=1e-5)
        and residuals["dense_relaxed_gap"] < 1e-5
        and residuals["minimum_scalar_inequality_dual"] >= -1e-6
        and residuals["minimum_S_eigenvalue"] >= -1e-6
    )
    assert passed, residuals
    return (
        ctx,
        pb,
        obj,
        pm,
        checked,
        dict(tolerances=tolerances, residuals=residuals, passed=bool(passed)),
    )
