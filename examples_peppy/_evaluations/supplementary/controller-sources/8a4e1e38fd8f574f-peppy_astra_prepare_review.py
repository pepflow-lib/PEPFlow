"""Prepare one independent review after every generation attempt is frozen."""

import datetime as dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = Path((ROOT / "tmp/current_peppy_astra_medium_6x5_campaign.txt").read_text())
S = C / "supplementary"
mp = S / "manifest.json"
m = json.loads(mp.read_text())
assert all(a["run_status"] not in ["running", "not_started"] for a in m["attempts"]), (
    "All selected generation must stop before review"
)
aid = sys.argv[1]
a = next(a for a in m["attempts"] if a["attempt_id"] == aid)
out = Path(a["output"])
review = S / "evaluation" / aid
review.mkdir(exist_ok=False)
hashes = json.loads(Path(a["submission_hashes"]).read_text())
for name, expected in hashes.items():
    assert hashlib.sha256((out / name).read_bytes()).hexdigest() == expected, (
        f"Frozen submission changed: {name}"
    )
shutil.copyfile(a["packet"], review / "input.md")
shutil.copyfile(
    ROOT / "tmp/peppy_astra_review_schema.json", review / "review-schema.json"
)
rubric = (S / "evaluation/protocol/references/evaluation-rubric.md").read_text()
lines = []
for line in rubric.splitlines():
    if line.startswith("| ") and any(
        x in line for x in ["| PGM (", "| OGM |", "| BPPM |", "| FEG |", "| Dual-FEG |"]
    ):
        key = {
            "pgm": "| PGM (",
            "ogm": "| OGM |",
            "bppm": "| BPPM |",
            "feg": "| FEG |",
            "dual_feg": "| Dual-FEG |",
        }[a["case_id"]]
        if not line.startswith(key):
            continue
    if line == "## Controller-only historical attribution":
        break
    lines.append(line)
(review / "rubric.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
shutil.copyfile(
    S / "evaluation/protocol/references/clean-room.md", review / "clean-room.md"
)
shutil.copyfile(
    S / "evaluation/protocol/references/evaluation-operations.md",
    review / "evaluation-operations.md",
)
validation = review / "validation"
validation.mkdir()
for name in hashes:
    src = out / name
    dst = validation / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
now = dt.datetime.now(dt.timezone.utc)
deadline = now + dt.timedelta(seconds=m["review_wall_limit_seconds"])
a.update(
    review_dispatch_at=now.isoformat(),
    review_deadline=deadline.isoformat(),
    review_status="running",
)
settings = dict(
    attempt_id=aid,
    model="gpt-6-astra",
    reasoning_effort="medium",
    review_started_at=now.isoformat(),
    deadline=deadline.isoformat(),
    review_wall_limit_seconds=7200,
    token_cap=None,
    original_submission=str(out),
    validation_copy=str(validation),
    generation_status=a["run_status"],
    generation_stop_reason=a.get("stop_reason"),
    submission_hashes=hashes,
    python=str(ROOT / ".venv/Scripts/python.exe"),
    review_output=str(review / "review.json"),
)
(review / "settings.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")
instructions = f"""Independent evaluation of {aid}. All campaign generation is frozen. Model GPT-6 Astra, medium reasoning. Review only this submission; do not repair its proof or consult other attempts, papers, reference solutions, or history. Read own settings.json, input.md, rubric.md, clean-room.md, evaluation-operations.md, review-schema.json and submitted generic skills. Original artifacts are read-only at {out}. Use only your validation copy {validation} for re-execution, and redirect ALL writes/state/helper/temp/cache paths to this review workspace. Python -I -B with explicitly approved package/helper roots. Do not execute a saved notebook without checking and redirecting its absolute write paths. No browser, rendering or exports are required.

Deadline {deadline.isoformat()}; review starts {now.isoformat()}, 7200 seconds, no token cap. Evaluate exact target and mathematical argument using submitted evidence only, separately from block/delivery and operational status. Inspect actual evidence rather than trusting saved completion flags. Clearly label checks replayed versus inspected. No essential missing lemma or coefficient may be invented. If a substantive candidate remains undecidable at the limit, use REVIEW. Record absence/incomplete arguments honestly as FAIL; only concrete preflight/access ineligibility warrants NOT_EVALUATED. Instruction-only observability limits alone do not establish contamination.

Write {review / "review.json"} matching the schema, with exactly B1-B5, actual detailed checks/reasons/evidence and UTC review stop time. Evidence refs should be paths relative to original attempt or validation directory and identify notebook cells when relevant. Assess access records and required source/execution checks as well as proof. Return a concise completion notice with review.json path. Do not spawn agents. Your readable repository scope is this review directory, original own submission and its approved generic resources; no other campaign files or attempts. Installed pinned dependencies/stdlib are trusted. Do not modify frozen submissions, sources or skills.
"""
(review / "instructions.md").write_text(instructions, encoding="utf-8")
mp.write_text(json.dumps(m, indent=2), encoding="utf-8")
print(str(review / "instructions.md"))
