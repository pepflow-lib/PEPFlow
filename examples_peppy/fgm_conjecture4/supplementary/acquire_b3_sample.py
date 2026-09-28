"""Acquire a supplementary Block 3 sample without replacing N=4.

The study remains contaminated. Only the current study's setup/candidates and
generic non-test pepflow sources are used. No global formula search is repeated.
"""

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
import uuid
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

import cvxpy as cp
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parent.parent
NAME = STUDY.name
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
HELPER = HERE / "block2_certificate.py"
spec = importlib.util.spec_from_file_location("_n6_certificate_helpers", HELPER)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load certificate helper: {HELPER}")

helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
pf = helper.pf
N = 6
OUT = HERE / "b3_samples" / f"N{N}"
SETTINGS = dict(solver="SCS", eps_abs=1e-9, eps_rel=1e-9, max_iters=200000)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.resolve().relative_to(ROOT).as_posix()


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False), encoding="utf-8")


def solve(sparse, params, attempts):
    ctx, pb, obj = helper.mod.get_pep_setup(N, params)
    points = [ctx[f"x_{i}"] for i in range(N)] + [ctx[f"y_{N}"]]
    keep = {f"{obj}:{ctx['x_star']},{point}" for point in points}
    keep.update(f"{obj}:{points[i]},{points[i + 1]}" for i in range(N))
    if sparse:
        pb.set_relaxed_constraints(
            [
                c.name
                for c in obj.get_interpolation_constraints(ctx)
                if c.name not in keep
            ]
        )
    original = cp.Problem.solve
    info = {}

    def precise(problem, *args, **kwargs):
        kwargs.update(SETTINGS)
        value = original(problem, *args, **kwargs)
        info.update(
            effective_name=problem.solver_stats.solver_name,
            status=problem.status,
            num_iters=problem.solver_stats.num_iters,
            solve_time=problem.solver_stats.solve_time,
        )
        return value

    with patch.object(cp.Problem, "solve", precise):
        result = pb.solve(resolve_parameters=params)
    attempts.append(dict(sparse=sparse, settings=dict(SETTINGS), **info))
    dump(OUT / "solver_attempts.json", attempts)
    assert result.context is ctx and pb.ctx is ctx
    assert result.solver_status == "optimal", info
    return ctx, pb, obj, result, info


def capture(live, params, b1, source_hashes, dense_bound):
    ctx, pb, obj, result, info = live
    ctx.set_as_current()
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    entries = helper.constraint_entries(ctx, pb)
    metadata, values = helper.capture_duals(entries, pb, result)
    assert set(metadata) == set(values)
    S = result.get_gram_dual_matrix()
    S_array = np.asarray(S.matrix, dtype=float)
    basis = ctx.basis_vectors()
    D, ell = helper.ldl_decompose_with_reversed_basis(S, basis, print_output=False)
    D = np.asarray(D, dtype=float)
    E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
    bound = float(result.opt_value)
    candidate_bound = float(helper.mod.conjectured_rate(N, params["L"], params["R"]))
    checks, checked = helper.check_certificate(
        ctx,
        pb,
        params,
        entries,
        metadata,
        values,
        S_array,
        D,
        E,
        bound,
        dense_bound,
        candidate_bound,
        str(result.solver_status),
    )
    assert checks["passed"], checks
    lamb = result.get_scalar_constraint_dual_value_in_numpy(obj)
    descriptive = (
        "algo_name",
        "problem_type",
        "obj_tag",
        "params_json",
        "performance_metric",
        "initial_condition",
        "conjectured_rate",
        "setup_file",
        "clean_room_status",
        "independent_reproduction",
        "contamination",
    )
    record = {key: b1[key] for key in descriptive}
    record.update(
        N=N,
        N_verify=N,
        opt_value=bound,
        tau_sol=values["initial_condition"],
        tau_name="initial_condition",
        relaxed_constraints=list(pb.relaxed_constraints),
        lambda_matrix=np.asarray(lamb.matrix, dtype=float).tolist(),
        lambda_row_names=list(lamb.row_names),
        lambda_col_names=list(lamb.col_names),
        S_matrix=S_array.tolist(),
        S_row_names=list(S.row_names),
        S_col_names=list(S.col_names),
        basis_vectors=[str(v) for v in basis],
        basis_scalars=[str(v) for v in ctx.basis_scalars()],
        named_dual_values=values,
        constraint_metadata=metadata,
        normalization=dict(
            tau_name="initial_condition",
            initial_condition=b1["initial_condition"],
            performance_metric=b1["performance_metric"],
            bound_value=bound,
            bound_formula=b1["conjectured_rate"],
            L=1,
            R=1,
            radius_squared=1,
        ),
        certificate_provenance=dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=str(result.solver_status),
            source_hashes=source_hashes,
            solver=dict(
                api="PEPBuilder.solve_primal",
                cvxpy_version=version("cvxpy"),
                settings=dict(SETTINGS),
                **info,
            ),
        ),
        numerical_checks=checks,
        numerical_decomposition=dict(
            method="reverse_ldl",
            D=D.tolist(),
            ell_coords=E.tolist(),
            basis_labels=[str(v) for v in basis],
        ),
        numerical_residual_coordinates=dict(
            gram=np.asarray(checked.inner_prod_coords, dtype=float).tolist(),
            function=np.asarray(checked.func_coords, dtype=float).tolist(),
            offset=float(checked.offset),
        ),
        S_decomp_type="ldl",
        numerical_certificate_verified=True,
        proof_valid=True,
        analytic_full_pep_verified=False,
        lyapunov_proof_verified=False,
        require_analytic_full_pep=False,
        supplementary_only=True,
    )
    record["certificate_id"] = helper.certificate_id(record)
    return record


def candidate_checks(live, record, params, prior):
    ctx, pb, obj, _, _ = live
    ctx.set_as_current()
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    lamb = helper.candidate_multiplier_map(ctx, obj, N)
    values = record["named_dual_values"]
    interpolation = obj.get_interpolation_constraints(ctx)
    guess = pm.eval_scalar(helper.candidate_S(ctx, pb, obj, N, params["L"]))
    matrix = np.asarray(guess.inner_prod_coords, dtype=float)
    squares = pm.eval_scalar(helper.candidate_S_squares(ctx, obj, N, params["L"]))
    max_abs = lambda a: float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0.0))  # noqa: E731 - retain the archived numerical helper
    checks = dict(
        lambda_max_abs=max(
            abs(float(lamb[c.name]) - (values[c.name] or 0.0)) for c in interpolation
        ),
        S_gram_max_abs=max_abs(matrix - np.asarray(record["S_matrix"])),
        S_func_max_abs=max_abs(guess.func_coords),
        S_offset_abs=abs(float(guess.offset)),
        square_formula_gram_max_abs=max_abs(
            np.asarray(squares.inner_prod_coords, dtype=float) - matrix
        ),
        square_formula_func_max_abs=max_abs(squares.func_coords),
        square_formula_offset_abs=abs(float(squares.offset)),
    )
    checks["matches_selected_at_1e_4"] = all(value <= 1e-4 for value in checks.values())
    _, alpha, weights = helper.candidate_edge_weights(N)
    checks["sample_minimum_alpha"] = min(float(a) for a in alpha)
    checks["sample_minimum_edge_weight"] = min(float(w) for w in weights.values())
    record.update(
        formula_status={"lambda": "candidate", "S": "candidate"},
        lamb_code=prior["lamb_code"],
        S_code=prior["S_code"],
        candidate_checks=checks,
        candidate_lambda={k: float(v) for k, v in lamb.items()},
        candidate_S_matrix=matrix.tolist(),
        candidate_edge_weights={f"{i},{j}": float(w) for (i, j), w in weights.items()},
        closed_form_search=dict(
            completed=True,
            reused_from_certificate_id=prior["certificate_id"],
            reused_from_path=relative(STUDY / "state" / f"{NAME}_b2.json"),
            references_reviewed=[],
            initial_search_record=copy.deepcopy(prior["closed_form_search"]),
            applicability=f"Same FGM setup, L=R=1, chain/star support; candidate definitions accept N={N}.",
            attempts=[
                dict(
                    method=f"Evaluate the existing N=4 chain/star and S-square candidates at N={N}",
                    outcome="Finite-sample checks only; no global rediscovery or analytic sign proof.",
                    checks=checks,
                )
            ],
            unresolved_components=copy.deepcopy(
                prior["closed_form_search"]["unresolved_components"]
            ),
        ),
    )
    assert checks["matches_selected_at_1e_4"], checks


def revalidate(record, params):
    assert record["certificate_id"] == helper.certificate_id(record)
    for path, expected in record["certificate_provenance"]["source_hashes"].items():
        assert not Path(path).is_absolute()
        assert digest(ROOT / path) == expected, path
    assert record["N"] == record["N_verify"] == N
    assert json.loads(record["params_json"]) == {"L": 1, "R": 1}
    ctx, pb, obj = helper.mod.get_pep_setup(N, params)
    if record["relaxed_constraints"]:
        pb.set_relaxed_constraints(record["relaxed_constraints"])
    entries = helper.constraint_entries(ctx, pb)
    assert {c.name for c, *_ in entries} == set(record["constraint_metadata"])
    assert set(record["constraint_metadata"]) == set(record["named_dual_values"])
    for c, origin, owner, group in entries:
        scalar = isinstance(c, helper.ScalarConstraint)
        expected = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar" if scalar else "psd",
            comparator=c.cmp.value,
            shape=[] if scalar else list(np.asarray(c.lhs - c.rhs).shape),
            relaxed=c.name in pb.relaxed_constraints,
        )
        assert record["constraint_metadata"][c.name] == expected
        value = record["named_dual_values"][c.name]
        if expected["relaxed"]:
            assert value is None
        else:
            assert (
                value is not None and np.isfinite(np.asarray(value, dtype=float)).all()
            )
            assert list(np.asarray(value).shape) == expected["shape"]
    assert [str(v) for v in ctx.basis_vectors()] == record["basis_vectors"]
    assert record["S_row_names"] == record["S_col_names"] == record["basis_vectors"]
    assert [str(v) for v in ctx.basis_scalars()] == record["basis_scalars"]
    assert record["normalization"]["bound_value"] == record["opt_value"]
    assert record["normalization"]["initial_condition"] == "||x_0-x_star||^2 <= R^2"
    assert record["normalization"]["performance_metric"] == "f(y_N) - f(x_star)"
    assert record["normalization"]["L"] == record["normalization"]["R"] == 1
    assert record["normalization"]["radius_squared"] == 1
    assert record["tau_name"] == "initial_condition"
    assert record["tau_sol"] == record["named_dual_values"]["initial_condition"]
    D = np.asarray(record["numerical_decomposition"]["D"], dtype=float)
    E = np.asarray(record["numerical_decomposition"]["ell_coords"], dtype=float)
    checks, _ = helper.check_certificate(
        ctx,
        pb,
        params,
        entries,
        record["constraint_metadata"],
        record["named_dual_values"],
        np.asarray(record["S_matrix"], dtype=float),
        D,
        E,
        record["opt_value"],
        record["dense_comparator_bound"],
        float(helper.mod.conjectured_rate(N, 1, 1)),
        record["certificate_provenance"]["solver_status"],
    )
    assert checks["passed"] and checks == record["numerical_checks"], checks
    return checks


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    b1_path = STUDY / "state" / f"{NAME}_b1.json"
    prior_path = STUDY / "state" / f"{NAME}_b2.json"
    preserved_paths = [
        STUDY / "state" / f"{NAME}_{suffix}.json"
        for suffix in ("b2", "relaxed", "dense")
    ]
    preserved_hashes = {relative(p): digest(p) for p in preserved_paths}
    b1 = json.loads(b1_path.read_text(encoding="utf-8"))
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    assert prior["N_verify"] == 4
    assert helper.certificate_id(prior) == prior["certificate_id"]
    assert (
        digest(HELPER)
        == prior["certificate_provenance"]["source_hashes"][relative(HELPER)]
    )
    params = {"L": sp.Integer(1), "R": sp.Integer(1)}
    source_paths = [
        helper.setup_path,
        HELPER,
        Path(__file__).resolve(),
        *sorted(
            p
            for p in (ROOT / "pepflow").glob("*.py")
            if not p.name.endswith("_test.py")
        ),
    ]
    hashes = {relative(p): digest(p) for p in source_paths}
    attempts = []
    dense_live = solve(False, params, attempts)
    dense_bound = float(dense_live[3].opt_value)
    dense = capture(dense_live, params, b1, hashes, dense_bound)
    dense["dense_comparator_bound"] = dense_bound
    dump(OUT / "dense.json", dense)
    live = solve(True, params, attempts)
    record = capture(live, params, b1, hashes, dense_bound)
    record["dense_comparator_bound"] = dense_bound
    record["dense_comparator_certificate_id"] = dense["certificate_id"]
    candidate_checks(live, record, params, prior)
    for path, expected in hashes.items():
        assert digest(ROOT / path) == expected, path
    for path, expected in preserved_hashes.items():
        assert digest(ROOT / path) == expected, path
    dump(OUT / "certificate.json", record)
    revalidation = revalidate(
        json.loads((OUT / "certificate.json").read_text()), params
    )
    revalidate(json.loads((OUT / "dense.json").read_text()), params)
    audit_path = OUT / "audit.json"
    audit = json.loads(audit_path.read_text()) if audit_path.exists() else {}
    audit.update(
        updated_utc=datetime.now(timezone.utc).isoformat(),
        study_status="contaminated",
        no_analytic_proof_claim=True,
        original_N4_preserved=True,
        original_N4_hashes=preserved_hashes,
        source_hashes=hashes,
        files_consulted_by_acquisition=sorted(
            set(
                [
                    relative(b1_path),
                    relative(prior_path),
                    *preserved_hashes,
                    *hashes,
                    relative(OUT / "dense.json"),
                    relative(OUT / "certificate.json"),
                    relative(audit_path),
                ]
            )
        ),
        certificate_id=record["certificate_id"],
        dense_certificate_id=dense["certificate_id"],
        serialized_revalidation_passed=revalidation["passed"],
        solver_attempts=attempts,
        note=f"N={N} is supplementary only. Selected N=4 state, dense and relaxed files are hash-preserved. The notebook is never opened or written by this script.",
    )
    dump(audit_path, audit)
    print(
        json.dumps(
            dict(
                certificate_id=record["certificate_id"],
                opt_value=record["opt_value"],
                dense_bound=dense_bound,
                residuals=record["numerical_checks"]["residuals"],
                candidate_checks=record["candidate_checks"],
                certificate_path=relative(OUT / "certificate.json"),
                dense_path=relative(OUT / "dense.json"),
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, default=6, choices=range(2, 13))
    N = parser.parse_args().N
    OUT = HERE / "b3_samples" / f"N{N}"
    run()
