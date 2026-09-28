"""Derive campaign reports solely from operational evidence and independent reviews."""

import csv
import datetime as dt
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = Path((ROOT / "tmp/current_peppy_astra_medium_6x5_campaign.txt").read_text())
S = C / "supplementary"
M = json.loads((S / "manifest.json").read_text())
parse = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))  # noqa: E731 -- Preserve the archived helper lambda.
write = lambda p, v: p.write_text(json.dumps(v, indent=2), encoding="utf-8")  # noqa: E731 -- Preserve the archived helper lambda.
assert all(a["run_status"] not in ["running", "not_started"] for a in M["attempts"]), (
    "Generation must stop before reporting assessments"
)
spec = importlib.util.spec_from_file_location(
    "activity", S / "evaluation/protocol/scripts/collect_activity.py"
)
assert spec is not None and spec.loader is not None
activity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)
runs = []
blocks = []
block_timing = []
(S / "assessments").mkdir(exist_ok=True)
results = [
    f"# {M['campaign_id']}\n",
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
    assert reviewfile.exists(), f"Independent review missing: {aid}"
    r = json.loads(reviewfile.read_text(encoding="utf-8-sig"))
    assert r["attempt_id"] == aid and {b["block_id"] for b in r["blocks"]} == {
        f"B{i}" for i in range(1, 6)
    }
    assert r["mathematical_verdict"] in ["PASS", "FAIL", "REVIEW", "NOT_EVALUATED"]
    row = dict(a)
    row.update({k: v for k, v in r.items() if k != "blocks"})
    row["summary_result"] = (
        "PASS" if row["eligible"] and row["mathematical_verdict"] == "PASS" else "FAIL"
    )
    row["assessment_path"] = f"supplementary/assessments/{aid}.md"
    hpath = S / "host" / f"review_{aid}.json"
    h = json.loads(hpath.read_text()) if hpath.exists() else {}
    row["evaluation_tokens_total"] = (
        (h.get("last_total") or {}).get("total_tokens")
        if not h.get("anomalies")
        else None
    )
    row["evaluation_usage_status"] = (
        "complete" if row["evaluation_tokens_total"] is not None else "unavailable"
    )
    row["evaluation_wall_seconds"] = (
        (parse(r["review_stopped_at"]) - parse(a["review_dispatch_at"])).total_seconds()
        if a.get("review_dispatch_at")
        else None
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
        b["wall_seconds"] = (
            sum((parse(v["end"]) - parse(v["start"])).total_seconds() for v in visits)
            if visits
            else 0
            if not b["reached"]
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
                or end.get("total_tokens", 0) < begin.get("total_tokens", 0)
            ):
                deltas.append(None)
            else:
                deltas.append(end["total_tokens"] - begin["total_tokens"])
        b["tokens_total"] = (
            sum(deltas)  # ty: ignore[no-matching-overload]  # The condition below excludes missing token counts.
            if deltas and all(x is not None for x in deltas)
            else 0
            if not b["reached"]
            else None
        )
        b["tokens_observed"] = (
            sum(x for x in deltas if x is not None) if deltas else None
        )
        b["usage_status"] = (
            "complete" if b["tokens_total"] is not None else "unavailable"
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
                + ", ".join(str(x) for x in b.get("evidence_refs", []))
                + "\n",
            ]
        )
        if b["wall_seconds"] is not None:
            total_wall += b["wall_seconds"]
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
            + ", ".join(str(x) for x in r.get("final_evidence_refs", []))
            + "\n",
        ]
    )
    (S / "assessments" / f"{aid}.md").write_text("\n".join(notes), encoding="utf-8")
    row["block_wall_seconds_sum"] = total_wall
    row["unallocated_seconds"] = max(
        0, (a.get("attempt_wall_seconds") or 0) - total_wall
    )
    row["block_tokens_sum"] = total_tokens if complete_tokens else None
    row["unallocated_tokens"] = (
        a["generation_tokens_total"] - total_tokens
        if complete_tokens and a.get("generation_tokens_total") is not None
        else None
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
        write(measured / "activity_timing.json", act)
        row["activity_timing"] = str((measured / "activity_timing.json").relative_to(C))
    val = lambda x: f"{x / 60:.2f}" if x is not None else "unavailable"  # noqa: E731 -- Preserve the archived helper lambda.
    timing.append(
        f"| {aid} | {val(a.get('attempt_wall_seconds'))} | {a.get('generation_tokens_total')} | {val(row.get('evaluation_wall_seconds'))} | {row['evaluation_tokens_total']} |"
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
            f"| {pair['pair_id']} | {bid} | {wb['gate_verdict']} / {nb['gate_verdict']} | {wb['wall_seconds']} / {nb['wall_seconds']} | {observed['consumed_time_difference']} | {observed['token_difference']} | {wb['visit_count']} / {nb['visit_count']} |"
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
assert len(runs) == 30 and len(blocks) == 150 and len(pairs) == 5
assert len({a["attempt_id"] for a in runs}) == 30
write(
    S / "details.json",
    dict(
        campaign_id=M["campaign_id"],
        protocol_version=M["protocol_version"],
        status="completed",
        attempts=runs,
        blocks=blocks,
        pgm_pairs=pairs,
    ),
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
(C / "results.md").write_text("\n".join(results) + "\n", encoding="utf-8")
timing.extend(
    [
        "\n## Block wall time (minutes)\n",
        "Revisits are included. Zero denotes a confirmed unreached block; unavailable measurements stay explicit.\n",
        "| Attempt | B1 | B2 | B3 | B4 | B5 |",
        "| --- | --- | --- | --- | --- | --- |",
        *block_timing,
    ]
)
prep = []
for a in runs:
    hp = S / "host" / f"gen_{a['attempt_id']}.json"
    if hp.exists() and a.get("dispatch_at"):
        host = json.loads(hp.read_text())
        starts = [e["timestamp"] for e in host["events"] if e["type"] == "task_started"]
        if starts:
            prep.append((parse(a["dispatch_at"]) - parse(starts[0])).total_seconds())
controllerpath = S / "host/controller.json"
controller = json.loads(controllerpath.read_text()) if controllerpath.exists() else {}
start_events = [
    e["timestamp"] for e in controller.get("events", []) if e["type"] == "task_started"
]
campaign_start = parse(start_events[0]) if start_events else parse(M["created_at"])
gen_starts = [parse(a["dispatch_at"]) for a in runs if a.get("dispatch_at")]
gen_stops = [parse(a["stopped_at"]) for a in runs if a.get("stopped_at")]
timing.extend(
    [
        "\n## Preparation and elapsed scope\n",
        f"Initial preparation to first generation dispatch: {(min(gen_starts) - campaign_start).total_seconds() / 60:.2f} minutes."
        if gen_starts
        else "No timed generation.",
        f"Summed per-worker preflight/dispatch preparation: {sum(prep) / 60:.2f} minutes across {len(prep)} observed workers. These intervals overlap; do not add them to campaign elapsed time.",
        f"Generation campaign span: {(max(gen_stops) - min(gen_starts)).total_seconds() / 60:.2f} minutes."
        if gen_starts and gen_stops
        else "",
        f"Elapsed through report creation: {(dt.datetime.now(dt.timezone.utc) - campaign_start).total_seconds() / 60:.2f} minutes.",
        "Controller and preparation-agent token counters are retained separately under supplementary/host/. Review costs appear above. Rendering/export were not requested.",
    ]
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
