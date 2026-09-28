"""Acquire one coherent Block 2 certificate using only the current-run setup.

No reference examples, previous target runs, repository history, or tests are read.
The selected lambda, S and all extra multipliers originate in one primal solve.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import uuid
from fractions import Fraction
from importlib.metadata import version
from pathlib import Path

import cvxpy as cp
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
EXAMPLE = HERE.parent
ROOT = EXAMPLE.parent.parent
sys.path.insert(0, str(ROOT))
# Imports follow repository-path and runtime setup.
import pepflow as pf  # noqa: E402
from pepflow.constraint import PSDConstraint, ScalarConstraint  # noqa: E402
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis  # noqa: E402
from pepflow.operator import LinearOperatorTranspose  # noqa: E402
from pepflow.utils import Comparator  # noqa: E402

ALGO = "fgm_rational_test"
STATE = EXAMPLE / "state"
SETUP = EXAMPLE / "fgm_rational_tight_setup.py"
OPTIONS = dict(tol_gap_abs=1e-8, tol_gap_rel=1e-8, tol_feas=1e-8, max_iter=500)
TOLERANCES = dict(
    identity_atol=1e-5,
    identity_rtol=0.0,
    reconstruction_atol=1e-4,
    reconstruction_rtol=1e-5,
    dual_tol=1e-6,
    psd_tol=1e-6,
    dense_opt_atol=1e-5,
    conjecture_atol=1e-5,
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


def relative(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")


def write(path, data):
    path.write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def max_abs(values):
    return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0.0))


def load_inputs():
    b1 = json.loads((STATE / f"{ALGO}_b1.json").read_text(encoding="utf-8"))
    assert b1["algo_name"] == ALGO and b1["N_verify"] == 4
    params = {k: sp.Rational(str(v)) for k, v in json.loads(b1["params_json"]).items()}
    spec = importlib.util.spec_from_file_location("_block2_current_setup", SETUP)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load setup module: {SETUP}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert Path(pf.__file__).resolve() == ROOT / "pepflow/__init__.py"
    # Only generic top-level source modules; tests are explicitly excluded.
    sources = [
        SETUP,
        Path(__file__).resolve(),
        *sorted((ROOT / "pepflow").glob("*.py")),
    ]
    sources = [p for p in sources if not p.name.endswith("_test.py")]
    hashes = {relative(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    return b1, params, module, hashes


def inventory(ctx, pb):
    entries = [(c, "initial", None, None) for c in pb.init_conditions]
    for owner in [*ctx.func_to_triplets, *ctx.oper_to_duplets]:
        if isinstance(owner, LinearOperatorTranspose):
            continue
        owner.get_interpolation_constraints(ctx)
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
    assert len({c.name for c, *_ in entries}) == len(entries)
    return entries


def solve(b1, params, module, hashes, pattern, drop_names=(), dense_value=None):
    n = b1["N_verify"]
    ctx, pb, obj = module.get_pep_setup(sp.Integer(n), params)
    assert ctx["x_0"] is ctx["y_0"] and ctx["x_1"] is ctx["y_1"]
    entries = inventory(ctx, pb)
    pb.set_relaxed_constraints(list(drop_names))
    assert set(drop_names).issubset({c.name for c, *_ in entries})
    constraints = [c for c, *_ in entries if c.name not in pb.relaxed_constraints]
    solver = pf.CVXPrimalSolver(pb.performance_metric, constraints, ctx)
    problem = solver.build_problem(resolve_parameters=params)
    value = problem.solve(solver=cp.CLARABEL, **OPTIONS)
    print(
        f"{pattern}: N={n}, status={problem.status}, value={value:.14g}, dropped={len(drop_names)}",
        flush=True,
    )
    if problem.status != cp.OPTIMAL:
        raise RuntimeError(f"{pattern}: unusable status {problem.status}")
    result = pf.PEPResult(
        opt_value=value,
        dual_var_manager=solver.dual_var_manager,
        pep_type=pf.PEPType.PRIMAL,
        solver_status=problem.status,
        context=ctx,
    )
    ctx.set_as_current()
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    S_sol = result.get_gram_dual_matrix()
    S = np.asarray(S_sol.matrix, dtype=float)
    basis = ctx.basis_vectors()
    D, ell = ldl_decompose_with_reversed_basis(S_sol, basis, print_output=False)
    D = np.asarray(D, dtype=float)
    E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
    S_numeric = sum(
        (float(D[i, j]) * ell[i] * ell[j] for i, j in np.ndindex(D.shape)),
        pf.Scalar.zero(),
    )
    decomposition = dict(
        method="reverse_ldl",
        D=D.tolist(),
        ell_coords=E.tolist(),
        basis_labels=[str(v) for v in basis],
        factor_labels=[f"ell_{i + 1}" for i in range(len(ell))],
        eigenvalues=np.linalg.eigvalsh(S).tolist(),
        numerical_rank_at_1e_7=int(np.linalg.matrix_rank(S, tol=1e-7)),
    )
    metadata, duals = {}, {}
    scalar_signs, psd_signs = [], []
    weighted = pf.Scalar.zero()
    for c, origin, owner, group in entries:
        scalar = isinstance(c, ScalarConstraint)
        assert scalar or isinstance(c, PSDConstraint)
        dropped = c.name in pb.relaxed_constraints
        dual = result.get_dual_value(c.name)
        shape = [] if scalar else list(np.asarray(c.lhs - c.rhs).shape)
        metadata[c.name] = dict(
            origin=origin,
            owner=owner,
            group=group,
            kind="scalar" if scalar else "psd",
            comparator=c.cmp.value,
            shape=shape,
            relaxed=dropped,
        )
        if dropped:
            assert dual is None
            duals[c.name] = None
            continue
        assert dual is not None and np.all(np.isfinite(np.asarray(dual, dtype=float)))
        assert list(np.asarray(dual).shape) == shape
        residual = c.lhs - c.rhs
        if c.cmp in (Comparator.GE, Comparator.SEQ):
            residual = -residual
        if scalar:
            duals[c.name] = float(dual)
            weighted += float(dual) * (pf.Scalar.zero() + residual)
            if c.cmp != Comparator.EQ:
                scalar_signs.append(float(dual))
        else:
            arr = np.asarray(dual, dtype=float)
            duals[c.name] = arr.tolist()
            weighted += sum(
                (float(arr[i, j]) * residual[j, i] for i, j in np.ndindex(arr.shape)),
                pf.Scalar.zero(),
            )
            if c.cmp != Comparator.EQ:
                assert np.allclose(arr, arr.T, atol=TOLERANCES["psd_tol"], rtol=0)
                psd_signs.extend(np.linalg.eigvalsh((arr + arr.T) / 2))
    checked = pm.eval_scalar(
        pb.performance_metric - float(value) - weighted + S_numeric
    )
    reconstruction = E.T @ D @ E
    tau = duals["initial_condition"]
    conjecture = float(2 * params["L"] * params["R"] ** 2 / ((n + 2) * (n + 3)))
    residuals = dict(
        identity_gram_max_abs=max_abs(checked.inner_prod_coords),
        identity_func_max_abs=max_abs(checked.func_coords),
        identity_offset_abs=max_abs(checked.offset),
        S_reconstruction_max_abs=max_abs(reconstruction - S),
        dense_relaxed_gap=abs(
            float(value) - (float(value) if dense_value is None else dense_value)
        ),
        conjecture_gap=abs(float(value) - conjecture),
        minimum_scalar_inequality_dual=min(scalar_signs, default=0.0),
        minimum_S_eigenvalue=float(np.linalg.eigvalsh((S + S.T) / 2)[0]),
        minimum_matrix_inequality_eigenvalue=min(psd_signs, default=0.0),
    )
    passed = (
        np.all(np.isfinite(S))
        and np.allclose(S, S.T, atol=TOLERANCES["psd_tol"], rtol=0)
        and all(
            residuals[k] <= TOLERANCES["identity_atol"]
            for k in (
                "identity_gram_max_abs",
                "identity_func_max_abs",
                "identity_offset_abs",
            )
        )
        and np.allclose(
            reconstruction,
            S,
            atol=TOLERANCES["reconstruction_atol"],
            rtol=TOLERANCES["reconstruction_rtol"],
        )
        and residuals["dense_relaxed_gap"] < TOLERANCES["dense_opt_atol"]
        and residuals["conjecture_gap"] < TOLERANCES["conjecture_atol"]
        and residuals["minimum_scalar_inequality_dual"] >= -TOLERANCES["dual_tol"]
        and residuals["minimum_S_eigenvalue"] >= -TOLERANCES["psd_tol"]
        and residuals["minimum_matrix_inequality_eigenvalue"] >= -TOLERANCES["psd_tol"]
    )
    numerical_checks = dict(
        tolerances=TOLERANCES,
        residuals=residuals,
        passed=bool(passed),
        identity_components={
            "gram": np.asarray(checked.inner_prod_coords, dtype=float).tolist(),
            "function": np.asarray(checked.func_coords, dtype=float).tolist(),
            "offset": float(checked.offset),
        },
        inventory_complete=True,
        inventory_count=len(entries),
        active_count=len(constraints),
        solver_status=str(problem.status),
    )
    raw_display = result.get_scalar_constraint_dual_value_in_numpy(obj)

    def display(x):
        # Library display uses NaN for omitted multipliers; the authoritative
        # mapping records None. Display zeros mean deliberately dropped entries.
        return dict(
            matrix=np.nan_to_num(np.asarray(x.matrix, dtype=float), nan=0.0).tolist(),
            row_names=list(x.row_names),
            col_names=list(x.col_names),
        )

    if isinstance(raw_display, dict):
        lambda_display = {
            "lambda_groups": {str(k): display(v) for k, v in raw_display.items()}
        }
    else:
        d = display(raw_display)
        lambda_display = dict(
            lambda_matrix=d["matrix"],
            lambda_row_names=d["row_names"],
            lambda_col_names=d["col_names"],
        )
    normalization = dict(
        tau_name="initial_condition",
        initial_condition=b1["initial_condition"],
        performance_metric=b1["performance_metric"],
        bound_value=float(value),
        bound_formula=b1["conjectured_rate"],
        conjectured_value=conjecture,
    )
    provenance = dict(
        solve_id=str(uuid.uuid4()),
        pep_type="primal",
        solver_status=str(problem.status),
        source_hashes=hashes,
        source_scope="Current-run setup/helper and generic pepflow/*.py excluding *_test.py",
        solver=dict(
            api="CVXPrimalSolver.build_problem + cvxpy.Problem.solve",
            cvxpy_version=version("cvxpy"),
            effective_name=problem.solver_stats.solver_name,
            settings=OPTIONS,
            num_iters=problem.solver_stats.num_iters,
        ),
    )
    state = {
        **b1,
        **lambda_display,
        "N": n,
        "opt_value": float(value),
        "tau_sol": tau,
        "tau_name": "initial_condition",
        "relaxed_constraints": list(pb.relaxed_constraints),
        "S_matrix": S.tolist(),
        "S_row_names": list(S_sol.row_names),
        "S_col_names": list(S_sol.col_names),
        "basis_vectors": [str(v) for v in basis],
        "basis_scalars": [str(v) for v in ctx.basis_scalars()],
        "named_dual_values": duals,
        "constraint_metadata": metadata,
        "normalization": normalization,
        "certificate_provenance": provenance,
        "numerical_checks": numerical_checks,
        "numerical_decomposition": decomposition,
        "sparsity_pattern": pattern,
        "closed_form_search": {
            "completed": False,
            "references_reviewed": [],
            "attempts": [],
            "unresolved_components": ["lambda", "S"],
        },
        "formula_status": {"lambda": "unresolved", "S": "unresolved"},
        "lamb_code": None,
        "S_code": None,
        "S_decomp_type": "ldl",
        "numerical_certificate_verified": bool(passed),
        "analytic_full_pep_verified": False,
        "lyapunov_proof_verified": False,
        "require_analytic_full_pep": b1.get("require_analytic_full_pep", False),
        "proof_valid": bool(passed),
        "solver_diagnostics": {
            "max_primal_constraint_violation": max(
                max_abs(c.violation()) for c in problem.constraints
            ),
            "primal_dual_gap": float(tau * float(params["R"] ** 2) - value),
        },
        "reference_policy": "User prohibits other examples/reference history; initial S search uses only current sample before reverse LDL.",
    }
    # The B1 sweep is already stored in its own state; do not replicate it here.
    state.pop("sweep_results", None)
    state["certificate_id"] = hashlib.sha256(
        json.dumps(
            {k: state[k] for k in CERTIFICATE_KEYS},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    for path, expected in hashes.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    print(
        json.dumps(
            {
                "pattern": pattern,
                "residuals": residuals,
                "active": len(constraints),
                "S_rank": decomposition["numerical_rank_at_1e_7"],
                "verified": bool(passed),
            }
        ),
        flush=True,
    )
    return state


def initial_search(state):
    active = {
        name: value
        for name, value in state["named_dual_values"].items()
        if value is not None and state["constraint_metadata"][name]["kind"] == "scalar"
    }
    fractions = {
        name: {
            "value": value,
            "fraction_1000": str(Fraction(value).limit_denominator(1000)),
            "fraction_error": abs(
                value - float(Fraction(value).limit_denominator(1000))
            ),
        }
        for name, value in active.items()
    }
    S = np.asarray(state["S_matrix"])
    n = state["N_verify"]
    # Inspect the displacement-square component by its forced first column.
    tau = state["tau_sol"]
    w = S[:, 0] / tau
    rank_one = tau * np.outer(w, w)
    remainder = S - rank_one
    search = dict(
        completed=True,
        references_reviewed=[],
        reference_policy="No external/previous target material permitted; only current sample and generic workflow/source used.",
        attempts=[
            {
                "component": "lambda",
                "method": "Rational reconstruction of every active scalar with denominator <=1000 at N=4",
                "result": fractions,
                "outcome": "Sample fractions inspected; no all-N formula established from one sample.",
            },
            {
                "component": "S",
                "method": "Numerical rank/eigenvalues and first-column displacement-square extraction",
                "rank_at_1e_7": int(np.linalg.matrix_rank(S, tol=1e-7)),
                "eigenvalues": np.linalg.eigvalsh(S).tolist(),
                "first_column_square_weight": tau,
                "first_column_square_coords": w.tolist(),
                "square_coord_fractions_1000": [
                    str(Fraction(float(x)).limit_denominator(1000)) for x in w
                ],
                "remaining_gram_matrix": remainder.tolist(),
                "remainder_eigenvalues": np.linalg.eigvalsh(
                    (remainder + remainder.T) / 2
                ).tolist(),
                "outcome": "Low-rank guess alone does not reconstruct S; reverse LDL retains all sample factors and verifies reconstruction.",
            },
        ],
        unresolved_components=["lambda", "S"],
        sample_domain={"N": n, "params_json": state["params_json"]},
        analytic_domain_claim="None; initial numerical structure search only.",
    )
    state["closed_form_search"] = search


def main():
    b1, params, module, hashes = load_inputs()
    dense = solve(b1, params, module, hashes, "dense")
    assert dense["numerical_certificate_verified"]
    write(STATE / f"{ALGO}_dense.json", dense)
    threshold = 1e-7
    drop_threshold = [
        name
        for name, value in dense["named_dual_values"].items()
        if dense["constraint_metadata"][name]["origin"] == "interpolation"
        and value is not None
        and abs(value) < threshold
    ]
    threshold_state = solve(
        b1,
        params,
        module,
        hashes,
        "dense_threshold_1e-7",
        drop_threshold,
        dense["opt_value"],
    )
    write(HERE / "block2_threshold.json", threshold_state)
    chain = [f"x_{i}" for i in range(b1["N_verify"])] + [f"y_{b1['N_verify']}"]
    keep_pairs = {(chain[i], chain[i + 1]) for i in range(len(chain) - 1)} | {
        ("x_star", p) for p in chain
    }
    keep = {f"{b1['obj_tag']}:{a},{b}" for a, b in keep_pairs}
    drop_chain = [
        name
        for name, meta in dense["constraint_metadata"].items()
        if meta["origin"] == "interpolation" and name not in keep
    ]
    chain_state = solve(
        b1,
        params,
        module,
        hashes,
        "forward_chain_plus_star",
        drop_chain,
        dense["opt_value"],
    )
    write(HERE / "block2_chain.json", chain_state)
    candidates = [dense, threshold_state, chain_state]
    if not chain_state["numerical_certificate_verified"]:
        keep_pairs |= {(chain[i], chain[i + 2]) for i in range(len(chain) - 2)}
        keep = {f"{b1['obj_tag']}:{a},{b}" for a, b in keep_pairs}
        drop = [
            name
            for name, meta in dense["constraint_metadata"].items()
            if meta["origin"] == "interpolation" and name not in keep
        ]
        expanded = solve(
            b1,
            params,
            module,
            hashes,
            "forward_chain_skip_one_plus_star",
            drop,
            dense["opt_value"],
        )
        write(HERE / "block2_expanded_chain.json", expanded)
        candidates.append(expanded)
    selected = min(
        (s for s in candidates if s["numerical_certificate_verified"]),
        key=lambda s: s["numerical_checks"]["active_count"],
    )
    initial_search(selected)
    selected["sparsity_search"] = {
        "threshold": threshold,
        "attempts": [
            {
                "pattern": s["sparsity_pattern"],
                "opt_value": s["opt_value"],
                "active_count": s["numerical_checks"]["active_count"],
                "dropped_count": len(s["relaxed_constraints"]),
                "preserved": s["numerical_certificate_verified"],
                "certificate_id": s["certificate_id"],
            }
            for s in candidates
        ],
        "selected_pattern": selected["sparsity_pattern"],
    }
    assert (
        selected["numerical_certificate_verified"]
        and selected["closed_form_search"]["completed"]
    )
    for name in (f"{ALGO}_relaxed.json", f"{ALGO}_b2.json"):
        target = STATE / name
        if target.exists():
            previous = json.loads(target.read_text(encoding="utf-8"))
            write(
                HERE
                / f"preserved_{target.stem}_{previous['certificate_id'][:12]}.json",
                previous,
            )
        write(target, selected)
    print("SELECTED", selected["certificate_id"], flush=True)
    print(
        "ACTIVE",
        json.dumps(
            {k: v for k, v in selected["named_dual_values"].items() if v is not None}
        ),
        flush=True,
    )
    print(
        "LDL_DIAGONAL",
        np.diag(selected["numerical_decomposition"]["D"]).tolist(),
        flush=True,
    )


if __name__ == "__main__":
    main()
