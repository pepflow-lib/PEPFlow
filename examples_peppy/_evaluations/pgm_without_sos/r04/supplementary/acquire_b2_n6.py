# Notebook/proof state is executed below into the shared runtime namespace.
# These names are supplied by the notebook cells or serialized proof source.
# ty: ignore[unresolved-reference]
# ruff: noqa: F821

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json

import runtime

# Preserve the recorded import initialization order.
# isort: split
import numpy as np  # noqa: F401 -- Required by exec of b2_cells.py.

import pepflow as pf  # noqa: F401 -- Required by exec of b2_cells.py.

# local helper resolved by the notebook runtime path
# Preserve the recorded import initialization order.
# isort: split
from certificates import acquire, file_hash  # ty: ignore[unresolved-import]

notebook_dir = runtime.ATTEMPT
archive = notebook_dir / "supplementary/sample_n6"
archive.mkdir(exist_ok=True)
previous = json.loads((notebook_dir / "state/pgm_b2.json").read_text())
hashes = {
    p: file_hash(notebook_dir / p)
    for p in previous["certificate_provenance"]["source_hashes"]
}
ctx, pb, result, dense = acquire(6)
(archive / "dense.json").write_text(json.dumps(dense, indent=2))
dropped = []
for name, meta in dense["constraint_metadata"].items():
    if meta["origin"] != "interpolation":
        continue
    ri, ci = name.split(":")[1].split(",")
    adjacent = ri != "x_star" and ci != "x_star" and int(ci[2:]) == int(ri[2:]) + 1
    if not (ri == "x_star" or adjacent):
        dropped.append(name)
ctx, pb, result, sample = acquire(6, dropped)
assert all(file_hash(notebook_dir / p) == digest for p, digest in hashes.items())
sample["certificate_provenance"]["source_hashes"] = hashes
(archive / "raw.json").write_text(json.dumps(sample, indent=2))
print("N6 dense/selected statuses:", dense["solver_status"], sample["solver_status"])
source = (notebook_dir / "supplementary/b2_cells.py").read_text(encoding="utf-8-sig")
source = source.replace(
    "'state/pgm_dense.json'", "'supplementary/sample_n6/dense.json'"
).replace("'supplementary/b2-selected-raw.json'", "'supplementary/sample_n6/raw.json'")
(archive / "verification_source.py").write_text(source)
exec(compile(source, "sample_n6/verification_source.py", "exec"))
finalizer = (notebook_dir / "supplementary/finalize_b2.py").read_text(
    encoding="utf-8-sig"
)
state_code = finalizer[finalizer.index("lamb_code =") : finalizer.index("\nnb =")]
state_code = state_code.replace(
    "(notebook_dir / 'state' / filename)", "(archive / filename)"
)
exec(compile(state_code, "sample_n6/state_serialization", "exec"))
(archive / "certificate.json").write_text(json.dumps(state, indent=2))
print("Verified complete additional certificate:", state["certificate_id"])
