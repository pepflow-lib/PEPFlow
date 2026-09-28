"""Read only metadata, usage and boundaries for this controller's children."""

import json
from pathlib import Path

root = Path("C:/Users/Jack/.codex/sessions/2026/09/23")
metas = []
for p in root.glob("*.jsonl"):
    with p.open(encoding="utf-8") as f:
        try:
            e = json.loads(f.readline())
        except ValueError:
            continue
    m = e.get("payload", {})
    src = m.get("source", {})
    spawn = (
        src.get("subagent", {}).get("thread_spawn", {}) if isinstance(src, dict) else {}
    )
    if spawn.get("agent_path") == "/root/prepare_campaign":
        metas.append((p, m, spawn))
for p, m, spawn in metas:
    turns, usages, boundaries = [], [], []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        v = e.get("payload", {})
        if e.get("type") == "turn_context":
            turns.append({k: v.get(k) for k in ["turn_id", "model", "effort"]})
        if e.get("type") == "event_msg" and v.get("type") == "token_count":
            usages.append(v.get("info"))
        if e.get("type") == "event_msg" and v.get("type") in [
            "task_started",
            "task_complete",
        ]:
            boundaries.append({"timestamp": e.get("timestamp"), "type": v["type"]})
    print(
        json.dumps(
            {
                "session_id": m.get("id"),
                "spawn": spawn,
                "path": str(p),
                "turns": turns,
                "usage_events": len(usages),
                "latest_usage": usages[-1] if usages else None,
                "boundaries": boundaries,
            },
            indent=2,
        )
    )
