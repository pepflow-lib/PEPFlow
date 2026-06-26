#!/usr/bin/env python3
"""
PEPFlow Analysis Runner.

Called by the /pep-analyze workflow to solve PEP problems from the command line
and return structured JSON output for Claude to interpret.

Usage:
    # Single N (full dual variable data):
    python -m pepflow.pep_runner \\
        --module examples/{ALGO_NAME}/{ALGO_NAME}_setup.py \\
        --N 4 \\
        --params '{"L": 1, "R": 1}' \\
        [--relaxed '["f:x_0,x_2", "f:x_1,x_3"]'] \\
        [--tau-name initial_condition] \\
        [--output results.json]

    # Sweep over a range of N in one process (faster than a bash loop):
    python -m pepflow.pep_runner \\
        --module examples/{ALGO_NAME}/{ALGO_NAME}_setup.py \\
        --sweep 1:8 \\
        --params '{"L": 1, "R": 1}'
    # Output: {"sweep": "1:8", "results": [{N:1, opt_value:...}, ...]}

    # Exact fractions via string params:
    --params '{"L": 1, "R": 1, "beta": "1/3"}'

The algorithm setup module at --module must define:

    def get_pep_setup(
        N,       # int or sp.Integer
        params,  # dict[str, sp.Basic]  (sympy values — exact arithmetic)
    ) -> tuple[pf.PEPContext, pf.PEPBuilder, pf.Function | pf.Operator]:
        ...

    where the returned PEPBuilder already has:
        - initial_condition added via pb.add_initial_constraint(..., name=TAU_NAME)
          (TAU_NAME defaults to "initial_condition"; pass --tau-name to change it)
        - performance metric set via pb.set_performance_metric(...)

    Use ctx_name=f"ctx_{N}" so repeated calls with different N values stay isolated.
    This is required for --sweep mode, which runs all N values in the same process.

Parameter precision:
    String values in --params are parsed as exact sympy Rationals:
        "1/3" → Rational(1, 3)    "2" → Integer(2)
    Float values are rationalized via nsimplify (tolerance 1e-9):
        0.3333333333 → Rational(1, 3)
    Integer values are passed as sympy Integers.
    For clean closed-form work, prefer string fractions: '{"beta": "1/3"}'.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def _load_setup_module(path: str):
    abs_path = str(Path(path).resolve())
    spec = importlib.util.spec_from_file_location("_pepflow_setup", abs_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {abs_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _parse_param(v):
    """Convert a JSON value to a sympy number with exact arithmetic where possible.

    str  → sp.Rational(v)                         e.g. "1/3" → Rational(1,3)
    float → sp.nsimplify(v, rational=True, ...)   e.g. 0.333... → Rational(1,3)
    int  → sp.S(v)                                e.g. 1 → Integer(1)
    """
    import sympy as sp

    if isinstance(v, str):
        return sp.Rational(v)
    if isinstance(v, float):
        return sp.nsimplify(v, rational=True, tolerance=1e-9)
    return sp.S(v)


def _to_serializable(x) -> float | str:
    try:
        return float(x)
    except (TypeError, ValueError):
        return str(x)


def _serialize_matrix_with_names(m):
    return {
        "matrix": [[_to_serializable(v) for v in row] for row in m.matrix.tolist()],
        "row_names": list(m.row_names),
        "col_names": list(m.col_names),
    }


def run(
    module_path: str,
    N: int,
    params: dict[str, int | float | str],
    relaxed: list[str] | None = None,
    tau_name: str = "initial_condition",
) -> dict[str, Any]:
    """Solve a PEP for a single N and return dual variable data as a plain dict.

    All param values are converted to sympy for exact arithmetic via _parse_param.
    The output dict is JSON-serializable (floats and strings only).
    tau_name is the constraint name used to extract tau_sol from the dual.
    """
    import sympy as sp

    mod = _load_setup_module(module_path)
    if not hasattr(mod, "get_pep_setup"):
        raise AttributeError(
            f"{module_path} must define get_pep_setup(N, params) -> (ctx, pb, obj)"
        )

    N_sp = sp.S(N)
    params_sp = {k: _parse_param(v) for k, v in params.items()}

    ctx, pb, obj = mod.get_pep_setup(N_sp, params_sp)

    if relaxed:
        pb.set_relaxed_constraints(relaxed)

    result = pb.solve(resolve_parameters=params_sp)

    lamb_sol = result.get_scalar_constraint_dual_value_in_numpy(obj)
    S_sol = result.get_gram_dual_matrix()
    tau_sol = result.dual_var_manager.dual_value(tau_name)

    output: dict[str, Any] = {
        "N": N,
        "opt_value": _to_serializable(result.opt_value),
        "tau_sol": _to_serializable(tau_sol) if tau_sol is not None else None,
        "S_matrix": [
            [_to_serializable(v) for v in row] for row in S_sol.matrix.tolist()
        ],
        "S_row_names": list(S_sol.row_names),
        "S_col_names": list(S_sol.col_names),
        "basis_vectors": [str(v) for v in ctx.basis_vectors()],
    }
    if isinstance(lamb_sol, dict):
        output["lambda_groups"] = {
            name: _serialize_matrix_with_names(matrix)
            for name, matrix in lamb_sol.items()
        }
    else:
        serialized_lambda = _serialize_matrix_with_names(lamb_sol)
        output["lambda_matrix"] = serialized_lambda["matrix"]
        output["lambda_row_names"] = serialized_lambda["row_names"]
        output["lambda_col_names"] = serialized_lambda["col_names"]
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Solve a PEP and write dual variable data as JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--module", required=True, help="Path to the algorithm setup module"
    )
    parser.add_argument(
        "--N", type=int, default=4, help="Number of iterations (single-N mode)"
    )
    parser.add_argument(
        "--sweep",
        type=str,
        default=None,
        help="Range of N to solve in one process, e.g. '1:8' solves N=1..7. "
        "Output includes a 'results' array. Requires ctx_name=f'ctx_{N}' "
        "in the setup module to avoid registry conflicts.",
    )
    parser.add_argument(
        "--params",
        type=str,
        default="{}",
        help="JSON object of parameter values. Use strings for exact fractions: "
        '\'{"L": 1, "R": 1, "beta": "1/3"}\'',
    )
    parser.add_argument(
        "--relaxed",
        type=str,
        default=None,
        help="JSON array of constraint names to relax, e.g. '[\"f:x_0,x_2\"]'",
    )
    parser.add_argument(
        "--tau-name",
        type=str,
        default="initial_condition",
        dest="tau_name",
        help="Name of the initial condition constraint used to extract tau_sol "
        "(default: 'initial_condition'). Change this if your setup module "
        "uses a different name, e.g. --tau-name 'init'.",
    )
    parser.add_argument(
        "--output", type=str, default=None, help="Write JSON output to this file"
    )
    args = parser.parse_args()

    params = json.loads(args.params)
    relaxed = json.loads(args.relaxed) if args.relaxed else None

    if args.sweep:
        lo, hi = (int(x) for x in args.sweep.split(":"))
        results = [
            run(args.module, k, params, relaxed, args.tau_name) for k in range(lo, hi)
        ]
        output: dict = {"sweep": args.sweep, "results": results}
    else:
        output = run(args.module, args.N, params, relaxed, args.tau_name)

    out_str = json.dumps(output, indent=2)

    if args.output:
        Path(args.output).write_text(out_str)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(out_str)


if __name__ == "__main__":
    main()
