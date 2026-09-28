"""Test structured supports using only this run's fresh dense certificate."""

import hashlib
import json
from pathlib import Path

import run_block2 as run

HERE = Path(__file__).resolve().parent
dense = json.loads((run.STATE / f"{run.NAME}_dense.json").read_text())
threshold_capture = json.loads((HERE / "b2_selected_capture.json").read_text())
run.save(HERE / "b2_threshold_capture.json", threshold_capture)
points = [f"x_{i}" for i in range(run.N)] + [f"y_{run.N}"]
chain = {f"f:{a},{b}" for a, b in zip(points, points[1:])}
star = {f"f:x_star,{p}" for p in points}
forward_terminal = {f"f:{p},{points[-1]}" for p in points[:-1]}
backward_terminal = {f"f:{points[-1]},{p}" for p in points[:-1]}
patterns = [
    ("star_chain", star | chain),
    ("star_chain_terminal", star | chain | forward_terminal | backward_terminal),
]
attempts = []
selected = None
for label, keep in patterns:
    relaxed = [
        name
        for name, meta in dense["constraint_metadata"].items()
        if meta["origin"] == "interpolation" and name not in keep
    ]
    captured = run.acquire(relaxed, label)
    data = captured[-1]
    gap = abs(data["opt_value"] - dense["opt_value"])
    error = abs(data["opt_value"] / float(run.mod.conjectured_rate(run.N)) - 1)
    preserved = gap < 1e-7 and error < 1e-5
    attempts.append(
        dict(
            label=label,
            kept=sorted(keep),
            dropped=len(relaxed),
            opt_value=data["opt_value"],
            dense_gap=gap,
            conjecture_relative_error=error,
            preserved=preserved,
        )
    )
    run.save(HERE / f"b2_{label}_capture.json", data)
    print(label, attempts[-1], flush=True)
    if preserved:
        selected = data
        break
assert selected is not None, "Neither structured support preserved the rate"
selected["sparsity_search"] = dict(
    threshold=1e-6,
    threshold_dropped_count=len(threshold_capture["relaxed_constraints"]),
    attempts=attempts,
    selected_support=selected["label"],
    dense_value=dense["opt_value"],
)
selected["certificate_provenance"]["source_hashes"][
    Path(__file__).relative_to(run.ROOT).as_posix()
] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
run.save(HERE / "b2_selected_capture.json", selected)
for name, value in selected["named_dual_values"].items():
    if value is not None:
        print(name, value)
print("BASIS", selected["basis_vectors"])
print("S", selected["S_matrix"])
