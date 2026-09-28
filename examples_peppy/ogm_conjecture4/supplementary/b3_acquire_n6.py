"""Acquire exactly one fresh N=6 star-and-forward-chain numerical capture.

The existing B1/B2 states, setup, and notebook are read-only. This capture is
not an independently verified certificate; downstream checks are required.
"""

import hashlib
import json
import sys
import traceback
from pathlib import Path

sys.dont_write_bytecode = True
# Imports follow repository-path and runtime setup.
import run_block2 as run  # noqa: E402

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "b3_N6_capture.json"
FAILURE = HERE / "b3_N6_failure.json"
COMMAND = (
    ".venv/Scripts/python.exe -B "
    "examples_peppy/ogm_conjecture4_test_20260916_2am/"
    "supplementary/b3_acquire_n6.py"
)


def main():
    assert not OUTPUT.exists(), "Refuse to overwrite an existing fresh capture"
    assert not FAILURE.exists(), "Previous acquisition failed; do not retry"
    run.N = 6
    assert run.SETTINGS == {
        "solver": "CLARABEL",
        "tol_gap_abs": 1e-8,
        "tol_gap_rel": 1e-8,
        "tol_feas": 1e-8,
        "max_iter": 300,
    }
    b2_path = run.STATE / f"{run.NAME}_b2.json"
    b2 = json.loads(b2_path.read_text(encoding="utf-8"))
    assert b2["N"] == b2["N_verify"] == 4

    # This fresh inventory, not any N=4 name list, supplies the complement.
    inventory_ctx, inventory_pb, _ = run.mod.get_pep_setup(run.sp.S(run.N), run.PARAMS)
    entries = run.inventory(inventory_ctx, inventory_pb)
    interpolation_names = {
        c.name for c, origin, _, _ in entries if origin == "interpolation"
    }
    points = [f"x_{i}" for i in range(run.N)] + [f"y_{run.N}"]
    star = {f"f:x_star,{point}" for point in points}
    chain = {f"f:{left},{right}" for left, right in zip(points, points[1:])}
    keep = star | chain
    assert len(interpolation_names) == 56 and len(keep) == 13
    assert keep.issubset(interpolation_names)
    relaxed = [
        c.name
        for c, origin, _, _ in entries
        if origin == "interpolation" and c.name not in keep
    ]
    assert len(relaxed) == 43 and set(relaxed) == interpolation_names - keep

    # This is the only acquire/solve invocation in this wrapper.
    captured = run.acquire(relaxed, "star_chain_N6_fresh")
    data = captured[-1]
    data["certificate_provenance"]["source_hashes"][
        Path(__file__).relative_to(run.ROOT).as_posix()
    ] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    bound = float(run.mod.conjectured_rate(run.N))
    dense = next(row for row in run.B1["sweep_results"] if row["N"] == run.N)
    bound_relative_error = abs(data["opt_value"] / bound - 1.0)
    dense_gap = abs(data["opt_value"] - dense["opt_value"])
    data["acquisition_checks"] = {
        "solver_status": data["certificate_provenance"]["solver_status"],
        "prompt_bound_value": bound,
        "prompt_bound_relative_error": bound_relative_error,
        "existing_B1_dense_N6_value": dense["opt_value"],
        "absolute_gap_to_existing_B1_dense_N6": dense_gap,
        "bound_match_relative_tolerance": 1e-5,
        "dense_match_absolute_tolerance": 1e-7,
        "objective_matches": bound_relative_error < 1e-5 and dense_gap < 1e-7,
        "independent_full_identity_verification_complete": False,
    }
    data["sparsity_search"] = {
        "selected_support": "star_chain",
        "kept": sorted(keep),
        "kept_interpolation_count": len(keep),
        "dropped_interpolation_count": len(relaxed),
        "support_source": "Generalized current-run N=4 star-chain support",
        "relaxation_name_source": "Fresh get_pep_setup(N=6) interpolation inventory",
        "number_of_fresh_solves": 1,
    }
    data["closed_form_search"] = {
        "completed_for_fresh_capture": False,
        "reusable_current_run_source": b2_path.relative_to(run.ROOT).as_posix(),
        "reusable_current_run_source_sha256": hashlib.sha256(
            b2_path.read_bytes()
        ).hexdigest(),
        "source_N": 4,
        "note": (
            "The current-run N=4 algebraic closed-form search remains reusable. "
            "Its N=6 candidates have not yet been compared with this fresh capture. "
            "No exact or all-N certificate claim is made by this acquisition."
        ),
    }
    data["acquisition_audit"] = {
        "command": COMMAND,
        "wrapper": Path(__file__).relative_to(run.ROOT).as_posix(),
        "output": OUTPUT.relative_to(run.ROOT).as_posix(),
        "scope": "Current-run artifacts and generic pepflow source only",
        "existing_artifacts_mutated": [],
        "fresh_solve_count": 1,
    }
    run.save(OUTPUT, data)
    print(json.dumps(data["acquisition_checks"], indent=2), flush=True)
    print("CAPTURE", OUTPUT.relative_to(run.ROOT).as_posix(), flush=True)
    print("CAPTURE_SHA256", hashlib.sha256(OUTPUT.read_bytes()).hexdigest(), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        if not OUTPUT.exists() and not FAILURE.exists():
            run.save(
                FAILURE,
                {
                    "N": 6,
                    "command": COMMAND,
                    "error": repr(error),
                    "traceback": traceback.format_exc(),
                    "retry_performed": False,
                },
            )
        raise
