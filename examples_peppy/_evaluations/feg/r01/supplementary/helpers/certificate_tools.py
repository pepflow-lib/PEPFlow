"""Capture a complete scalar-constraint certificate for this operator setup."""

import hashlib
import json
import uuid
from pathlib import Path

import numpy as np
from solve_tools import solve_setup

import pepflow as pf
from pepflow.utils import Comparator


def entries_for(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for obj in list(ctx.func_to_triplets) + list(ctx.oper_to_duplets):
        groups = ctx.get_constraint_data(obj)
        assert not groups.psd_dict, (
            "This capture route requires scalar-only interpolation"
        )
        entries.extend(
            (c, "interpolation", str(obj), str(group))
            for group, constraints in groups.sc_dict.items()
            for c in constraints
        )
    assert len({c.name for c, *_ in entries}) == len(entries)
    return entries


def capture(ctx, pb, obj, params):
    result, options = solve_setup(ctx, pb, params)
    entries = entries_for(ctx, pb)
    metadata, duals = {}, {}
    for c, origin, owner, group in entries:
        assert isinstance(c, pf.ScalarConstraint)
        dropped = c.name in pb.relaxed_constraints
        value = result.get_dual_value(c.name)
        assert dropped or value is not None
        metadata[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=dropped,
        )
        duals[c.name] = None if dropped else float(value)
    sm = result.get_gram_dual_matrix()
    lamb = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert isinstance(lamb, dict)
    state = {
        "opt_value": float(result.opt_value),
        "tau_sol": float(result.get_dual_value("initial_condition")),
        "tau_name": "initial_condition",
        "S_matrix": np.asarray(sm.matrix, float).tolist(),
        "S_row_names": list(sm.row_names),
        "S_col_names": list(sm.col_names),
        "basis_vectors": [str(v) for v in ctx.basis_vectors()],
        "basis_scalars": [str(v) for v in ctx.basis_scalars()],
        "named_dual_values": duals,
        "constraint_metadata": metadata,
        "relaxed_constraints": list(pb.relaxed_constraints),
        "lambda_groups": {
            str(k): dict(
                matrix=np.asarray(v.matrix, float).tolist(),
                row_names=list(v.row_names),
                col_names=list(v.col_names),
            )
            for k, v in lamb.items()
        },
        "certificate_provenance": {
            "solve_id": str(uuid.uuid4()),
            "pep_type": "primal",
            "solver_status": str(result.solver_status),
            "solver": {
                "api": "CVXPrimalSolver.build_problem",
                "effective_name": options["solver"],
                "settings": options,
            },
        },
    }
    return state, result, sm


def check_saved(ctx, pb, state, params, dense_value):
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    basis = ctx.basis_vectors()
    assert state["basis_vectors"] == [str(v) for v in basis]
    entries = entries_for(ctx, pb)
    assert {c.name for c, *_ in entries} == set(state["named_dual_values"])
    weighted = pf.Scalar.zero()
    inequality_duals = []
    for c, *_ in entries:
        value = state["named_dual_values"][c.name]
        if state["constraint_metadata"][c.name]["relaxed"]:
            assert value is None
            continue
        assert value is not None
        residual = c.lhs - c.rhs
        if c.cmp in (Comparator.GE, Comparator.SEQ):
            residual = -residual
        weighted += float(value) * residual
        if c.cmp != Comparator.EQ:
            inequality_duals.append(float(value))
    s = np.asarray(state["S_matrix"], float)
    s_scalar = sum(
        (float(s[i, j]) * basis[i] * basis[j] for i, j in np.ndindex(s.shape)),
        pf.Scalar.zero(),
    )
    residual = pm.eval_scalar(
        pb.performance_metric - state["opt_value"] - weighted + s_scalar
    )

    def maxabs(x):
        return float(np.max(np.abs(np.asarray(x, float)), initial=0))

    values = dict(
        identity_gram_max_abs=maxabs(residual.inner_prod_coords),
        identity_func_max_abs=maxabs(residual.func_coords),
        identity_offset_abs=maxabs(residual.offset),
        dense_relaxed_gap=abs(dense_value - state["opt_value"]),
        minimum_scalar_inequality_dual=min(inequality_duals, default=0),
        minimum_matrix_inequality_eigenvalue=0,
        minimum_S_eigenvalue=float(np.linalg.eigvalsh(s).min()),
    )
    passed = all(
        values[k] <= 1e-5
        for k in (
            "identity_gram_max_abs",
            "identity_func_max_abs",
            "identity_offset_abs",
            "dense_relaxed_gap",
        )
    )
    passed &= values["minimum_scalar_inequality_dual"] >= -1e-6
    passed &= values["minimum_S_eigenvalue"] >= -1e-6
    passed &= state["certificate_provenance"]["solver_status"] == "optimal"
    return dict(residuals=values, passed=bool(passed)), residual


def source_hashes(root):
    allowlist = json.loads((root / "supplementary/approved/allowlist.json").read_text())
    paths = [
        Path(p)
        for p in allowlist["exact_read_files"]
        if Path(p).parent.name == "pepflow"
    ]
    paths += [root / "feg_setup.py", root / "supplementary/helpers/solve_tools.py"]
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths
    }
