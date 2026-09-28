"""Controller-only adapter for a host's existing same-session continuation API.

The callback must accept keyword arguments session_id, message, deadline and
idempotency_key, enforce the original deadline, and return a JSON-safe receipt.
No transport, timer, worker creation or host capability is invented here.
Persist returned receipts in the existing host event log. On unknown dispatch
outcome, inspect that log before retrying; do not start a replacement session.
"""

import json
from datetime import datetime

CONTINUATION = "Proceed with the next step under the existing case instructions."
SCHEMA_VERSION = "same-session-continuation-v1"


def continue_handoff(*, attempt, handoff, now, receipts, send=None):
    """Send only a real operational handoff, once, through an injected host API."""
    if not isinstance(attempt, dict) or not isinstance(handoff, dict):
        raise ValueError("Attempt and handoff must be objects")
    protocol = attempt.get("protocol_version")
    if protocol is not None and (not isinstance(protocol, str) or not protocol.strip()):
        raise ValueError("Campaign protocol must be a nonempty string or None")
    metadata = {"schema_version": SCHEMA_VERSION, "protocol_version": protocol}
    for field in ("session_id", "attempt_id"):
        identity = attempt.get(field)
        if not isinstance(identity, str) or not identity.strip():
            raise ValueError("Frozen attempt and session identities are required")
    if (
        handoff.get("attempt_id") != attempt["attempt_id"]
        or handoff.get("session_id") != attempt["session_id"]
    ):
        raise ValueError("Continuation must use the original attempt session")
    if (
        handoff.get("event") != "block_handoff"
        or handoff.get("host_task_completed") is not True
    ):
        raise ValueError("An observed host handoff is required")
    if (
        not isinstance(handoff.get("handoff_id"), str)
        or not handoff["handoff_id"].strip()
    ):
        raise ValueError("A stable host handoff identity is required")
    allowed_blocks = tuple(f"B{i}" for i in range(1, 6))
    if (
        handoff.get("current_block") not in allowed_blocks
        or handoff.get("next_block") not in allowed_blocks
    ):
        raise ValueError("Handoff must name actual workflow blocks, including revisits")
    key = json.dumps(
        [attempt["attempt_id"], attempt["session_id"], handoff["handoff_id"]],
        separators=(",", ":"),
    )
    if key in receipts:
        return {**metadata, "status": "already_dispatched", "receipt": receipts[key]}
    deadline_text = attempt.get("deadline")
    if not isinstance(deadline_text, str) or not isinstance(now, datetime):
        raise ValueError("Deadline must be an ISO string and host time a datetime")
    deadline = datetime.fromisoformat(deadline_text.replace("Z", "+00:00"))
    if deadline.utcoffset() is None or now.utcoffset() is None:
        raise ValueError("Deadline and host time must have UTC offsets")
    if attempt.get("stopped") or now >= deadline:
        return {
            **metadata,
            "status": "stopped",
            "reason": "attempt_stopped_or_deadline",
        }
    if send is None:
        return {
            **metadata,
            "status": "unsupported",
            "reason": "no_same_session_host_adapter",
        }
    receipt = send(
        session_id=attempt["session_id"],
        message=CONTINUATION,
        deadline=deadline_text,
        idempotency_key=key,
    )
    receipts[key] = receipt
    return {**metadata, "status": "dispatched", "receipt": receipt}
