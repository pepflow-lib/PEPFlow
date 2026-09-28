import hashlib
import json
from pathlib import Path

root = Path.cwd()
review = json.loads((root.parent / "review.json").read_text())
settings = json.loads((root.parent / "settings.json").read_text())
campaign = root.parents[3]
refs = review["final_evidence_refs"] + [review["notebook_path"]]
for b in review["blocks"]:
    refs += b["evidence_refs"] + [c["evidence_ref"] for c in b["checks"]]
missing = [r for r in refs if not (campaign / r.split("#")[0]).is_file()]
assert not missing, missing
original = Path(settings["original_submission"])
assert all(
    hashlib.sha256((original / p).read_bytes()).hexdigest() == h
    for p, h in settings["submission_hashes"].items()
)
print(
    "Review JSON parsed; all evidence paths exist; all 178 original artifact hashes remain unchanged."
)
