import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

# local helper resolved by the notebook runtime path
from certificate import capture  # ty: ignore[unresolved-import]

root = runtime.ROOT
folder = root / "supplementary/certificate-n6"
folder.mkdir(exist_ok=True)
dense6 = capture(6)
(folder / "pgm_dense.json").write_text(json.dumps(dense6, indent=2))
print(
    "Dense6",
    dense6["opt_value"],
    dense6["certificate_provenance"]["solver_status"],
    flush=True,
)
relaxed = []
for name, meta in dense6["constraint_metadata"].items():
    if meta["origin"] == "initial":
        continue
    first, second = name.split(":")[1].split(",")
    keep = first == "x_star" or (
        second != "x_star" and int(second[2:]) == int(first[2:]) + 1
    )
    if not keep:
        relaxed.append(name)
selected6 = capture(6, relaxed)
(folder / "selected-raw.json").write_text(json.dumps(selected6, indent=2))
print(
    "Selected6",
    selected6["opt_value"],
    selected6["certificate_provenance"]["solver_status"],
    flush=True,
)
