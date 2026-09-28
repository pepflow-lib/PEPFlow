import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import unquote

from peppy_astra_prepare_review import (  # ty: ignore[unresolved-import]  # Historical controller imports its sibling helper from the original tmp directory.
    digest,
    fs_path,
    read,
    require,
)

root = Path(__file__).resolve().parents[1]
p = Path((root / "tmp/current_peppy_posthoc.txt").read_text())
s = read(p / "settings.json")
c = Path(s["campaign"])
inventory = read(p / "original-inventory.json")
changed = [
    name
    for name, sha in inventory.items()
    if not fs_path(c / name).is_file() or digest(c / name) != sha
]
require(
    changed == ["results.md"] or set(changed) == {"results.md"},
    f"Unexpected historical changes: {changed}",
)
require(
    digest(p / "original-summary/results.md") == inventory["results.md"],
    "Original summary lost",
)
a = read(p / "assessment.json")
require(len(a["attempts"]) == 30 and len(a["blocks"]) == 150, "Incomplete assessment")
require(len({r["attempt_id"] for r in a["attempts"]}) == 30, "Duplicate attempt")
require(len(a["additional_verification_costs"]) == 2, "Wrong verification count")
links = 0
for f in [c / "results.md", p / "report.md", p / "bppm_r02-adjudication.md"]:
    for target in re.findall(r"\]\(([^\n]+?)\)", f.read_text(encoding="utf-8")):
        path = (f.parent / unquote(target.partition("#")[0])).resolve()
        require(
            path.is_relative_to(c) and fs_path(path).is_file(),
            f"Broken report link: {target}",
        )
        links += 1
evidence = 0
for aid in s["fresh_reviews"]:
    r = read(p / aid / "review.json")
    require(
        digest(p / aid / "review.json") == s["reviews"][aid]["review_sha256"],
        "Review changed",
    )
    refs = []

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {
                    "evidence_ref",
                    "evidence_refs",
                    "mathematical_evidence_refs",
                    "execution_adjustments",
                    "evidence",
                }:
                    if isinstance(item, str):
                        refs.append(item)
                    elif isinstance(item, list):
                        refs.extend(x for x in item if isinstance(x, str))
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(r)
    for ref in refs:
        target = Path(ref.partition("#")[0])
        target = (target if target.is_absolute() else p / aid / target).resolve()
        require(fs_path(target).is_file(), f"Missing evidence: {ref}")
        require(
            target.is_relative_to((p / aid).resolve())
            or target.is_relative_to(
                Path(s["reviews"][aid]["original_submission"]).resolve()
            ),
            "Evidence out of scope",
        )
        evidence += 1
    h = read(p / "host" / ("ph_" + aid + ".json"))
    require(
        all(
            t["model"] == "gpt-6-astra" and t["effort"] == "medium" for t in h["turns"]
        ),
        "Model mismatch",
    )
cost = a["additional_verification_costs"]
result = {
    "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "status": "passed",
    "historical_files_verified": len(inventory),
    "only_updated_historical_file": "results.md",
    "original_summary_preserved": True,
    "attempts": 30,
    "blocks": 150,
    "report_links_checked": links,
    "new_review_evidence_refs_checked": evidence,
    "original_proofs_reviews_cost_records_unchanged": True,
    "additional_verification_tokens": sum(r["tokens_total"] for r in cost),
    "additional_worker_minutes": sum(r["wall_seconds"] for r in cost) / 60,
    "additional_controller_cost": "Separate partial observation in costs.json",
}
(p / "final-validation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
