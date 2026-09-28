"""Acquire one coherent numerical full-PEP certificate for the current run."""

import hashlib
import importlib.util
import json
import sys
import uuid
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

import cvxpy as cp
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
EXAMPLE = HERE.parent
ROOT = EXAMPLE.parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
# Imports follow repository-path and runtime setup.
from pepflow.constraint import PSDConstraint, ScalarConstraint  # noqa: E402
from pepflow.operator import LinearOperatorTranspose  # noqa: E402

NAME = "ogm_conjecture_4"
STATE = HERE / "b3_prior_N4"
B1 = json.loads((STATE / f"{NAME}_b1.json").read_text())
SETUP = EXAMPLE / "ogm_conjecture4_setup.py"
spec = importlib.util.spec_from_file_location("b2_current_setup", SETUP)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load setup module: {SETUP}")

mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
N = B1["N_verify"]
PARAMS = {k: sp.sympify(v) for k, v in json.loads(B1["params_json"]).items()}
SETTINGS = B1["solver_settings"]
SOURCE_PATHS = [
    SETUP,
    Path(__file__),
    *sorted(
        p for p in (ROOT / "pepflow").glob("*.py") if not p.name.endswith("_test.py")
    ),
]
HASHES = {
    p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in SOURCE_PATHS
}


def inventory(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in [*ctx.func_to_triplets, *ctx.oper_to_duplets]:
        if isinstance(owner, LinearOperatorTranspose):
            continue
        groups = ctx.get_constraint_data(owner)
        entries.extend(
            (c, "interpolation", str(owner), str(group))
            for group, constraints in groups.sc_dict.items()
            for c in constraints
        )
        entries.extend(
            (c, "interpolation", str(owner), str(group))
            for group, c in groups.psd_dict.items()
        )
    assert len({c.name for c, *_ in entries}) == len(entries)
    return entries


def acquire(relaxed, label):
    ctx, pb, obj = mod.get_pep_setup(sp.S(N), PARAMS)
    pb.set_relaxed_constraints(relaxed)
    original_solve = cp.Problem.solve
    stats = {}

    def configured_solve(problem, *args, **kwargs):
        value = original_solve(problem, *args, **(SETTINGS | kwargs))
        stats.update(
            effective_name=problem.solver_stats.solver_name,
            solve_time=problem.solver_stats.solve_time,
            max_constraint_violation=max(
                float(np.max(c.violation())) for c in problem.constraints
            ),
        )
        return value

    with patch.object(cp.Problem, "solve", configured_solve):
        result = pb.solve(context=ctx, resolve_parameters=PARAMS)
    assert result.context is ctx and result.solver_status == "optimal"
    ctx.set_as_current()
    entries = inventory(ctx, pb)
    named, metadata = {}, {}
    for c, origin, owner, group in entries:
        scalar = isinstance(c, ScalarConstraint)
        assert scalar or isinstance(c, PSDConstraint)
        dropped = c.name in relaxed
        value = result.get_dual_value(c.name)
        if not dropped:
            assert value is not None and np.all(np.isfinite(np.asarray(value, float)))
        shape = [] if scalar else list(np.asarray(c.lhs - c.rhs).shape)
        assert value is None or list(np.asarray(value).shape) == shape
        metadata[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar" if scalar else "psd",
            comparator=c.cmp.value,
            shape=shape,
            relaxed=dropped,
        )
        named[c.name] = (
            None if dropped else float(value) if scalar else np.asarray(value).tolist()
        )
    assert set(relaxed).issubset(metadata)
    lamb = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert not isinstance(lamb, dict), "Adapt display for grouped inequalities"
    S = result.get_gram_dual_matrix()
    data = dict(
        N=N,
        N_verify=N,
        params_json=B1["params_json"],
        opt_value=float(result.opt_value),
        tau_sol=float(result.get_dual_value("initial_condition")),
        tau_name="initial_condition",
        relaxed_constraints=list(relaxed),
        lambda_matrix=np.asarray(lamb.matrix, float).tolist(),
        lambda_row_names=list(lamb.row_names),
        lambda_col_names=list(lamb.col_names),
        S_matrix=np.asarray(S.matrix, float).tolist(),
        S_row_names=list(S.row_names),
        S_col_names=list(S.col_names),
        basis_vectors=[str(v) for v in ctx.basis_vectors()],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        named_dual_values=named,
        constraint_metadata=metadata,
        normalization=dict(
            tau_name="initial_condition",
            initial_condition=B1["initial_condition"],
            performance_metric=B1["performance_metric"],
            bound_value=float(result.opt_value),
            bound_formula=B1["conjectured_rate"],
        ),
        certificate_provenance=dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=str(result.solver_status),
            source_hashes=HASHES,
            solver=dict(
                api="PEPBuilder.solve_primal",
                cvxpy_version=version("cvxpy"),
                settings=SETTINGS,
                **stats,
            ),
        ),
        label=label,
    )
    return ctx, pb, obj, result, entries, data


def save(path, data):
    path.write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def main():
    dense = acquire([], "dense")
    dense_data = dense[-1]
    save(STATE / f"{NAME}_dense.json", dense_data)
    print(
        "DENSE",
        dense_data["opt_value"],
        "candidate",
        float(mod.conjectured_rate(N)),
        flush=True,
    )
    for name, value in dense_data["named_dual_values"].items():
        print(name, value, flush=True)
    print("DENSE S EIGENVALUES", np.linalg.eigvalsh(dense_data["S_matrix"]), flush=True)
    # First retain exactly the dense multipliers above a declared threshold.
    threshold = 1e-6
    relaxed = [
        name
        for name, value in dense_data["named_dual_values"].items()
        if dense_data["constraint_metadata"][name]["origin"] == "interpolation"
        and value is not None
        and abs(value) < threshold
    ]
    selected = acquire(relaxed, "threshold_1e-6")
    data = selected[-1]
    data["sparsity_search"] = dict(
        threshold=threshold,
        criterion="drop interpolation multipliers with abs(value)<threshold",
        dropped_count=len(relaxed),
        dense_value=dense_data["opt_value"],
    )
    save(HERE / "b2_selected_capture.json", data)
    print("SELECTED", data["opt_value"], "dropped", len(relaxed), flush=True)
    for name, value in data["named_dual_values"].items():
        if value is not None:
            print(name, value, flush=True)
    print("SELECTED S", np.asarray(data["S_matrix"]), flush=True)
    print("SELECTED S EIGENVALUES", np.linalg.eigvalsh(data["S_matrix"]), flush=True)


if __name__ == "__main__":
    main()
