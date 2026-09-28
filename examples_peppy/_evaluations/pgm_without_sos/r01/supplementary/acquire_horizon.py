"""B2-only acquisition for the horizon requested by B3."""
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path[:0] = [str(root / "supplementary/approved"), str(root / "supplementary/h"), str(root)]
    from runtime import configure
    configure()
    import numpy as np
    import sympy as sp
    from certificate import capture, inventory, certificate_id
    from pgm_setup import get_pep_setup
    previous = json.loads((root / "state/pgm_b2.json").read_text())
    request = json.loads((root / "supplementary/b3-recovery-request.json").read_text(encoding="utf-8-sig"))
    N = request["requested_horizon"]
    params = json.loads(previous["params_json"])
    hashes = previous["certificate_provenance"]["source_hashes"]
    for path, expected in hashes.items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected
    ctx, pb, obj = get_pep_setup(N, params)
    dense = capture(ctx, pb, obj, params)
    (root / f"supplementary/b2_n{N}_dense.json").write_text(json.dumps(dense, indent=2))
    print("Dense status / bound:", dense["certificate_provenance"]["solver_status"], dense["opt_value"])
    ctx, pb, obj = get_pep_setup(N, params)
    dropped = []
    for c, origin, _, _ in inventory(ctx, pb):
        if origin == "initial":
            continue
        first, second = c.name.split(":")[1].split(",")
        keep = first == "x_star"
        if first != "x_star" and second != "x_star":
            keep = int(second[2:]) == int(first[2:]) + 1
        if not keep:
            dropped.append(c.name)
    pb.set_relaxed_constraints(dropped)
    selected = capture(ctx, pb, obj, params, dense["opt_value"])
    state: dict[str, Any] = {**previous, **selected, "N": N, "N_verify": N}
    state["certificate_provenance"]["source_hashes"] = hashes
    state["normalization"] = {**previous["normalization"], "bound_value": selected["opt_value"]}
    state["numerical_certificate_verified"] = selected["numerical_checks"]["passed"]
    state["proof_valid"] = state["numerical_certificate_verified"]
    namespace: dict[str, Any] = {"sp": sp}
    exec(previous["lamb_code"], namespace)
    candidate = namespace["candidate_multiplier"]
    error = max(abs(float(candidate(name, N))-value)
                for name, value in selected["named_dual_values"].items() if value is not None)
    state["closed_form_search"] = {
        **previous["closed_form_search"],
        "reused_from_certificate": previous["certificate_id"],
        "additional_horizon_lambda_error": error,
        "additional_horizon_formula_status": "candidate" if error < 1e-4 else "unresolved",
    }
    state["formula_status"] = {"lambda": "candidate" if error < 1e-4 else "unresolved", "S": "unresolved"}
    state["S_code"] = None
    state["certificate_id"] = certificate_id(state)
    for path, expected in hashes.items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected
    assert np.isfinite(selected["opt_value"])
    (root / f"supplementary/b2_n{N}.json").write_text(json.dumps(state, indent=2))
    print(json.dumps(selected["numerical_checks"], indent=2))
    print("Candidate multiplier error:", error)
    print("Certificate:", state["certificate_id"])
    assert state["numerical_certificate_verified"]


if __name__ == "__main__":
    main()
