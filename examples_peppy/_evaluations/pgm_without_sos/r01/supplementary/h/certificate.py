"""Capture and independently recheck complete PGM primal dual certificates."""
import hashlib
import json
import uuid

import numpy as np
import pepflow as pf
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

from runtime import solve_setup


def inventory(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        entries.extend((c, "interpolation", str(owner), str(group))
                       for group, constraints in groups.sc_dict.items() for c in constraints)
        entries.extend((c, "interpolation", str(owner), str(group))
                       for group, c in groups.psd_dict.items())
    assert len({c.name for c, *_ in entries}) == len(entries)
    return entries


def capture(ctx, pb, obj, params, dense_value=None):
    result, solver_record = solve_setup(ctx, pb, params)
    ctx.set_as_current()
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    S = result.get_gram_dual_matrix()
    metadata, duals = {}, {}
    for c, origin, owner, group in inventory(ctx, pb):
        assert isinstance(c, pf.ScalarConstraint), "Unexpected matrix constraint"
        dropped = c.name in pb.relaxed_constraints
        value = result.get_dual_value(c.name)
        assert dropped or value is not None, c.name
        metadata[c.name] = dict(origin=origin, owner=owner, group=group,
                               kind="scalar", comparator=c.cmp.value,
                               shape=[], relaxed=dropped)
        duals[c.name] = None if dropped else float(value)
    D, ell = ldl_decompose_with_reversed_basis(
        S, ctx.basis_vectors(), print_output=False)
    E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
    state = dict(
        opt_value=float(result.opt_value), tau_sol=float(duals["initial_condition"]),
        tau_name="initial_condition", relaxed_constraints=list(pb.relaxed_constraints),
        S_matrix=np.asarray(S.matrix, dtype=float).tolist(),
        S_row_names=list(S.row_names), S_col_names=list(S.col_names),
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        named_dual_values=duals, constraint_metadata=metadata,
        certificate_provenance=dict(solve_id=str(uuid.uuid4()), pep_type="primal",
                                    solver_status=str(result.solver_status),
                                    solver=solver_record),
        numerical_decomposition=dict(method="reverse_ldl",
            D=np.asarray(D, dtype=float).tolist(), ell_coords=E.tolist(),
            basis_labels=[str(v) for v in ctx.basis_vectors()]))
    displays = {}
    for owner in (obj, *[o for o in ctx.func_to_triplets if o is not obj]):
        value = result.get_scalar_constraint_dual_value_in_numpy(owner)
        groups = value if isinstance(value, dict) else {"default": value}
        for group, matrix in groups.items():
            displays[f"{owner}:{group}"] = dict(
                matrix=np.asarray(matrix.matrix, dtype=float).tolist(),
                row_names=list(matrix.row_names), col_names=list(matrix.col_names))
    state["all_lambda_groups"] = displays
    state["lambda_groups"] = {key: value for key, value in displays.items()
                              if key.startswith(str(obj) + ":")}
    state["dense_opt_value"] = state["opt_value"] if dense_value is None else dense_value
    state["numerical_checks"], _, _ = verify(ctx, pb, params, state)
    return state


def verify(ctx, pb, params, state):
    ctx.set_as_current()
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    basis = ctx.basis_vectors()
    assert [str(v) for v in basis] == state["basis_vectors"]
    assert [str(v) for v in ctx.basis_scalars()] == state["basis_scalars"]
    entries = inventory(ctx, pb)
    assert {c.name for c, *_ in entries} == set(state["named_dual_values"])
    assert set(state["constraint_metadata"]) == set(state["named_dual_values"])
    weighted = pf.Scalar.zero()
    nonnegative = []
    for c, origin, owner, group in entries:
        meta = state["constraint_metadata"][c.name]
        assert meta == dict(origin=origin, owner=owner, group=group,
                            kind="scalar", comparator=c.cmp.value, shape=[],
                            relaxed=c.name in pb.relaxed_constraints)
        value = state["named_dual_values"][c.name]
        if meta["relaxed"]:
            assert value is None
            continue
        assert value is not None and np.isfinite(value)
        residual = c.lhs - c.rhs
        if c.cmp == pf.Comparator.GE:
            residual = -residual
        weighted += value * residual
        if c.cmp != pf.Comparator.EQ:
            nonnegative.append(value)
    D = np.asarray(state["numerical_decomposition"]["D"])
    E = np.asarray(state["numerical_decomposition"]["ell_coords"])
    ell = [sum((float(a) * v for a, v in zip(row, basis)), pf.Vector.zero())
           for row in E]
    S_numeric = sum((float(D[i, j]) * ell[i] * ell[j]
                     for i, j in np.ndindex(D.shape)), pf.Scalar.zero())
    checked = pm.eval_scalar(pb.performance_metric - state["opt_value"] - weighted + S_numeric)
    S = np.asarray(state["S_matrix"])
    def maxabs(value):
        return float(np.max(np.abs(np.asarray(value, dtype=float)), initial=0))
    residuals = dict(
        identity_gram_max_abs=maxabs(checked.inner_prod_coords),
        identity_func_max_abs=maxabs(checked.func_coords),
        identity_offset_abs=maxabs(checked.offset),
        S_reconstruction_max_abs=maxabs(E.T @ D @ E - S),
        dense_relaxed_gap=abs(state["dense_opt_value"] - state["opt_value"]),
        minimum_scalar_inequality_dual=min(nonnegative, default=0),
        minimum_S_eigenvalue=float(np.linalg.eigvalsh((S+S.T)/2).min()),
        minimum_matrix_inequality_eigenvalue=0.0)
    tolerances = dict(identity_atol=1e-5, identity_rtol=0,
                      reconstruction_atol=1e-4, reconstruction_rtol=1e-5,
                      dual_tol=1e-6, psd_tol=1e-6, dense_opt_atol=1e-5)
    passed = (
        state["certificate_provenance"]["solver_status"] == "optimal"
        and np.all(np.isfinite(S)) and np.allclose(S, S.T, atol=1e-6, rtol=0)
        and all(residuals[key] <= 1e-5 for key in (
            "identity_gram_max_abs", "identity_func_max_abs", "identity_offset_abs"))
        and np.allclose(E.T @ D @ E, S, atol=1e-4, rtol=1e-5)
        and residuals["dense_relaxed_gap"] < 1e-5
        and residuals["minimum_scalar_inequality_dual"] >= -1e-6
        and residuals["minimum_S_eigenvalue"] >= -1e-6)
    return dict(tolerances=tolerances, residuals=residuals, passed=bool(passed)), checked, S_numeric


def certificate_id(state):
    keys = ("N_verify", "params_json", "relaxed_constraints", "S_matrix", "S_row_names",
            "S_col_names", "basis_vectors", "basis_scalars", "opt_value", "tau_sol",
            "tau_name", "named_dual_values", "constraint_metadata", "normalization",
            "certificate_provenance", "numerical_checks", "numerical_decomposition")
    return hashlib.sha256(json.dumps({key: state[key] for key in keys},
        sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
