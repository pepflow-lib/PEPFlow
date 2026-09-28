import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import runtime

# local helper resolved by the notebook runtime path
from certificates import acquire, file_hash  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
source_paths = [root / "pgm_setup.py", root / "supplementary/helpers/certificates.py"]
allowlist = json.loads((runtime.APPROVED / "allowlist.json").read_text())
source_paths += [
    Path(p)
    for p in allowlist["exact_read_files"]
    if Path(p).parent == runtime.APPROVED / "pepflow"
]
hashes = {str(p.relative_to(root)): file_hash(p) for p in source_paths}
prior = json.loads((root / "supplementary/b2-sparse-first.json").read_text())
ctx, pb, result, selected = acquire(4, prior["relaxed_constraints"])
assert all(file_hash(root / p) == digest for p, digest in hashes.items())
selected["certificate_provenance"]["source_hashes"] = hashes
(root / "supplementary/b2-selected-raw.json").write_text(json.dumps(selected, indent=2))
print(selected["opt_value"], selected["solver_status"])
