"""Capture all named multipliers from one primal solve."""

import hashlib
import json
import uuid
from importlib.metadata import version
from pathlib import Path

import numpy as np
import runtime
from pgm_setup import get_pep_setup

from pepflow.constraint import ScalarConstraint


def capture(n, relaxed=()):
    ctx, pb, obj = get_pep_setup(n, {"L": 1, "R": 1})
    if relaxed:
        pb.set_relaxed_constraints(list(relaxed))
    source_paths = [
        runtime.ROOT / "pgm_setup.py",
        Path(__file__),
        runtime.ROOT / "supplementary/helpers/runtime.py",
    ]
    allowlist = json.loads((runtime.APPROVED / "allowlist.json").read_text())
    source_paths += [
        Path(p)
        for p in allowlist["exact_read_files"]
        if Path(p).parent == runtime.APPROVED / "pepflow"
    ]
    source_hashes = {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths
    }
    result, options = runtime.solve_setup(ctx, pb, {"L": 1, "R": 1})
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        entries.extend(
            (c, "interpolation", str(owner), str(group))
            for group, cs in groups.sc_dict.items()
            for c in cs
        )
        entries.extend(
            (c, "interpolation", str(owner), str(group))
            for group, c in groups.psd_dict.items()
        )
    meta, duals = {}, {}
    for c, origin, owner, group in entries:
        is_scalar = isinstance(c, ScalarConstraint)
        dropped = c.name in pb.relaxed_constraints
        value = result.get_dual_value(c.name)
        if value is None and not dropped:
            raise ValueError(f"Missing dual {c.name}")
        meta[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar" if is_scalar else "psd",
            comparator=c.cmp.value,
            shape=[] if is_scalar else list(np.asarray(c.lhs - c.rhs).shape),
            relaxed=dropped,
        )
        duals[c.name] = (
            None
            if dropped
            else float(value)
            if is_scalar
            else np.asarray(value).tolist()
        )
    S = result.get_gram_dual_matrix()
    displays = {}
    for owner in ctx.func_to_triplets:
        data = result.get_scalar_constraint_dual_value_in_numpy(owner)
        if not isinstance(data, dict):
            data = {"default": data}
        for group, matrix in data.items():
            displays[f"{owner}/{group}"] = dict(
                matrix=np.asarray(matrix.matrix).tolist(),
                row_names=list(matrix.row_names),
                col_names=list(matrix.col_names),
            )
    sample = dict(
        N=n,
        N_verify=n,
        opt_value=float(result.opt_value),
        tau_sol=float(result.get_dual_value("initial_condition")),
        tau_name="initial_condition",
        relaxed_constraints=list(pb.relaxed_constraints),
        S_matrix=np.asarray(S.matrix).tolist(),
        S_row_names=list(S.row_names),
        S_col_names=list(S.col_names),
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        named_dual_values=duals,
        constraint_metadata=meta,
        lambda_groups=displays,
        certificate_provenance=dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=str(result.solver_status),
            source_hashes=source_hashes,
            solver=dict(
                api="CVXPrimalSolver.build_problem",
                cvxpy_version=version("cvxpy"),
                effective_name=options["solver"],
                settings=options,
            ),
        ),
    )
    for p, sha in source_hashes.items():
        assert hashlib.sha256(Path(p).read_bytes()).hexdigest() == sha
    return sample
