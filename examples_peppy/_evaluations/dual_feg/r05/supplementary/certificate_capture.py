"""Capture one coherent primal PEP certificate."""

from typing import Any, cast

# Preserve the recorded import initialization order.
# isort: split
import hashlib
import json
import os
import sys
import uuid
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for key in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]:
    os.environ[key] = "1"
for key in [
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
]:
    path = ROOT / "supplementary" / ".runtime" / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
sys.path[:0] = [str(ROOT / "supplementary" / "approved"), str(ROOT)]
import cvxpy as cp  # noqa: E402 - imports follow runtime or notebook setup
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup
from dual_feg_setup import (  # noqa: E402 - imports follow runtime or notebook setup
    get_pep_setup,
)

import pepflow as pf  # noqa: E402 - imports follow runtime or notebook setup
from pepflow.constants import (  # noqa: E402 - imports follow runtime or notebook setup
    PSD_CONSTRAINT,
)
from pepflow.solver import (  # noqa: E402 - imports follow runtime or notebook setup
    CVXPrimalSolver,
)


def capture(N, dropped=()):
    allowed = json.loads((ROOT / "supplementary/approved/allowlist.json").read_text())[
        "exact_read_files"
    ]
    sources = [Path(p) for p in allowed if Path(p).parent.name == "pepflow"] + [
        ROOT / "dual_feg_setup.py",
        Path(__file__).resolve(),
    ]
    hashes = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sources
    }
    ctx, pb, obj = get_pep_setup(N, {"L": 1, "R": 1})
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    groups = ctx.get_constraint_data(obj)
    assert not groups.psd_dict
    entries += [
        (c, "interpolation", str(obj), str(group))
        for group, constraints in groups.sc_dict.items()
        for c in constraints
    ]
    constraints = [c for c, *_ in entries if c.name not in dropped]
    solver = CVXPrimalSolver(
        perf_metric=pb.performance_metric, constraints=constraints, context=ctx
    )
    problem = solver.build_problem(resolve_parameters={"L": 1, "R": 1})
    options = {"solver": "CLARABEL"}
    try:
        val = problem.solve(**options)
    except cp.error.SolverError:
        options = {"solver": "SCS", "eps": 1e-7, "max_iters": 200000}
        val = problem.solve(**options)
    pm = pf.ExpressionManager(ctx, resolve_parameters={"L": 1, "R": 1})

    def coords(s):
        e = pm.eval_scalar(pf.Scalar.zero() + s)
        return {
            "gram": np.asarray(e.inner_prod_coords, dtype=float).tolist(),
            "func": np.asarray(e.func_coords, dtype=float).tolist(),
            "offset": float(e.offset),
        }

    duals, metadata, ccoords = {}, {}, {}
    for c, origin, owner, group in entries:
        value = solver.dual_var_manager.dual_value(c.name)
        duals[c.name] = None if c.name in dropped else float(value)
        metadata[c.name] = {
            "origin": origin,
            "owner": owner,
            "group": group,
            "kind": "scalar",
            "comparator": c.cmp.value,
            "shape": [],
            "relaxed": c.name in dropped,
        }
        residual = c.lhs - c.rhs
        if c.cmp.value in ("GE", "SEQ"):
            residual = -residual
        ccoords[c.name] = coords(residual)
    S = np.asarray(solver.dual_var_manager.dual_value(PSD_CONSTRAINT), dtype=float)
    data: dict[str, Any] = {
        "N": N,
        "N_verify": N,
        "opt_value": float(val),
        "tau_sol": duals["initial_condition"],
        "tau_name": "initial_condition",
        "solver_status": problem.status,
        "solver_options": options,
        "basis_vectors": [str(v) for v in ctx.basis_vectors()],
        "basis_scalars": [str(v) for v in ctx.basis_scalars()],
        "S_matrix": S.tolist(),
        "S_row_names": [str(v) for v in ctx.basis_vectors()],
        "S_col_names": [str(v) for v in ctx.basis_vectors()],
        "named_dual_values": duals,
        "constraint_metadata": metadata,
        "constraint_coordinates": ccoords,
        "metric_coordinates": coords(pb.performance_metric),
        "relaxed_constraints": list(dropped),
        "certificate_provenance": {
            "solve_id": str(uuid.uuid4()),
            "pep_type": "primal",
            "solver_status": problem.status,
            "solver": {
                "api": "CVXPrimalSolver.build_problem",
                "cvxpy_version": cp.__version__,
                "effective_name": problem.solver_stats.solver_name,
                "settings": options,
            },
        },
    }
    assert all(
        hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h
        for p, h in hashes.items()
    )
    cast(dict[str, Any], data["certificate_provenance"])["source_hashes"] = hashes
    return data


if __name__ == "__main__":
    data = capture(6)
    (ROOT / "state" / "dual_feg_dense.json").write_text(json.dumps(data, indent=2))
    print("Dense", data["opt_value"], data["solver_status"], flush=True)
    print("Basis", data["basis_vectors"], flush=True)
    for name, v in data["named_dual_values"].items():
        if v is not None and v > 1e-6:
            print(name, v, str(Fraction(v).limit_denominator(1000)), flush=True)
    print("S eigenvalues", np.linalg.eigvalsh(data["S_matrix"]), flush=True)
