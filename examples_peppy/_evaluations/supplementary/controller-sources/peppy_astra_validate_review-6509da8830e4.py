"""Mechanical review validation only; does not adjudicate mathematical claims."""

import json
import sys
from pathlib import Path

from peppy_astra_prepare_review import (  # ty: ignore[unresolved-import]  # Historical controller imports its sibling helper from the original tmp directory.
    fs_path,
    parse,
    read,
    require,
    verify_submission,
)

root = Path(__file__).resolve().parents[1]
campaign = Path(
    (root / "tmp/current_peppy_astra_medium_6x5_campaign.txt").read_text().strip()
).resolve()
manifest = read(campaign / "supplementary/manifest.json")
aid = sys.argv[1]
attempt = next(a for a in manifest["attempts"] if a["attempt_id"] == aid)
review_dir = campaign / "supplementary/evaluation" / aid
review = read(review_dir / "review.json")
verify_submission(campaign, attempt)
require(review["attempt_id"] == aid, "Attempt mismatch")
require(
    len(review["blocks"]) == 5
    and {b["block_id"] for b in review["blocks"]} == {f"B{i}" for i in range(1, 6)},
    "Expected B1-B5",
)
require(
    type(review["eligible"]) is bool and type(review["workflow_complete"]) is bool,
    "Invalid booleans",
)
require(
    review["mathematical_verdict"] in ["PASS", "FAIL", "REVIEW", "NOT_EVALUATED"],
    "Invalid verdict",
)
require(
    review["access_status"]
    in ["no_incident", "recovered", "deviation", "unresolved", "contaminated"],
    "Invalid access status",
)
require(
    not review["eligible"]
    or review["access_status"] not in ["unresolved", "contaminated"],
    "Eligibility/access contradiction",
)
require(
    parse(attempt["review_dispatch_at"])
    <= parse(review["review_started_at"])
    <= parse(review["review_stopped_at"]),
    "Invalid timestamps",
)
refs = list(review["final_evidence_refs"])
require(review["mathematical_verdict"] != "PASS" or refs, "PASS missing evidence")
for block in review["blocks"]:
    require(type(block["reached"]) is bool, "Invalid reached value")
    require(
        block["gate_verdict"]
        in ["PASS", "FAIL", "UNRESOLVED", "NOT_REACHED", "NOT_EVALUATED"],
        "Invalid gate",
    )
    require(
        block["gate_verdict"] != "PASS"
        or (block["reached"] and block.get("checks") and block.get("evidence_refs")),
        "Gate PASS missing evidence",
    )
    require(
        block["gate_verdict"] != "NOT_REACHED" or not block["reached"],
        "Reached contradiction",
    )
    refs.extend(block.get("evidence_refs", []))
    for check in block.get("checks", []):
        require(
            check["status"] in ["PASS", "FAIL", "UNRESOLVED"], "Invalid check status"
        )
        if check.get("evidence_ref"):
            refs.append(check["evidence_ref"])
if review.get("notebook_path"):
    refs.append(review["notebook_path"])
for ref in refs:
    require(isinstance(ref, str) and ref, "Invalid evidence ref")
    name = ref.partition("#")[0]
    require(not Path(name).is_absolute(), "Absolute evidence ref")
    path = (campaign / name).resolve()
    require(
        fs_path(path).is_file()
        and any(
            path.is_relative_to(p.resolve())
            for p in [Path(attempt["output"]), review_dir]
        ),
        f"Missing/out-of-scope evidence: {ref}",
    )
print(
    json.dumps(
        {
            "attempt_id": aid,
            "validation": "passed",
            "mathematical_verdict": review["mathematical_verdict"],
            "eligible": review["eligible"],
            "workflow_complete": review["workflow_complete"],
            "blocks": {b["block_id"]: b["gate_verdict"] for b in review["blocks"]},
            "reason": review["final_reason"],
        }
    )
)
