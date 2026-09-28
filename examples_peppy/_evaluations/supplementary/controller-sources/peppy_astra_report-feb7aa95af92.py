"""Derive campaign reports solely from operational evidence and independent reviews."""

from typing import Any

# Keep typing metadata separate from the recorded import sequence.
# isort: split


import csv
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
helper_spec = importlib.util.spec_from_file_location(
    "review_preparation", ROOT / "tmp/peppy_astra_prepare_review.py"
)
assert helper_spec is not None and helper_spec.loader is not None
helper = importlib.util.module_from_spec(helper_spec)
helper_spec.loader.exec_module(helper)
contained, digest, parse, read, require, validate_campaign, verify_submission = (
    getattr(helper, name)
    for name in [
        "contained",
        "digest",
        "parse",
        "read",
        "require",
        "validate_campaign",
        "verify_submission",
    ]
)
C = Path(
    (ROOT / "tmp/current_peppy_astra_medium_6x5_campaign.txt")
    .read_text(encoding="utf-8-sig")
    .strip()
).resolve()
S = C / "supplementary"
M = json.loads((S / "manifest.json").read_text())
write = lambda p, v: p.write_text(json.dumps(v, indent=2), encoding="utf-8")  # noqa: E731 -- Preserve the archived helper lambda.
validate_campaign(M)


def evidence_link(ref, a):
    require(isinstance(ref, str) and bool(ref), "Evidence must name a file")
    name, separator, anchor = ref.partition("#")
    require(not Path(name).is_absolute(), "Evidence refs must be campaign-relative")
    path = contained(C, name)
    roots = [
        Path(a["output"]).resolve(),
        (S / "evaluation" / a["attempt_id"]).resolve(),
    ]
    require(
        path.is_file() and any(path.is_relative_to(root) for root in roots),
        f"Missing or out-of-scope evidence: {ref}",
    )
    relative = Path(os.path.relpath(path, S / "assessments")).as_posix()
    return f"[{ref.replace('[', '(').replace(']', ')')}]({quote(relative)}{separator}{quote(anchor)})"


# Validate every assessment and frozen original before writing any result files.
reviews = {}
review_sessions = [a.get("review_session_id") for a in M["attempts"]]
require(
    all(review_sessions) and len(set(review_sessions)) == 30,
    "Every review requires a distinct registered fresh session",
)
require(
    not (set(review_sessions) & {a.get("session_id") for a in M["attempts"]}),
    "Generation sessions cannot perform independent review",
)
for a in M["attempts"]:
    aid = a["attempt_id"]
    verify_submission(C, a)
    reviewfile = S / "evaluation" / aid / "review.json"
    require(a.get("review_status") == "completed", f"Review has not stopped: {aid}")
    require(
        reviewfile.is_file() and digest(reviewfile) == a.get("review_sha256"),
        f"Missing/changed registered review: {aid}",
    )
    r = read(reviewfile)
    hostpath = S / "host" / f"{a.get('review_agent_name', 'review_' + aid)}.json"
    require(hostpath.is_file(), f"Missing reviewer host observations: {aid}")
    host = read(hostpath)
    require(
        host.get("session_id") == a["review_session_id"]
        and host.get("turns")
        and all(
            t.get("model") == M["evaluator_model"]
            and t.get("effort") == M["evaluator_reasoning_effort"]
            for t in host["turns"]
        ),
        f"Reviewer model/session mismatch: {aid}",
    )
    require(
        r["attempt_id"] == aid
        and len(r["blocks"]) == 5
        and {b["block_id"] for b in r["blocks"]} == {f"B{i}" for i in range(1, 6)},
        "Review block mismatch",
    )
    require(
        type(r["eligible"]) is bool and type(r["workflow_complete"]) is bool,
        "Invalid review booleans",
    )
    require(
        r["mathematical_verdict"] in ["PASS", "FAIL", "REVIEW", "NOT_EVALUATED"],
        "Invalid final verdict",
    )
    require(
        r["access_status"]
        in ["no_incident", "recovered", "deviation", "unresolved", "contaminated"],
        "Invalid access status",
    )
    require(
        not r["eligible"] or r["access_status"] not in ["unresolved", "contaminated"],
        "Ineligible access cannot count as success",
    )
    require(
        parse(a["review_dispatch_at"])
        <= parse(r["review_started_at"])
        <= parse(r["review_stopped_at"]),
        "Invalid review timestamps",
    )
    require(
        parse(a["review_dispatch_at"])
        >= max(parse(x["stopped_at"]) for x in M["attempts"] if x.get("stopped_at")),
        "Review preceded generation barrier",
    )
    for b in r["blocks"]:
        require(
            type(b["reached"]) is bool
            and b["gate_verdict"]
            in ["PASS", "FAIL", "UNRESOLVED", "NOT_REACHED", "NOT_EVALUATED"],
            "Invalid block judgment",
        )
        require(
            b["gate_verdict"] != "PASS"
            or (b["reached"] and b.get("evidence_refs") and b.get("checks")),
            "PASS lacks inspectable checks/evidence",
        )
        require(
            b["gate_verdict"] != "NOT_REACHED" or not b["reached"],
            "Reached block marked NOT_REACHED",
        )
        for ref in b.get("evidence_refs", []):
            evidence_link(ref, a)
        for check in b.get("checks", []):
            require(
                check["status"] in ["PASS", "FAIL", "UNRESOLVED"],
                "Invalid check status",
            )
            if check.get("evidence_ref"):
                evidence_link(check["evidence_ref"], a)
    require(
        r["mathematical_verdict"] != "PASS" or r.get("final_evidence_refs"),
        "Final PASS lacks evidence",
    )
    for ref in r.get("final_evidence_refs", []):
        evidence_link(ref, a)
    if r.get("notebook_path"):
        evidence_link(r["notebook_path"], a)
    reviews[aid] = r


def review_usage(a, h):
    """Fresh-session zero origin and final boundary are required for a complete total."""
    usage = [e for e in h.get("events", []) if e["type"] == "usage"]
    observed = (h.get("last_total") or {}).get("total_tokens")
    first = usage[0] if usage else {}
    zero_origin = bool(first.get("total")) and first.get("total") == first.get(
        "last_usage"
    )
    boundaries = [e for e in h.get("events", []) if e["type"] != "usage"]
    complete = (
        observed is not None
        and zero_origin
        and not h.get("anomalies")
        and bool(a.get("review_session_id"))
        and h.get("session_id") == a.get("review_session_id")
        and boundaries
        and boundaries[0]["type"] == "task_started"
        and boundaries[-1]["type"] == "task_complete"
        and parse(boundaries[-1]["timestamp"]) >= parse(a["review_stopped_at"])
        and parse(h["observed_at"]) >= parse(boundaries[-1]["timestamp"])
        and h.get("turns")
        and all(
            t["model"] == M["evaluator_model"]
            and t["effort"] == M["evaluator_reasoning_effort"]
            for t in h["turns"]
        )
    )
    require(
        observed is None or (type(observed) is int and observed >= 0),
        "Invalid review counter",
    )
    return (
        observed if complete else None,
        observed,
        "complete"
        if complete
        else "partial"
        if observed is not None
        else "unavailable",
    )


collector = S / "evaluation/protocol/scripts/collect_activity.py"
require(
    digest(collector) == M["protocol_hashes"]["scripts/collect_activity.py"],
    "Frozen collector drift",
)
spec = importlib.util.spec_from_file_location("activity", collector)
assert spec is not None and spec.loader is not None
activity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)
runs = []
blocks = []
block_timing = []
(S / "assessments").mkdir(exist_ok=True)
results = [
    f"# {M['campaign_id']}\n",
    f"Completed 30 generation attempts and 30 independent reviews using {M['model']} / {M['reasoning_effort']} for generation and {M['evaluator_model']} / {M['evaluator_reasoning_effort']} for evaluation, with up to {M['worker_limit']} parallel workers. Isolation was instruction-only, not OS-enforced.\n",
    "PASS means that the corresponding requirement was established in a valid independent attempt. FAIL means that success was not established under this protocol; the linked detail distinguishes mathematical failure, incomplete review, unreached blocks, contamination, and infrastructure problems.\n",
    "| Example / condition | Repetition | B1 | B2 | B3 | B4 | B5 | Final |",
    "| --- | --- | --- | --- | --- | --- | --- | --- |",
]
timing = [
    f"# Timing: {M['campaign_id']}\n",
    "Generation includes model/service waits and recovery after dispatch. Preflight and independent review are separate. Concurrent attempt durations do not sum to campaign elapsed time.\n",
    "| Attempt | Generation minutes | Generation tokens | Review minutes | Review tokens |",
    "| --- | --- | --- | --- | --- |",
]
for a in M["attempts"]:
    aid = a["attempt_id"]
    reviewfile = S / "evaluation" / aid / "review.json"
    require(reviewfile.exists(), f"Independent review missing: {aid}")
    r = reviews[aid]
    row = dict(a)
    row["independent_review"] = r
    row.update(
        {
            k: r[k]
            for k in [
                "eligible",
                "access_status",
                "access_reason",
                "mathematical_verdict",
                "workflow_complete",
                "notebook_path",
                "final_reason",
            ]
        }
    )
    row["summary_result"] = (
        "PASS" if row["eligible"] and row["mathematical_verdict"] == "PASS" else "FAIL"
    )
    row["assessment_path"] = f"supplementary/assessments/{aid}.md"
    hpath = S / "host" / f"{a.get('review_agent_name', 'review_' + aid)}.json"
    h = json.loads(hpath.read_text()) if hpath.exists() else {}
    (
        row["evaluation_tokens_total"],
        row["evaluation_tokens_observed"],
        row["evaluation_usage_status"],
    ) = review_usage(a, h)
    row["evaluation_usage_components_observed"] = h.get("last_total")
    row["evaluation_usage_source"] = hpath.relative_to(C).as_posix() if h else None
    row["evaluation_usage_definition"] = h.get("usage_scope")
    row["evaluation_wall_seconds"] = (
        (parse(r["review_stopped_at"]) - parse(a["review_dispatch_at"])).total_seconds()
        if a.get("review_dispatch_at")
        else None
    )
    row["review_deadline_overrun_seconds"] = max(
        0, (parse(r["review_stopped_at"]) - parse(a["review_deadline"])).total_seconds()
    )
    notes = [
        f"# {aid}\n",
        r["final_reason"] + "\n",
        f"Operational status: {a['run_status']}. Access: {r['access_status']}; eligible: {r['eligible']}. {r['access_reason']}\n",
    ]
    label = aid.rsplit("_r", 1)[0].replace("_", " ")
    if a["condition_id"] == "bppm":
        label += " (supplied rate)"
    cells = [label, a["repetition_id"]]
    total_wall = 0.0
    total_tokens = 0
    complete_tokens = True
    complete_wall = True
    all_visits = a.get("visits", [])
    intervals = sorted(
        (parse(v["start"]), parse(v["end"]))
        for v in all_visits
        if v.get("start") and v.get("end")
    )
    require(
        all(v["block_id"] in {f"B{i}" for i in range(1, 6)} for v in all_visits),
        "Unknown visit block",
    )
    require(all(end >= start for start, end in intervals), "Reversed visit")
    require(
        all(right[0] >= left[1] for left, right in zip(intervals, intervals[1:])),
        "Overlapping visits",
    )
    wall_coverage = (
        bool(intervals)
        and len(intervals) == len(all_visits)
        and bool(a.get("dispatch_at"))
        and bool(a.get("stopped_at"))
        and intervals[0][0] == parse(a["dispatch_at"])
        and intervals[-1][1] == parse(a["stopped_at"])
        and all(right[0] == left[1] for left, right in zip(intervals, intervals[1:]))
    )
    if a.get("attempt_wall_seconds") is not None:
        require(a["attempt_wall_seconds"] >= 0, "Negative attempt duration")
        require(
            abs(
                a["attempt_wall_seconds"]
                - (parse(a["stopped_at"]) - parse(a["dispatch_at"])).total_seconds()
            )
            < 0.001,
            "Attempt duration mismatch",
        )
    genhost = S / "host" / f"{a.get('agent_name', 'gen_' + aid)}.json"
    gh = read(genhost) if genhost.exists() else {}
    generation_coverage = (
        a.get("usage_status") == "complete"
        and bool(a.get("session_id"))
        and not gh.get("anomalies")
        and gh.get("session_id") == a.get("session_id")
    )
    if generation_coverage:
        begin = a.get("preflight_usage_baseline") or {}
        end = a.get("host_usage_final") or {}
        generation_coverage = (
            type(begin.get("total_tokens")) is int
            and type(end.get("total_tokens")) is int
            and end["total_tokens"] >= begin["total_tokens"]
            and a.get("generation_tokens_total")
            == end["total_tokens"] - begin["total_tokens"]
        )
    if not generation_coverage:
        row["generation_tokens_total"] = None
        row["usage_status"] = (
            "partial"
            if a.get("generation_tokens_observed") is not None
            else "unavailable"
        )
    for b in sorted(r["blocks"], key=lambda b: b["block_id"]):
        b = dict(b)
        b.update(
            {
                k: a[k]
                for k in [
                    "campaign_id",
                    "protocol_version",
                    "attempt_id",
                    "case_id",
                    "condition_id",
                    "pair_id",
                    "repetition",
                ]
            }
        )
        visits = [v for v in a.get("visits", []) if v["block_id"] == b["block_id"]]
        b["visit_count"] = len(visits)
        b["wall_seconds_observed"] = (
            sum(
                (parse(v["end"]) - parse(v["start"])).total_seconds()
                for v in visits
                if v.get("start") and v.get("end")
            )
            if visits
            else None
        )
        b["wall_seconds"] = (
            b["wall_seconds_observed"]
            if wall_coverage and visits
            else 0
            if wall_coverage and not b["reached"]
            else None
        )
        deltas = []
        for v in visits:
            begin = v.get("usage_start") or (
                a.get("preflight_usage_baseline") if v["visit_id"] == 1 else None
            )
            end = v.get("usage_end")
            if (
                not begin
                or not end
                or type(end.get("total_tokens")) is not int
                or type(begin.get("total_tokens")) is not int
                or end["total_tokens"] < begin["total_tokens"]
            ):
                deltas.append(None)
            else:
                deltas.append(end["total_tokens"] - begin["total_tokens"])
        b["tokens_total"] = (
            sum(deltas)  # ty: ignore[no-matching-overload]  # The condition below excludes missing token counts.
            if wall_coverage
            and generation_coverage
            and deltas
            and all(x is not None for x in deltas)
            else 0
            if wall_coverage and generation_coverage and not visits and not b["reached"]
            else None
        )
        b["tokens_observed"] = (
            sum(x for x in deltas if x is not None)
            if any(x is not None for x in deltas)
            else 0
            if b["tokens_total"] == 0
            else None
        )
        b["usage_status"] = (
            "complete"
            if b["tokens_total"] is not None
            else "partial"
            if b["tokens_observed"] is not None
            else "unavailable"
        )
        b["usage_definition"] = (
            "Host cumulative total_tokens deltas at controller visit boundaries; cached input/reasoning are subsets."
        )
        b["summary_result"] = (
            "PASS" if r["eligible"] and b["gate_verdict"] == "PASS" else "FAIL"
        )
        b["assessment_path"] = row["assessment_path"] + "#" + b["block_id"].lower()
        cells.append(f"[{b['summary_result']}]({b['assessment_path']})")
        notes.extend(
            [
                f"## {b['block_id']}\n",
                f"{b['gate_verdict']}: {b['reason']}\n",
                f"Time: {b['wall_seconds']} seconds; tokens: {b['tokens_total']} ({b['usage_status']}). Evidence: "
                + ", ".join(evidence_link(x, a) for x in b.get("evidence_refs", []))
                + "\n",
            ]
        )
        if b["wall_seconds"] is not None:
            total_wall += b["wall_seconds"]
        else:
            complete_wall = False
        if b["tokens_total"] is None:
            complete_tokens = False
        else:
            total_tokens += b["tokens_total"]
        blocks.append(b)
    cells.append(f"[{row['summary_result']}]({row['assessment_path']}#final)")
    results.append("| " + " | ".join(cells) + " |")
    notes.extend(
        [
            "## Final\n",
            f"{r['mathematical_verdict']}: {r['final_reason']}\n",
            r.get("target_scope_comparison", "") + "\n",
            r.get("verification_method", "") + "\n",
            "Evidence: "
            + ", ".join(evidence_link(x, a) for x in r.get("final_evidence_refs", []))
            + "\n",
        ]
    )
    (S / "assessments" / f"{aid}.md").write_text("\n".join(notes), encoding="utf-8")
    observed_walls = [
        b["wall_seconds_observed"]
        for b in blocks
        if b["attempt_id"] == aid and b["wall_seconds_observed"] is not None
    ]
    row["block_wall_seconds_observed"] = sum(observed_walls) if observed_walls else None
    row["block_wall_seconds_sum"] = total_wall if complete_wall else None
    row["unallocated_seconds"] = (
        a["attempt_wall_seconds"] - total_wall
        if complete_wall and a.get("attempt_wall_seconds") is not None
        else None
    )
    require(
        row["unallocated_seconds"] is None or row["unallocated_seconds"] >= -0.001,
        "Block wall totals exceed generation",
    )
    row["block_tokens_sum"] = total_tokens if complete_tokens else None
    row["unallocated_tokens"] = (
        row["generation_tokens_total"] - total_tokens
        if complete_tokens and row.get("generation_tokens_total") is not None
        else None
    )
    require(
        row["unallocated_tokens"] is None or row["unallocated_tokens"] >= 0,
        "Block tokens exceed generation",
    )
    measured = S / "measurements" / aid
    measured.mkdir(parents=True, exist_ok=True)
    if a.get("dispatch_at") and a.get("stopped_at"):
        act = activity.collect(
            [],
            a["dispatch_at"],
            a["stopped_at"],
            protocol_version=M["protocol_version"],
        )
        act["limitations"] = (
            "No complete orthogonal activity boundary stream was established; elapsed generation is retained as unallocated in this independent activity view. Block measurements remain separately available."
        )
        if not (measured / "activity_timing.json").exists():
            write(measured / "activity_timing.json", act)
        else:
            existing = read(measured / "activity_timing.json")
            require(
                existing["protocol_version"] == M["protocol_version"]
                and abs(existing["attempt_wall_seconds"] - act["attempt_wall_seconds"])
                < 0.001
                and abs(
                    sum(existing["activity_seconds"].values())
                    - act["attempt_wall_seconds"]
                )
                < 0.001,
                "Existing activity measurements do not reconcile",
            )
        row["activity_timing"] = (
            (measured / "activity_timing.json").relative_to(C).as_posix()
        )
    val = lambda x: f"{x / 60:.2f}" if x is not None else "unavailable"  # noqa: E731 -- Preserve the archived helper lambda.
    timing.append(
        f"| {aid} | {val(a.get('attempt_wall_seconds'))} | {row.get('generation_tokens_total')} ({row['usage_status']}) | {val(row.get('evaluation_wall_seconds'))} | {row['evaluation_tokens_total']} ({row['evaluation_usage_status']}) |"
    )
    runs.append(row)
    local_blocks = [b for b in blocks if b["attempt_id"] == aid]
    block_timing.append(
        "| "
        + aid
        + " | "
        + " | ".join(
            "unavailable"
            if b["wall_seconds"] is None
            else f"{b['wall_seconds'] / 60:.2f}"
            for b in local_blocks
        )
        + " |"
    )
pairs = []
pairblocks = []
pairlines = [
    "# Paired PGM comparison\n",
    "All five preregistered pairs are retained. Differences are without supplied SOS minus with supplied SOS. Consumed cost is distinct from successful workflow completion time.\n",
    "| Pair | With SOS | Without SOS | Consumed seconds difference | Tokens difference |",
    "| --- | --- | --- | --- | --- |",
]
for rep in range(1, 6):
    w = next(a for a in runs if a["attempt_id"] == f"pgm_with_sos_r{rep:02d}")
    n = next(a for a in runs if a["attempt_id"] == f"pgm_without_sos_r{rep:02d}")
    diff = (  # noqa: E731 -- Preserve the archived helper lambda.
        lambda k: n[k] - w[k] if n.get(k) is not None and w.get(k) is not None else None
    )
    pair = dict(
        pair_id=f"pgm_r{rep:02d}",
        with_sos=w["attempt_id"],
        without_sos=n["attempt_id"],
        consumed_time_difference=diff("attempt_wall_seconds"),
        token_difference=diff("generation_tokens_total"),
        completion_time_difference=None,
    )
    fields = [
        "eligible",
        "mathematical_verdict",
        "run_status",
        "workflow_complete",
        "attempt_wall_seconds",
        "generation_tokens_total",
        "generation_usage_components",
        "usage_status",
        "evaluation_wall_seconds",
        "evaluation_tokens_total",
        "evaluation_tokens_observed",
        "evaluation_usage_status",
        "evaluation_usage_components_observed",
        "notebook_path",
    ]
    pair["with_sos_observations"] = {k: w.get(k) for k in fields}
    pair["without_sos_observations"] = {k: n.get(k) for k in fields}
    pair["evaluation_time_difference"] = diff("evaluation_wall_seconds")
    pair["evaluation_tokens_difference"] = diff("evaluation_tokens_total")
    pair["blocks"] = []
    for bid in [f"B{i}" for i in range(1, 6)]:
        wb = next(
            b
            for b in blocks
            if b["attempt_id"] == w["attempt_id"] and b["block_id"] == bid
        )
        nb = next(
            b
            for b in blocks
            if b["attempt_id"] == n["attempt_id"] and b["block_id"] == bid
        )
        bd = (  # noqa: E731 -- Preserve the archived helper lambda.
            lambda k: nb[k] - wb[k]
            if nb.get(k) is not None and wb.get(k) is not None
            else None
        )
        observed = dict(
            block_id=bid,
            with_sos={
                k: wb.get(k)
                for k in [
                    "reached",
                    "gate_verdict",
                    "wall_seconds",
                    "tokens_total",
                    "usage_status",
                    "visit_count",
                ]
            },
            without_sos={
                k: nb.get(k)
                for k in [
                    "reached",
                    "gate_verdict",
                    "wall_seconds",
                    "tokens_total",
                    "usage_status",
                    "visit_count",
                ]
            },
            consumed_time_difference=bd("wall_seconds"),
            token_difference=bd("tokens_total"),
        )
        pair["blocks"].append(observed)
        pairblocks.append(
            f"| {pair['pair_id']} | {bid} | {wb['gate_verdict']} (reached={wb['reached']}) / {nb['gate_verdict']} (reached={nb['reached']}) | {wb['wall_seconds']} / {nb['wall_seconds']} | {observed['consumed_time_difference']} | {observed['token_difference']} | {wb['visit_count']} / {nb['visit_count']} |"
        )
    if all(
        a["eligible"]
        and a["mathematical_verdict"] == "PASS"
        and a["run_status"] == "completed"
        and a["workflow_complete"]
        for a in [w, n]
    ):
        pair["completion_time_difference"] = pair["consumed_time_difference"]
    pairs.append(pair)
    pairlines.append(
        f"| {pair['pair_id']} | {w['mathematical_verdict']} | {n['mathematical_verdict']} | {pair['consumed_time_difference']} | {pair['token_difference']} |"
    )
require(
    len(runs) == 30 and len(blocks) == 150 and len(pairs) == 5, "Report counts mismatch"
)
require(
    len({(b["attempt_id"], b["block_id"]) for b in blocks}) == 150,
    "Duplicate block records",
)
for filename, rows in [("runs.csv", runs), ("blocks.csv", blocks)]:
    with (S / filename).open(encoding="utf-8") as f:
        columns = next(csv.reader(f))
    with (S / filename).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(
            {
                k: json.dumps(v) if isinstance(v, (dict, list)) else v
                for k, v in r.items()
            }
            for r in rows
        )
results.extend(
    [
        "",
        f"Eligible mathematical successes: {sum(a['summary_result'] == 'PASS' for a in runs)}/30. Operationally excluded (NOT_EVALUATED): {sum(a['mathematical_verdict'] == 'NOT_EVALUATED' for a in runs)}. Exclusion does not establish that a theorem is false.",
        "",
        "[Timing and token accounting](timing.md) · [Paired PGM comparison](supplementary/pgm-sos-comparison.md) · [Detailed records](supplementary/details.json) · [Protocol and settings](supplementary/manifest.json)",
    ]
)
(C / "results.md").write_text("\n".join(results) + "\n", encoding="utf-8")
timing.extend(
    [
        "\n## Block wall time (minutes)\n",
        "Revisits are included. Zero requires complete visit coverage and an unreached block; unavailable measurements stay explicit.\n",
        "| Attempt | B1 | B2 | B3 | B4 | B5 |",
        "| --- | --- | --- | --- | --- | --- |",
        *block_timing,
    ]
)
prep = []
for a in runs:
    hp = S / "host" / f"{a.get('agent_name', 'gen_' + a['attempt_id'])}.json"
    if hp.exists() and a.get("dispatch_at"):
        host = json.loads(hp.read_text())
        starts = [e["timestamp"] for e in host["events"] if e["type"] == "task_started"]
        if starts:
            duration = (parse(a["dispatch_at"]) - parse(starts[0])).total_seconds()
            require(duration >= 0, "Negative preparation time")
            prep.append(duration)
controllerpath = S / "host/controller.json"
controller = json.loads(controllerpath.read_text()) if controllerpath.exists() else {}
start_events = [
    e["timestamp"] for e in controller.get("events", []) if e["type"] == "task_started"
]
campaign_start = parse(start_events[0]) if start_events else parse(M["created_at"])
gen_starts = [parse(a["dispatch_at"]) for a in runs if a.get("dispatch_at")]
gen_stops = [parse(a["stopped_at"]) for a in runs if a.get("stopped_at")]
reported_at = dt.datetime.now(dt.timezone.utc)
baselines = [
    a["preflight_usage_baseline"]["total_tokens"]
    for a in runs
    if type((a.get("preflight_usage_baseline") or {}).get("total_tokens")) is int
]
staging = [
    a["review_preparation_wall_seconds"]
    for a in runs
    if a.get("review_preparation_wall_seconds") is not None
]
costs: dict[str, Any] = dict(
    reported_at=reported_at.isoformat(),
    elapsed_start=campaign_start.isoformat(),
    elapsed_start_source="controller_first_observed_task_start"
    if start_events
    else "manifest_creation_only_preparation_start_unavailable",
    elapsed_through_report_seconds=(reported_at - campaign_start).total_seconds(),
    worker_preparation_wall_seconds_observed=sum(prep) if prep else None,
    worker_preparation_wall_observation_count=len(prep),
    worker_preflight_tokens_observed=sum(baselines) if baselines else None,
    worker_preflight_token_observation_count=len(baselines),
    worker_preflight_usage_status="partial" if baselines else "unavailable",
    worker_preflight_usage_limitation="Observed cumulative pre-dispatch snapshots; zero-origin coverage not independently established for this preparation scope.",
    review_staging_wall_seconds_observed=sum(staging) if staging else None,
    review_staging_observation_count=len(staging),
    controller_tokens_observed=(controller.get("last_total") or {}).get("total_tokens"),
    controller_usage_scope="Entire observed controller session, including preparation/orchestration/reporting; no phase allocation claimed",
    generation_span_seconds=(max(gen_stops) - min(gen_starts)).total_seconds()
    if gen_starts and gen_stops
    else None,
    preparation_agent_observations=[],
)
reserved = {a.get(k) for a in runs for k in ["agent_name", "review_agent_name"]} | {
    "controller"
}
for path in sorted((S / "host").glob("*.json")):
    if (
        path.stem in reserved
        or path.stem.startswith(("gen_", "review_"))
        or path.stem.endswith("-access-calls")
        or "-shortened-" in path.stem
    ):
        continue
    host = read(path)
    if not isinstance(host, dict) or "last_total" not in host:
        continue
    boundaries = [e for e in host.get("events", []) if e["type"] != "usage"]
    costs["preparation_agent_observations"].append(
        dict(
            agent=path.stem,
            source=path.relative_to(C).as_posix(),
            tokens_observed=(host.get("last_total") or {}).get("total_tokens"),
            usage_status="partial" if host.get("last_total") else "unavailable",
            session_span_seconds=(
                parse(boundaries[-1]["timestamp"]) - parse(boundaries[0]["timestamp"])
            ).total_seconds()
            if len(boundaries) >= 2
            else None,
            scope="Observed helper session; includes controller support/audit work, not necessarily pure preparation",
        )
    )
write(
    S / "details.json",
    dict(
        campaign_id=M["campaign_id"],
        protocol_version=M["protocol_version"],
        status="completed",
        attempts=runs,
        blocks=blocks,
        pgm_pairs=pairs,
        cost_scopes=costs,
    ),
)
timing.extend(
    [
        "\n## Preparation and elapsed scope\n",
        f"Observed start: {costs['elapsed_start_source']}.",
        f"Observed start to first generation dispatch: {(min(gen_starts) - campaign_start).total_seconds() / 60:.2f} minutes."
        if gen_starts
        else "No timed generation.",
        f"Summed per-worker preflight/dispatch preparation: {val(costs['worker_preparation_wall_seconds_observed'])} minutes across {len(prep)} observed workers. These intervals overlap; do not add them to campaign elapsed time.",
        f"Preflight cumulative tokens observed: {costs['worker_preflight_tokens_observed']} across {len(baselines)} workers (partial coverage; not a complete preparation total).",
        f"Review snapshot staging: {val(costs['review_staging_wall_seconds_observed'])} minutes across {len(staging)} measured submissions; separate from reviewer time.",
        f"Generation campaign span: {val(costs['generation_span_seconds'])} minutes.",
        f"Elapsed through report creation: {costs['elapsed_through_report_seconds'] / 60:.2f} minutes.",
        f"Controller session tokens observed: {costs['controller_tokens_observed']}; no phase allocation. Helper-session costs and coverage are retained in details.json. Review costs appear above. Rendering/export were not requested.",
    ]
)
for helper in costs["preparation_agent_observations"]:
    timing.append(
        f"Helper {helper['agent']}: {helper['tokens_observed']} observed tokens ({helper['usage_status']}); {val(helper['session_span_seconds'])} observed session minutes. Includes support/audit work where applicable."
    )
(C / "timing.md").write_text(
    "\n".join(timing)
    + "\n\nCanonical block costs, coverage and observed token components are in [details.json](supplementary/details.json). Host usage counts repeated context; cached input and reasoning are subsets, not additional tokens.\n",
    encoding="utf-8",
)
pairlines.extend(
    [
        "\n## Block costs and visits\n",
        "Each cell lists supplied-SOS / no-supplied-SOS observations. Unreached blocks are not fast successful completions. Null differences indicate unavailable comparable measurements.\n",
        "| Pair | Block | Gates | Seconds | Seconds difference | Tokens difference | Visits |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        *pairblocks,
    ]
)
for condition in ["pgm_with_sos", "pgm_without_sos"]:
    selected = [a for a in runs if a["condition_id"] == condition]
    pairlines.append(
        f"\n{condition}: {sum(a['summary_result'] == 'PASS' for a in selected)}/5 eligible mathematical successes. All five costs and underlying outcomes are retained.\n"
    )
pairlines.append(
    "Review costs, observed input/cached-input/output/reasoning components, reachability, and conditional successful-completion differences are recorded per pair in details.json. These five pairs support descriptive comparison, not a general reliability or speedup claim."
)
pairlines.append(
    f"Completed-workflow comparison includes {sum(p['completion_time_difference'] is not None for p in pairs)}/5 pairs meeting both-side eligibility, mathematical PASS, completed status and workflow requirements."
)
(S / "pgm-sos-comparison.md").write_text("\n".join(pairlines) + "\n", encoding="utf-8")
print(
    json.dumps(
        {
            "attempts": len(runs),
            "blocks": len(blocks),
            "pairs": len(pairs),
            "mathematical_passes": sum(a["summary_result"] == "PASS" for a in runs),
        }
    )
)
