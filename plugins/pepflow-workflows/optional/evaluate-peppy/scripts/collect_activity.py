"""Controller-only, evidence-based activity accounting; no target computations.

Usage: python collect_activity.py EVENTS.jsonl --start ISO --stop ISO --output JSON
       --protocol-version FROZEN_CAMPAIGN_PROTOCOL
Explicit activity_interval events use start/end ISO UTC timestamps, activity,
and a nonempty evidence_ref. request_usage events require a unique request_id,
tokens (provider-normalized nonnegative counters), and optionally an activity
with activity_boundary_observed=true. Other events are retained as observations.
Never derive activity labels or token splits from milestone names or block IDs.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

SCHEMA_VERSION = "activity-accounting-v1"
ACTIVITIES = (
    "mathematical_discovery_validation",
    "notebook_authoring_revision",
    "execution_rendered_review",
    "tooling_setup_repair",
    "handoff_wait",
    "unallocated",
)


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("Timestamps must be ISO strings")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Timestamps must include a UTC offset")
    return result.timestamp()


def collect(events, start, stop, *, protocol_version=None):
    """Partition the attempt clock; None identifies a generic, non-campaign check."""
    if protocol_version is not None and (
        not isinstance(protocol_version, str) or not protocol_version.strip()
    ):
        raise ValueError("Campaign protocol must be a nonempty string or None")
    start, stop = timestamp(start), timestamp(stop)
    if stop < start:
        raise ValueError("Attempt stop precedes dispatch")
    intervals, observations, requests = [], [], {}
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Events must be objects")
        kind = event.get("event")
        if kind == "activity_interval":
            activity = event.get("activity")
            evidence = event.get("evidence_ref")
            if (
                activity not in ACTIVITIES
                or not isinstance(evidence, str)
                or not evidence.strip()
            ):
                raise ValueError(
                    "Activity intervals require a known label and evidence_ref"
                )
            left, right = timestamp(event.get("start")), timestamp(event.get("end"))
            if right < left:
                raise ValueError("Activity interval ends before it starts")
            if left < start or right > stop:
                raise ValueError("Activity interval lies outside attempt clock")
            intervals.append((left, right, activity))
        elif kind == "request_usage":
            identity = event.get("request_id")
            evidence = event.get("evidence_ref")
            if (
                not isinstance(identity, str)
                or not identity.strip()
                or not isinstance(evidence, str)
                or not evidence.strip()
            ):
                raise ValueError("Usage needs stable request identity and evidence_ref")
            if identity in requests and requests[identity] != event:
                raise ValueError("Conflicting duplicate request usage")
            tokens = event.get("tokens")
            if not isinstance(tokens, dict) or not tokens:
                raise ValueError("Usage needs a nonempty object of observed counters")
            for field, value in tokens.items():
                if not isinstance(field, str) or not field.strip():
                    raise ValueError("Usage counter names must be nonempty strings")
                if type(value) is not int or value < 0:
                    raise ValueError("Usage counters must be nonnegative integers")
            requests[identity] = event
        else:
            observations.append(event)
    boundaries = sorted({start, stop} | {p for row in intervals for p in row[:2]})
    seconds = dict.fromkeys(ACTIVITIES, 0.0)
    segments = []
    for left, right in zip(boundaries, boundaries[1:]):
        if right == left:
            continue
        labels = {label for a, b, label in intervals if a < right and b > left}
        activity = next(iter(labels)) if len(labels) == 1 else "unallocated"
        reason = (
            "observed"
            if len(labels) == 1
            else "overlap_conflict"
            if labels
            else "no_observation"
        )
        seconds[activity] += right - left
        segments.append(
            {
                "start_offset_seconds": left - start,
                "end_offset_seconds": right - start,
                "activity": activity,
                "reason": reason,
            }
        )
    usage = {label: {} for label in ACTIVITIES}
    for event in requests.values():
        activity = event.get("activity")
        if (
            activity not in ACTIVITIES
            or event.get("activity_boundary_observed") is not True
        ):
            activity = "unallocated"
        for key, value in event["tokens"].items():
            usage[activity][key] = usage[activity].get(key, 0) + value
    return {
        "schema_version": SCHEMA_VERSION,
        "protocol_version": protocol_version,
        "attempt_wall_seconds": stop - start,
        "activity_seconds": seconds,
        "activity_seconds_sum": sum(seconds.values()),
        "segments": segments,
        "activity_token_observed": usage,
        "usage_status": "partial" if requests else "unavailable",
        "tokens_total": None,
        "request_count_observed": len(requests),
        "observations": observations,
        "limits": [
            "Activity and block views must never be added together.",
            "Same-label overlaps use enclosing wall time; conflicting overlaps are unallocated.",
            "Usage contains observed request deltas only; normalize cumulative host counters upstream.",
            "Token fields may overlap (cached input/reasoning); do not sum fields.",
            "Completeness requires separate host coverage reconciliation; no hidden activity is inferred.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", type=Path)
    parser.add_argument("--start", required=True)
    parser.add_argument("--stop", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--protocol-version", required=True)
    args = parser.parse_args()
    events = [
        json.loads(line)
        for line in args.events.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    result = collect(
        events, args.start, args.stop, protocol_version=args.protocol_version
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "attempt_wall_seconds": result["attempt_wall_seconds"],
                "unallocated_seconds": result["activity_seconds"]["unallocated"],
            }
        )
    )


if __name__ == "__main__":
    main()
