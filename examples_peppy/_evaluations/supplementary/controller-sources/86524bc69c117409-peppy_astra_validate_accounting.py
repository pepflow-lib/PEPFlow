"""Validate preregistration and observed completed-attempt accounting only."""

import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = Path((ROOT / "tmp/current_peppy_astra_medium_6x5_campaign.txt").read_text())
S = C / "supplementary"
m = json.loads((S / "manifest.json").read_text())
parse = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))  # noqa: E731 -- Preserve the archived helper lambda.
assert len(m["attempts"]) == 30 and len({a["attempt_id"] for a in m["attempts"]}) == 30
assert all(
    sum(a["condition_id"] == c for a in m["attempts"]) == 5
    for c in m["selected_conditions"]
)
assert sorted(
    sum(q["queue"][0] == p for q in m["round_queues"])
    for p in ["pgm_with_sos", "pgm_without_sos"]
) == [2, 3]
rows = []
events = []
for a in m["attempts"]:
    if a.get("dispatch_at"):
        events.append((parse(a["dispatch_at"]), 1, a["attempt_id"]))
    if a.get("stopped_at") and a.get("dispatch_at"):
        events.append((parse(a["stopped_at"]), -1, a["attempt_id"]))
    if not a.get("stopped_at") or not a.get("started"):
        continue
    wall = sum(
        (parse(v["end"]) - parse(v["start"])).total_seconds() for v in a["visits"]
    )
    assert abs(wall - a["attempt_wall_seconds"]) < 0.01, a["attempt_id"]
    tokens = 0
    for v in a["visits"]:
        begin = v.get("usage_start") or a["preflight_usage_baseline"]
        tokens += v["usage_end"]["total_tokens"] - begin["total_tokens"]
    assert tokens == a["generation_tokens_total"], a["attempt_id"]
    components = a.get("generation_usage_components")
    if components:
        assert (
            components["total_tokens"]
            == components["input_tokens"] + components["output_tokens"]
        )
    rows.append(
        {
            "attempt_id": a["attempt_id"],
            "visits": len(a["visits"]),
            "time_reconciled": True,
            "tokens_reconciled": True,
        }
    )
active = 0
peak = 0
for stamp, delta, aid in sorted(events):
    active += delta
    peak = max(peak, active)
    assert 0 <= active <= m["worker_limit"], (stamp, aid, active)
for rep in range(2, 6):
    starts = [
        parse(a["dispatch_at"])
        for a in m["attempts"]
        if a["repetition"] == rep and a.get("dispatch_at")
    ]
    if starts:
        prev = [a for a in m["attempts"] if a["repetition"] == rep - 1]
        assert all(a.get("stopped_at") for a in prev)
        assert min(starts) >= max(parse(a["stopped_at"]) for a in prev)
report = {
    "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    "planned_attempts": 30,
    "planned_blocks": 150,
    "pgm_pairs": 5,
    "observed_peak_generation_concurrency": peak,
    "completed_accounting_checks": rows,
    "mathematical_assessment_performed": False,
}
target = S / "measurements"
target.mkdir(exist_ok=True)
(target / "accounting-validation.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print(
    json.dumps(
        {
            "status": "passed",
            "finished_attempts_checked": len(rows),
            "observed_peak_generation_concurrency": peak,
        }
    )
)
