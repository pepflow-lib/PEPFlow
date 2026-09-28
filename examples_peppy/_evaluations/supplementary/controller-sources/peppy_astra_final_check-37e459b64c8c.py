"""Final campaign accounting, provenance, and report-link checks."""

import collections
import csv
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import unquote

from peppy_astra_prepare_review import (  # ty: ignore[unresolved-import]  # Historical controller imports its sibling helper from the original tmp directory.
    digest,
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
sup = campaign / "supplementary"
manifest = read(sup / "manifest.json")
details = read(sup / "details.json")
require(details["status"] == "completed", "Report incomplete")
require(
    len(details["attempts"]) == 30
    and len(details["blocks"]) == 150
    and len(details["pgm_pairs"]) == 5,
    "Count mismatch",
)
for name, expected in manifest["source_hashes"].items():
    require(digest(root / name) == expected, f"Framework/source drift: {name}")
for name, expected in manifest["protocol_hashes"].items():
    require(
        digest(sup / "evaluation/protocol" / name) == expected,
        f"Frozen protocol drift: {name}",
    )
    require(
        digest(root / "plugins/pepflow-workflows/optional/evaluate-peppy" / name)
        == expected,
        f"Original protocol drift: {name}",
    )
events = []
for attempt in details["attempts"]:
    verify_submission(campaign, attempt)
    require(digest(Path(attempt["packet"])) == attempt["packet_sha256"], "Packet drift")
    require(attempt["review_status"] == "completed", "Incomplete review")
    require(attempt["review_deadline_overrun_seconds"] == 0, "Review overrun")
    require(
        attempt["block_tokens_sum"] == attempt["generation_tokens_total"],
        "Token accounting mismatch",
    )
    require(
        abs(attempt["block_wall_seconds_sum"] - attempt["attempt_wall_seconds"])
        < 0.001,
        "Wall accounting mismatch",
    )
    events.extend(
        [
            (parse(attempt["review_dispatch_at"]), 1),
            (parse(attempt["review_stopped_at"]), -1),
        ]
    )
active = peak = 0
for stamp, delta in sorted(events):
    active += delta
    peak = max(peak, active)
    require(0 <= active <= manifest["worker_limit"], "Review concurrency exceeded")
require(active == 0, "Unclosed review")
for name, expected in [("runs.csv", 30), ("blocks.csv", 150)]:
    with (sup / name).open(encoding="utf-8") as stream:
        require(len(list(csv.DictReader(stream))) == expected, f"CSV count: {name}")
reports = [
    campaign / "results.md",
    campaign / "timing.md",
    sup / "pgm-sos-comparison.md",
    *sorted((sup / "assessments").glob("*.md")),
]
links = 0
for report in reports:
    for target in re.findall(r"\]\(([^\n]+?)\)", report.read_text(encoding="utf-8")):
        if "://" in target:
            continue
        name = unquote(target.partition("#")[0])
        if not name:
            continue
        path = (report.parent / name).resolve()
        require(
            path.is_relative_to(campaign) and fs_path(path).is_file(),
            f"Broken report link: {report.name}: {target}",
        )
        links += 1
result = dict(
    checked_at=dt.datetime.now(dt.timezone.utc).isoformat(),
    status="passed",
    attempts=30,
    blocks=150,
    pairs=5,
    frozen_submissions_unchanged=True,
    original_sources_and_protocol_unchanged=True,
    peak_review_concurrency=peak,
    report_links_checked=links,
    verdicts=dict(
        collections.Counter(a["mathematical_verdict"] for a in details["attempts"])
    ),
    condition_passes={
        c: sum(
            a["condition_id"] == c and a["summary_result"] == "PASS"
            for a in details["attempts"]
        )
        for c in manifest["selected_conditions"]
    },
)
(sup / "measurements/final-validation.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(result))
