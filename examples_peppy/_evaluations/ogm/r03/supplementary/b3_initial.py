import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
sys.path[:0] = [
    str(ROOT / "supplementary" / "approved"),
    str(ROOT),
    str(ROOT / "supplementary" / "helpers"),
]
# local helper resolved by the notebook runtime path
from partial_sums import (  # noqa: E402  # ty: ignore[unresolved-import]
    build_partial_sums,
)

certificate = json.loads((ROOT / "state" / "ogm_b2.json").read_text())
observation, coordinates, coverage = build_partial_sums(certificate, ROOT)
(ROOT / "supplementary" / "b3-N4-observation.json").write_text(
    json.dumps(
        dict(observation=observation, coordinates=coordinates, coverage=coverage),
        indent=2,
    )
)
print(json.dumps(observation))
