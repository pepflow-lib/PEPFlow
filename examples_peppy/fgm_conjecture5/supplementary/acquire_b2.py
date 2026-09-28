"""Acquire coherent dense and sparse primal-dual samples for Block 2."""

import hashlib
import json
import sys
import uuid
from contextlib import redirect_stderr, redirect_stdout
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Imports follow repository-path and runtime setup.
import cvxpy as cp  # noqa: E402
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import pepflow as pf  # noqa: E402
from pepflow.constraint import PSDConstraint, ScalarConstraint  # noqa: E402
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis  # noqa: E402
from pepflow.operator import LinearOperatorTranspose  # noqa: E402
from pepflow.pep_runner import _load_setup_module  # noqa: E402
from pepflow.utils import Comparator  # noqa: E402

# Initialized by main before certificate acquisition.
SOURCE_HASHES: dict[str, str]

ALGO = "fgm_conjecture5_test3"
SETUP = EXAMPLE / "fgm_conjecture5_setup.py"
SETTINGS = dict(
    solver="CLARABEL", tol_gap_abs=1e-8, tol_gap_rel=1e-8, tol_feas=1e-8, max_iter=300
)
TOLERANCES = dict(
    identity_atol=1e-5,
    identity_rtol=0.0,
    reconstruction_atol=1e-4,
    reconstruction_rtol=1e-5,
    dual_tol=1e-6,
    psd_tol=1e-6,
    dense_opt_atol=1e-5,
)
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


def all_entries(ctx, pb):
    """Inventory every initial/interpolation scalar or matrix constraint."""
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


def verify_certificate(ctx, pb, sample, dense_opt):
    """Rebuild the full identity from the original constraint expressions."""
    ctx.set_as_current()
    params_sp = {
        k: sp.Rational(str(v)) for k, v in json.loads(sample["params_json"]).items()
    }
    pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
    entries = all_entries(ctx, pb)
    meta = sample["constraint_metadata"]
    duals = sample["named_dual_values"]
    assert set(meta) == set(duals) == {c.name for c, *_ in entries}
    assert [str(v) for v in ctx.basis_vectors()] == sample["basis_vectors"]
    assert [str(v) for v in ctx.basis_scalars()] == sample["basis_scalars"]
    assert set(pb.relaxed_constraints) == set(sample["relaxed_constraints"])
    weighted = pf.Scalar.zero()
    inequality_values, matrix_eigenvalues = [], []
    for c, origin, owner, group in entries:
        data, value = meta[c.name], duals[c.name]
        scalar = isinstance(c, ScalarConstraint)
        expected = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar" if scalar else "psd",
            comparator=c.cmp.value,
            shape=[] if scalar else list(np.asarray(c.lhs - c.rhs).shape),
            relaxed=c.name in pb.relaxed_constraints,
        )
        assert data == expected
        if data["relaxed"]:
            assert value is None
            continue
        assert value is not None and np.all(np.isfinite(np.asarray(value, dtype=float)))
        assert list(np.asarray(value).shape) == data["shape"]
        residual = c.lhs - c.rhs
        if c.cmp in (Comparator.GE, Comparator.SEQ):
            residual = -residual
        if scalar:
            weighted += float(value) * (pf.Scalar.zero() + residual)
            if c.cmp != Comparator.EQ:
                inequality_values.append(float(value))
        else:
            dual = np.asarray(value, dtype=float)
            if c.cmp != Comparator.EQ:
                assert np.allclose(dual, dual.T, atol=1e-6, rtol=0)
                matrix_eigenvalues.extend(np.linalg.eigvalsh((dual + dual.T) / 2))
            weighted += sum(
                (float(dual[i, j]) * residual[j, i] for i, j in np.ndindex(dual.shape)),
                pf.Scalar.zero(),
            )
    basis = ctx.basis_vectors()
    S = np.asarray(sample["S_matrix"], dtype=float)
    assert sample["S_row_names"] == sample["S_col_names"] == sample["basis_vectors"]
    D = np.asarray(sample["numerical_decomposition"]["D"], dtype=float)
    E = np.asarray(sample["numerical_decomposition"]["ell_coords"], dtype=float)
    assert sample["numerical_decomposition"]["basis_labels"] == sample["basis_vectors"]
    ell = [
        sum((float(a) * v for a, v in zip(row, basis)), pf.Vector.zero()) for row in E
    ]
    S_numeric = sum(
        (float(D[i, j]) * ell[i] * ell[j] for i, j in np.ndindex(D.shape)),
        pf.Scalar.zero(),
    )
    diff = pb.performance_metric - sample["opt_value"] - weighted + S_numeric
    checked = pm.eval_scalar(diff)
    max_abs = lambda x: float(np.max(np.abs(np.asarray(x, dtype=float)), initial=0))  # noqa: E731 - retain the archived numerical helper
    residuals = dict(
        identity_gram_max_abs=max_abs(checked.inner_prod_coords),
        identity_func_max_abs=max_abs(checked.func_coords),
        identity_offset_abs=max_abs(checked.offset),
        S_reconstruction_max_abs=max_abs(E.T @ D @ E - S),
        dense_relaxed_gap=abs(dense_opt - sample["opt_value"]),
        minimum_scalar_inequality_dual=min(inequality_values, default=0.0),
        minimum_S_eigenvalue=float(np.linalg.eigvalsh((S + S.T) / 2).min()),
        minimum_matrix_inequality_eigenvalue=min(matrix_eigenvalues, default=0.0),
    )
    tol = TOLERANCES
    passed = (
        sample["certificate_provenance"]["solver_status"] == "optimal"
        and np.all(np.isfinite(S))
        and np.allclose(S, S.T, atol=tol["psd_tol"], rtol=0)
        and all(
            residuals[k] <= tol["identity_atol"]
            for k in (
                "identity_gram_max_abs",
                "identity_func_max_abs",
                "identity_offset_abs",
            )
        )
        and np.allclose(
            E.T @ D @ E,
            S,
            atol=tol["reconstruction_atol"],
            rtol=tol["reconstruction_rtol"],
        )
        and residuals["dense_relaxed_gap"] < tol["dense_opt_atol"]
        and residuals["minimum_scalar_inequality_dual"] >= -tol["dual_tol"]
        and residuals["minimum_S_eigenvalue"] >= -tol["psd_tol"]
        and residuals["minimum_matrix_inequality_eigenvalue"] >= -tol["psd_tol"]
    )
    checks = dict(tolerances=tol, residuals=residuals, passed=bool(passed))
    return checks, checked, S_numeric


def solve_sample(mod, b1, N, recipe, dense=None):
    params = json.loads(b1["params_json"])
    params_sp = {k: sp.Rational(str(v)) for k, v in params.items()}
    ctx, pb, obj = mod.get_pep_setup(sp.S(N), params_sp)
    entries = all_entries(ctx, pb)
    point_names = [str(ctx[f"x_{i}"]) for i in range(N + 1)]
    star = str(ctx["x_star"])
    if recipe == "dense":
        relaxed = []
    elif recipe == "threshold":
        assert dense is not None, (
            "Threshold sparsification requires a dense certificate"
        )
        relaxed = [
            c.name
            for c, origin, *_ in entries
            if origin == "interpolation"
            and abs(dense["named_dual_values"][c.name]) < 1e-7
        ]
    else:
        allowed = {f"{obj}:{point_names[i]},{point_names[i + 1]}" for i in range(N)}
        allowed.update(f"{obj}:{star},{name}" for name in point_names)
        if recipe == "expanded":
            allowed.update(
                f"{obj}:{point_names[i]},{point_names[j]}"
                for i in range(N + 1)
                for j in range(N + 1)
                if 0 < abs(i - j) <= 2
            )
        relaxed = [
            c.name
            for c, origin, *_ in entries
            if origin == "interpolation" and c.name not in allowed
        ]
    if relaxed:
        pb.set_relaxed_constraints(relaxed)
    original_solve = cp.Problem.solve
    solver_details = {}

    def recorded_solve(problem, *args, **kwargs):
        options = dict(SETTINGS)
        options.update(kwargs)
        value = original_solve(problem, *args, **options)
        solver_details.update(
            effective_name=problem.solver_stats.solver_name,
            settings=options,
            iterations=problem.solver_stats.num_iters,
            solve_seconds=problem.solver_stats.solve_time,
            max_primal_constraint_violation=max(
                float(np.max(c.violation())) for c in problem.constraints
            ),
        )
        return value

    cp.Problem.solve = recorded_solve
    try:
        result = pb.solve(resolve_parameters=params_sp)
    finally:
        cp.Problem.solve = original_solve
    if result.solver_status != "optimal":
        raise RuntimeError(f"{recipe} solve at N={N}: {result.solver_status}")
    pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
    metadata, named = {}, {}
    for c, origin, owner, group in entries:
        scalar = isinstance(c, ScalarConstraint)
        if not scalar and not isinstance(c, PSDConstraint):
            raise TypeError(c.name)
        dropped = c.name in relaxed
        value = result.get_dual_value(c.name)
        if value is None and not dropped:
            raise ValueError(f"Missing active dual: {c.name}")
        metadata[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar" if scalar else "psd",
            comparator=c.cmp.value,
            shape=[] if scalar else list(np.asarray(c.lhs - c.rhs).shape),
            relaxed=dropped,
        )
        named[c.name] = (
            None if dropped else float(value) if scalar else np.asarray(value).tolist()
        )
    S_sol = result.get_gram_dual_matrix()
    basis = ctx.basis_vectors()
    D, ell = ldl_decompose_with_reversed_basis(S_sol, basis, print_output=False)
    E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
    lamb = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert isinstance(lamb, pf.MatrixWithNames)  # one smooth-convex group in this setup
    sample = {
        **b1,
        "N": N,
        "N_verify": N,
        "opt_value": float(result.opt_value),
        "tau_sol": float(result.get_dual_value("initial_condition")),
        "tau_name": "initial_condition",
        "lambda_matrix": np.asarray(lamb.matrix, dtype=float).tolist(),
        "lambda_row_names": list(lamb.row_names),
        "lambda_col_names": list(lamb.col_names),
        "relaxed_constraints": relaxed,
        "relaxation_recipe": recipe,
        "S_matrix": np.asarray(S_sol.matrix, dtype=float).tolist(),
        "S_row_names": list(S_sol.row_names),
        "S_col_names": list(S_sol.col_names),
        "basis_vectors": [str(v) for v in basis],
        "basis_scalars": [str(v) for v in ctx.basis_scalars()],
        "named_dual_values": named,
        "constraint_metadata": metadata,
        "normalization": dict(
            tau_name="initial_condition",
            initial_condition=b1["initial_condition"],
            performance_metric=b1["performance_metric"],
            bound_value=float(result.opt_value),
            bound_formula=b1["conjectured_rate"],
        ),
        "certificate_provenance": dict(
            solve_id=str(uuid.uuid4()),
            pep_type="primal",
            solver_status=str(result.solver_status),
            source_hashes=SOURCE_HASHES,
            solver=dict(
                api="PEPBuilder.solve_primal",
                cvxpy_version=version("cvxpy"),
                **solver_details,
            ),
        ),
        "numerical_decomposition": dict(
            method="reverse_ldl",
            D=np.asarray(D).tolist(),
            ell_coords=E.tolist(),
            basis_labels=[str(v) for v in basis],
        ),
        "S_decomp_type": "ldl",
        "numerical_certificate_verified": False,
        "analytic_full_pep_verified": False,
        "lyapunov_proof_verified": False,
        "require_analytic_full_pep": False,
        "lamb_code": None,
        "S_code": None,
        "formula_status": dict(lambda_="unresolved", S="unresolved"),
    }
    sample["formula_status"] = {"lambda": "unresolved", "S": "unresolved"}
    checks, _, _ = verify_certificate(
        ctx, pb, sample, sample["opt_value"] if dense is None else dense["opt_value"]
    )
    checks["conjectured_value"] = float(mod.conjectured_bound(N))
    checks["conjectured_rate_abs_error"] = abs(
        sample["opt_value"] - checks["conjectured_value"]
    )
    checks["passed"] &= checks["conjectured_rate_abs_error"] < 1e-5
    sample["numerical_checks"] = checks
    sample["numerical_certificate_verified"] = sample["proof_valid"] = checks["passed"]
    sample["certificate_id"] = hashlib.sha256(
        json.dumps(
            {k: sample[k] for k in CERTIFICATE_KEYS},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    for path, digest in SOURCE_HASHES.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    return sample


def main():
    global SOURCE_HASHES
    b1 = json.loads((EXAMPLE / "state" / f"{ALGO}_b1.json").read_text())
    mod = _load_setup_module(str(SETUP))
    sources = {SETUP, Path(__file__).resolve()}
    sources.update(
        Path(m.__file__).resolve()
        for name, m in sys.modules.items()
        if (name == "pepflow" or name.startswith("pepflow."))
        and getattr(m, "__file__", None)
    )
    SOURCE_HASHES = {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(sources)
    }
    N = b1["N_verify"]
    records = []
    dense = None
    with (EXAMPLE / "supplementary" / "b2_solver.log").open(
        "w", encoding="utf-8"
    ) as log:
        for recipe in ["dense", "threshold", "adjacent_star", "expanded"]:
            with redirect_stdout(log), redirect_stderr(log):
                sample = solve_sample(mod, b1, N, recipe, dense)
            records.append(
                dict(
                    recipe=recipe,
                    opt_value=sample["opt_value"],
                    active_interpolation=sum(
                        not m["relaxed"] and m["origin"] == "interpolation"
                        for m in sample["constraint_metadata"].values()
                    ),
                    passed=sample["numerical_certificate_verified"],
                    checks=sample["numerical_checks"],
                )
            )
            print(json.dumps(records[-1]), flush=True)
            filename = EXAMPLE / "supplementary" / f"b2_{recipe}_sample.json"
            if recipe == "dense":
                dense = sample
                filename = EXAMPLE / "state" / f"{ALGO}_dense.json"
            filename.write_text(
                json.dumps(sample, indent=2, allow_nan=False), encoding="utf-8"
            )
            if (
                recipe in ("adjacent_star", "expanded")
                and sample["numerical_certificate_verified"]
            ):
                selected = sample
                break
        else:
            raise RuntimeError("No structured sparse certificate preserved the bound")
    selected["sparsity_search"] = records
    (EXAMPLE / "supplementary" / "b2_selected_pending_search.json").write_text(
        json.dumps(selected, indent=2, allow_nan=False), encoding="utf-8"
    )
    print(
        "SELECTED",
        selected["relaxation_recipe"],
        "D diagonal:",
        np.diag(selected["numerical_decomposition"]["D"]),
        flush=True,
    )
    for name, value in selected["named_dual_values"].items():
        if value is not None:
            print(name, f"{value:.12f}", flush=True)


if __name__ == "__main__":
    main()
