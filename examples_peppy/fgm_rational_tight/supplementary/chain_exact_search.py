"""De novo finite-horizon chain/star candidate search (no SDP solves)."""

import json
import sys
from pathlib import Path

import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

# Imports follow repository-path and runtime setup.
import pepflow as pf  # noqa: E402
from pepflow.pep_runner import _load_setup_module  # noqa: E402


def chain_candidate(n):
    mod = _load_setup_module(str(HERE.parent / "fgm_rational_test_setup.py"))
    ctx, pb, obj = mod.get_pep_setup(sp.Integer(n), {"L": sp.S.One, "R": sp.S.One})
    constraints = {c.name: c for c in obj.get_interpolation_constraints(ctx)}
    pm = pf.ExpressionManager(ctx, resolve_parameters={"L": sp.S.One, "R": sp.S.One})
    basis = ctx.basis_vectors()
    labels = [str(v) for v in basis]
    points = [f"x_{i}" for i in range(n)] + ["x_1" if n == 1 else f"y_{n}"]
    tau = sp.Rational(2, (n + 2) * (n + 3))
    a = sp.symbols(f"a0:{n}")
    b = [a[0]] + [a[i] - a[i - 1] for i in range(1, n)] + [1 - a[-1]]
    weighted = tau * (pb.init_conditions[0].lhs - pb.init_conditions[0].rhs)
    multipliers = {}
    for i in range(n):
        name = f"f:{points[i]},{points[i + 1]}"
        multipliers[name] = a[i]
    for i in range(n + 1):
        multipliers[f"f:x_star,{points[i]}"] = b[i]
    evaluation = pm.eval_scalar(weighted - pb.performance_metric + tau, sympy_mode=True)
    gram = sp.Matrix(evaluation.inner_prod_coords)
    func = sp.Matrix(evaluation.func_coords)
    offset = evaluation.offset
    for name, coef in multipliers.items():
        c = constraints[name]
        term = pm.eval_scalar(c.lhs - c.rhs, sympy_mode=True)
        gram += coef * sp.Matrix(term.inner_prod_coords)
        func += coef * sp.Matrix(term.func_coords)
        offset += coef * term.offset
    assert not gram.atoms(sp.Float)
    assert func.applyfunc(sp.simplify).is_zero_matrix
    assert sp.simplify(offset) == 0
    # A candidate kernel motivated by equal gradients; feasibility is tested below,
    # not assumed from this ansatz.
    q = sp.Matrix(
        [
            sp.S.One if name == "x_0" else sp.S.Zero if name == "x_star" else 2 * tau
            for name in labels
        ]
    )
    solutions = sp.solve(list(gram * q), a, dict=True)
    if len(solutions) != 1 or any(v.free_symbols for v in solutions[0].values()):
        return {
            "N": n,
            "status": "no_unique_rational_candidate",
            "solutions": str(solutions),
        }
    solution = solutions[0]
    matrix = gram.subs(solution).applyfunc(sp.factor)
    multipliers = {
        name: sp.factor(value.subs(solution)) for name, value in multipliers.items()
    }
    # Translation creates the x_star redundancy. Delete it and use exact LDL of
    # the gradient block after the x0 pivot; retain zero pivots explicitly.
    idx = [i for i, name in enumerate(labels) if name != "x_star"]
    reduced = matrix.extract(idx, idx)
    residual = reduced.copy()
    pivots = []
    factor_rows = []
    exact_psd = True
    for j in range(residual.rows):
        pivot = sp.factor(residual[j, j])
        pivots.append(pivot)
        if pivot < 0:
            exact_psd = False
            break
        if pivot == 0:
            if any(residual[j, k] != 0 for k in range(residual.cols)):
                exact_psd = False
                break
            factor_rows.append(sp.zeros(1, residual.cols))
            continue
        row = residual[j, :] / pivot
        factor_rows.append(row)
        residual = (residual - pivot * row.T * row).applyfunc(sp.factor)
    nonnegative = all(v >= 0 for v in multipliers.values())
    out = {
        "N": n,
        "tau": str(tau),
        "a": [str(solution[x]) for x in a],
        "b": [str(sp.factor(x.subs(solution))) for x in b],
        "multipliers": {name: str(v) for name, v in multipliers.items()},
        "basis_labels": labels,
        "S_exact": [[str(x) for x in row] for row in matrix.tolist()],
        "min_eigenvalue_diagnostic": float(
            np.linalg.eigvalsh(np.asarray(matrix, dtype=float))[0]
        ),
        "exact_reduced_pivots": [str(x) for x in pivots],
        "multipliers_nonnegative": bool(nonnegative),
        "exact_psd": bool(exact_psd),
        "kernel_identity_zero": bool((matrix * q).is_zero_matrix),
        "status": "finite_horizon_exact_candidate"
        if nonnegative and exact_psd
        else "rejected",
        "scope": "This is a finite-N calculation; no all-horizon sign theorem is established.",
    }
    return out


if __name__ == "__main__":
    records = []
    for n in range(1, 7):
        record = chain_candidate(n)
        records.append(record)
        print(
            {
                k: v
                for k, v in record.items()
                if k in ("N", "status", "a", "b", "exact_reduced_pivots")
            },
            flush=True,
        )
    (HERE / "chain_exact_search.json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )
