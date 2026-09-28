"""Controller-only filtered host measurements; never expose these to workers."""

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("campaign")
parser.add_argument("--parent", default="01a0ce93-530a-7fa2-b66e-53aa4b16df1e")
args = parser.parse_args()
dest = Path(args.campaign) / "supplementary/host"
dest.mkdir(parents=True, exist_ok=True)
now = dt.datetime.now(dt.timezone.utc)
summary = []
manifest = Path(args.campaign) / "supplementary/manifest.json"
created = dt.datetime.fromisoformat(
    json.loads(manifest.read_text())["created_at"].replace("Z", "+00:00")
).date()
days = [
    created - dt.timedelta(days=1) + dt.timedelta(days=i)
    for i in range((now.date() - created).days + 2)
]
for day in days:
    for path in (Path("C:/Users/Jack/.codex/sessions") / day.strftime("%Y/%m/%d")).glob(
        "*.jsonl"
    ):
        with path.open(encoding="utf-8") as f:
            try:
                first = json.loads(f.readline())
            except ValueError:
                continue
            meta = first.get("payload", {})
            source = meta.get("source", {})
            spawn = (
                source.get("subagent", {}).get("thread_spawn", {})
                if isinstance(source, dict)
                else {}
            )
            if (
                spawn.get("parent_thread_id") != args.parent
                and meta.get("id") != args.parent
            ):
                continue
            name = (
                "controller"
                if meta.get("id") == args.parent
                else spawn.get("agent_path", "").split("/")[-1]
            )
            events, calls, turns, anomalies = [], [], [], []
            previous = None
            turn = None
            for lineno, line in enumerate(f, 2):
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                p = e.get("payload", {})
                base = {
                    "timestamp": e.get("timestamp"),
                    "line": lineno,
                    "session_id": meta["id"],
                }
                if e.get("type") == "turn_context":
                    turn = p.get("turn_id")
                    turns.append(
                        {
                            **base,
                            "turn_id": turn,
                            "model": p.get("model"),
                            "effort": p.get("effort"),
                        }
                    )
                if e.get("type") == "event_msg" and p.get("type") in [
                    "task_started",
                    "task_complete",
                    "turn_aborted",
                ]:
                    events.append({**base, "turn_id": turn, "type": p["type"]})
                if (
                    e.get("type") == "event_msg"
                    and p.get("type") == "token_count"
                    and p.get("info")
                ):
                    total = p["info"].get("total_token_usage")
                    if total and total != previous:
                        delta = {
                            k: v - (previous or {}).get(k, 0)
                            for k, v in total.items()
                            if isinstance(v, int)
                        }
                        if any(v < 0 for v in delta.values()):
                            anomalies.append(
                                {
                                    **base,
                                    "kind": "counter_reset",
                                    "previous": previous,
                                    "total": total,
                                }
                            )
                        events.append(
                            {
                                **base,
                                "turn_id": turn,
                                "type": "usage",
                                "event_id": f"{meta['id']}:{lineno}",
                                "total": total,
                                "delta": delta,
                                "last_usage": p["info"].get("last_token_usage"),
                            }
                        )
                        previous = total
                if e.get("type") == "response_item" and p.get("type") in [
                    "function_call",
                    "custom_tool_call",
                ]:
                    calls.append(
                        {
                            **base,
                            "turn_id": turn,
                            "call_id": p.get("call_id"),
                            "name": p.get("name"),
                            "arguments": p.get("arguments", p.get("input")),
                        }
                    )
        record = {
            "observed_at": now.isoformat(),
            "session_id": meta["id"],
            "agent_path": spawn.get("agent_path"),
            "host_log": str(path),
            "turns": turns,
            "events": events,
            "anomalies": anomalies,
            "usage_scope": "Host cumulative request tokens; total=input+output; cached input and reasoning are subsets, not additive.",
            "last_total": previous,
        }
        ledger = dest / f"{name}-events-observed.jsonl"
        seen = set()
        if ledger.exists():
            for line in ledger.read_text(encoding="utf-8").splitlines():
                seen.add(json.loads(line)["observation_hash"])
        with ledger.open("a", encoding="utf-8") as retained:
            for observed in [*turns, *events]:
                digest = hashlib.sha256(
                    json.dumps(observed, sort_keys=True).encode()
                ).hexdigest()
                if digest not in seen:
                    retained.write(
                        json.dumps(
                            {
                                "observation_hash": digest,
                                "first_observed_at": now.isoformat(),
                                "record": observed,
                            }
                        )
                        + "\n"
                    )
                    seen.add(digest)
        outfile = dest / f"{name}.json"
        if outfile.exists():
            old = json.loads(outfile.read_text(encoding="utf-8"))
            if len(old.get("events", [])) > len(events):
                outfile = dest / f"{name}-shortened-{now.strftime('%H%M%S')}.json"
        outfile.write_text(json.dumps(record, indent=2), encoding="utf-8")
        (dest / f"{name}-access-calls.json").write_text(
            json.dumps(calls, indent=2), encoding="utf-8"
        )
        summary.append(
            {
                "agent": name,
                "session_id": meta["id"],
                "observed_settings": turns[-1] if turns else None,
                "usage_events": sum(e["type"] == "usage" for e in events),
                "total": previous,
                "latest_boundary": next(
                    (e for e in reversed(events) if e["type"] != "usage"), None
                ),
            }
        )
print(json.dumps(summary, indent=2))
