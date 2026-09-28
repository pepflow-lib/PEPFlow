import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

from bppm_setup import get_pep_setup

# local helper resolved by the notebook runtime path
from partial_sums import (  # ty: ignore[unresolved-import]
    construct_partial_sums,
    replay_certificate,
)

# local helper resolved by the notebook runtime path
from runtime import ATTEMPT  # ty: ignore[unresolved-import]

certificate = json.loads((ATTEMPT / "state/bppm_b2.json").read_text())
ctx, pb, obj = get_pep_setup(certificate["N_verify"], {})
pb.set_relaxed_constraints(certificate["relaxed_constraints"])
checks = replay_certificate(ctx, pb, certificate, ATTEMPT)
lyap, observation = construct_partial_sums(ctx, pb, certificate)
(ATTEMPT / "supplementary/b3-N4-observation.json").write_text(
    json.dumps(observation, indent=2)
)
print("Full-coordinate grouping checks:", observation["coordinate_errors"])
print(
    "Minimum significant singular value:",
    observation["minimum_significant_singular_value"],
)
print(
    "Maximum negligible singular value:",
    observation["maximum_negligible_singular_value"],
)
