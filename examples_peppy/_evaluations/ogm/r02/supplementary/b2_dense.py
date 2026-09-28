"""Acquire the B2 dense certificate."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for key in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]:
    os.environ[key] = "1"
sys.path[:0] = [
    str(ROOT / "supplementary/approved"),
    str(ROOT),
    str(ROOT / "supplementary/helpers"),
]
# local helper resolved by the notebook runtime path
from certificate_tools import (  # noqa: E402  # ty: ignore[unresolved-import]
    acquire,
    summary,
)

horizon = int(sys.argv[1]) if len(sys.argv) > 1 else 6
destination = (
    ROOT / "state" if horizon == 6 else ROOT / "supplementary" / f"horizon_N{horizon}"
)
destination.mkdir(exist_ok=True)
ctx, pb, obj, dense = acquire(horizon)
(destination / "ogm_dense.json").write_text(
    json.dumps(dense, indent=2, allow_nan=False)
)
print(json.dumps(summary(dense), indent=2))
