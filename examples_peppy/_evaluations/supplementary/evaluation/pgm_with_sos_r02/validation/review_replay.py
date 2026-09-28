import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / "supplementary/helpers"))
import runtime  # ty: ignore[unresolved-import]  # Runtime bootstrap adds the archived helper directory to sys.path.  # noqa: E402 -- Initialize paths and runtime environment before importing.

runtime.configure()
from basis_structure import (  # ty: ignore[unresolved-import]  # Runtime bootstrap adds the archived helper directory to sys.path.  # noqa: E402 -- Initialize paths and runtime environment before importing.
    extract_structure,
)
from certificate import (  # ty: ignore[unresolved-import]  # Runtime bootstrap adds the archived helper directory to sys.path.  # noqa: E402 -- Initialize paths and runtime environment before importing.
    verify,
)
from partial_sums import (  # ty: ignore[unresolved-import]  # Runtime bootstrap adds the archived helper directory to sys.path.  # noqa: E402 -- Initialize paths and runtime environment before importing.
    construct,
)

b2 = json.loads((root / "state/pgm_b2.json").read_text())
dense = json.loads((root / "state/pgm_dense.json").read_text())
checks, *_ = verify(b2, dense["opt_value"], b2["numerical_decomposition"])
result = {"B2": checks}
result["B3"] = {}
for n, cert in [
    (4, b2),
    (6, json.loads((root / "supplementary/b2-n6-certificate.json").read_text())),
]:
    trial = construct(cert, variant="blend-3/10")
    result["B3"][str(n)] = trial["observation"]
    if n == 4:
        _, _, _, errors = extract_structure(trial, n)
        result["B4"] = errors
(root / "replay-results.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
