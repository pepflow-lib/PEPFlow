# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

from typing import Any

# Preserve the recorded import initialization order.
# isort: split
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import hashlib
import json

import cvxpy as cp
import numpy as np
import pgm_setup as mod

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]
import sympy as sp  # noqa: F401 -- Required by exec of pgm_b2.json#lamb_code.

from pepflow.pep_result import PEPResult
from pepflow.solver import CVXDualSolver
from pepflow.utils import PEPType

previous = json.loads((runtime.ROOT / "state/pgm_b2.json").read_text())
exec(previous["lamb_code"])
for n, destination in [
    (4, "state/pgm_selected_raw.json"),
    (6, "supplementary/b2-N6-raw.json"),
]:
    hashes = previous["source_hashes"]
    for name, digest in hashes.items():
        assert hashlib.sha256((runtime.ROOT / name).read_bytes()).hexdigest() == digest
    ctx, pb, _ = mod.get_pep_setup(n, {"L": 1, "R": 1})
    records = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        assert not groups.psd_dict
        records.extend(
            (c, "interpolation", str(owner), str(group))
            for group, cs in groups.sc_dict.items()
            for c in cs
        )
    constraints = []
    dropped = []
    equalities = {}
    for c, origin, owner, group in records:
        assert c.cmp.value == "LE"
        if origin == "interpolation":
            left, right = c.name.split(":")[1].split(",")
            keep = left == "x_star" or (
                right != "x_star" and int(right[2:]) == int(left[2:]) + 1
            )
            if not keep:
                dropped.append(c.name)
                continue
            value = lambda_candidate(owner, left, right, n)
            c.dual_eq(float(value))
            equalities[c.name] = str(value)
        constraints.append(c)
    solver = CVXDualSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    options = {"solver": "CLARABEL"}
    try:
        problem.solve(**options)
    except cp.error.SolverError:
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        problem.solve(**options)
    result = PEPResult(
        problem.value, solver.dual_var_manager, PEPType.DUAL, problem.status, ctx
    )
    metadata = {}
    duals = {}
    for c, origin, owner, group in records:
        relaxed = c.name in dropped
        val = result.get_dual_value(c.name)
        assert val is not None or relaxed
        metadata[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar",
            comparator=c.cmp.value,
            shape=[],
            relaxed=relaxed,
        )
        duals[c.name] = None if relaxed else float(val)
    data: dict[str, Any] = dict(
        N=n,
        opt_value=problem.value,
        status=problem.status,
        solver_options=options,
        pep_type="dual",
        named_dual_values=duals,
        constraint_metadata=metadata,
        S_matrix=result.get_gram_dual_matrix().matrix.tolist(),
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        relaxed_constraints=dropped,
        source_hashes=hashes,
        derived_multiplier_equalities=equalities,
        sign_convention="All original constraints are scalar LE; CVXDualSolver uses performance - sum(lambda*(lhs-rhs)) + S = bound. No original EQ or matrix constraints are present. Multiplier-selection equalities are auxiliary dual constraints, not extra original residuals.",
    )
    for name, digest in hashes.items():
        assert hashlib.sha256((runtime.ROOT / name).read_bytes()).hexdigest() == digest
    (runtime.ROOT / destination).write_text(json.dumps(data, indent=2))
    print(
        n,
        problem.status,
        problem.value,
        "minimum S eigenvalue",
        np.linalg.eigvalsh(data["S_matrix"]).min(),
        flush=True,
    )
