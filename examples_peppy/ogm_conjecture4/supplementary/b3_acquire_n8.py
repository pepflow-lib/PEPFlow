"""Acquire one dense and one star/forward-chain capture at N=8.

The captures preserve raw numerical outputs. Independent certificate checks
and comparison with algebraic candidates belong to the downstream verifier.
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
DENSE_OUTPUT = HERE / "b3_N8_dense_capture.json"
SPARSE_OUTPUT = HERE / "b3_N8_capture.json"
FAILURE = HERE / "b3_N8_failure.json"
COMMAND = (
    ".venv/Scripts/python.exe -B "
    "examples_peppy/ogm_conjecture4_test_20260916_2am/"
    "supplementary/b3_acquire_n8.py"
)


def decorate(data, output, solve_number):
    wrapper = Path(__file__).relative_to(run.ROOT).as_posix()
    data["certificate_provenance"]["source_hashes"][wrapper] = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()
    bound = float(run.mod.conjectured_rate(run.N))
    data["acquisition_checks"] = {
        "solver_status": data["certificate_provenance"]["solver_status"],
        "prompt_bound_value": bound,
        "prompt_bound_relative_error": abs(data["opt_value"] / bound - 1.0),
        "bound_match_relative_tolerance": 1e-5,
        "independent_full_identity_verification_complete": False,
    }
    data["acquisition_audit"] = {
        "command": COMMAND,
        "wrapper": wrapper,
        "output": output.relative_to(run.ROOT).as_posix(),
        "scope": "Current-run artifacts and generic pepflow source only",
        "existing_artifacts_mutated": [],
        "solve_number_in_wrapper": solve_number,
        "maximum_fresh_solve_count": 2,
    }


def main():
    assert not any(path.exists() for path in (DENSE_OUTPUT, SPARSE_OUTPUT, FAILURE)), (
        "Refuse to overwrite or retry any existing N=8 acquisition"
    )
    run.N = 8
    assert run.SETTINGS == {
        "solver": "CLARABEL",
        "tol_gap_abs": 1e-8,
        "tol_gap_rel": 1e-8,
        "tol_feas": 1e-8,
        "max_iter": 300,
    }

    # First and only dense solve. A non-optimal status raises inside acquire;
    # the sparse solve is never attempted after such a failure.
    dense_capture = run.acquire([], "dense_N8_fresh")
    dense_data = dense_capture[-1]
    decorate(dense_data, DENSE_OUTPUT, 1)
    run.save(DENSE_OUTPUT, dense_data)
    print(
        "DENSE", dense_data["opt_value"], dense_data["acquisition_checks"], flush=True
    )

    # The successful fresh dense context supplies every interpolation name.
    entries = dense_capture[4]
    interpolation_names = {
        c.name for c, origin, _, _ in entries if origin == "interpolation"
    }
    points = [f"x_{i}" for i in range(run.N)] + [f"y_{run.N}"]
    star = {f"f:x_star,{point}" for point in points}
    chain = {f"f:{left},{right}" for left, right in zip(points, points[1:])}
    keep = star | chain
    assert len(interpolation_names) == 90 and len(keep) == 17
    assert keep.issubset(interpolation_names)
    relaxed = [
        c.name
        for c, origin, _, _ in entries
        if origin == "interpolation" and c.name not in keep
    ]
    assert len(relaxed) == 73 and set(relaxed) == interpolation_names - keep

    # Second and final solve. No retries or alternative supports are attempted.
    sparse_capture = run.acquire(relaxed, "star_chain_N8_fresh")
    sparse_data = sparse_capture[-1]
    decorate(sparse_data, SPARSE_OUTPUT, 2)
    sparse_data["dense_reference_value"] = dense_data["opt_value"]
    sparse_data["dense_reference_capture"] = DENSE_OUTPUT.relative_to(
        run.ROOT
    ).as_posix()
    sparse_data["dense_reference_capture_sha256"] = hashlib.sha256(
        DENSE_OUTPUT.read_bytes()
    ).hexdigest()
    dense_gap = abs(sparse_data["opt_value"] - dense_data["opt_value"])
    sparse_data["acquisition_checks"].update(
        {
            "fresh_dense_N8_value": dense_data["opt_value"],
            "absolute_gap_to_fresh_dense_N8": dense_gap,
            "dense_match_absolute_tolerance": 1e-7,
            "objective_matches": (
                sparse_data["acquisition_checks"]["prompt_bound_relative_error"] < 1e-5
                and dense_gap < 1e-7
            ),
        }
    )
    sparse_data["sparsity_search"] = {
        "selected_support": "star_chain",
        "kept": sorted(keep),
        "kept_interpolation_count": len(keep),
        "dropped_interpolation_count": len(relaxed),
        "support_source": "Generalized current-run star-chain support",
        "relaxation_name_source": "Fresh N=8 dense interpolation inventory",
        "number_of_fresh_sparse_solves": 1,
    }
    sparse_data["closed_form_search"] = {
        "completed_for_fresh_capture": False,
        "note": (
            "The current-run N=4 algebraic closed-form search remains reusable. "
            "Its N=8 candidates have not yet been compared with this fresh capture. "
            "No exact or all-N certificate claim is made by this acquisition."
        ),
    }
    run.save(SPARSE_OUTPUT, sparse_data)
    print("SPARSE", sparse_data["opt_value"], flush=True)
    print(json.dumps(sparse_data["acquisition_checks"], indent=2), flush=True)
    for output in (DENSE_OUTPUT, SPARSE_OUTPUT):
        print("CAPTURE", output.relative_to(run.ROOT).as_posix(), flush=True)
        print(
            "CAPTURE_SHA256",
            hashlib.sha256(output.read_bytes()).hexdigest(),
            flush=True,
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        if not FAILURE.exists():
            run.save(
                FAILURE,
                {
                    "N": 8,
                    "command": COMMAND,
                    "error": repr(error),
                    "traceback": traceback.format_exc(),
                    "retry_performed": False,
                    "dense_capture_exists": DENSE_OUTPUT.exists(),
                    "sparse_capture_exists": SPARSE_OUTPUT.exists(),
                },
            )
        raise
