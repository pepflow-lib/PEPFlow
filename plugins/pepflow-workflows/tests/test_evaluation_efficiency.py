"""Synthetic tests for controller accounting and protocol-only continuations."""

import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "optional/evaluate-peppy/scripts"


def module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


accounting = module("collect_activity")
continuation = module("continuation")


def stamp(second):
    return f"2026-09-19T00:00:{second:02d}Z"


def interval(start, end, activity):
    return {
        "event": "activity_interval",
        "start": stamp(start),
        "end": stamp(end),
        "activity": activity,
        "evidence_ref": "synthetic-host-event",
    }


class ActivityAccountingTests(unittest.TestCase):
    def test_campaign_protocol_is_preserved_without_inventing_one(self):
        result = accounting.collect(
            [], stamp(0), stamp(1), protocol_version="frozen-test-protocol"
        )
        self.assertEqual(result["protocol_version"], "frozen-test-protocol")
        self.assertEqual(result["schema_version"], "activity-accounting-v1")
        self.assertIsNone(
            accounting.collect([], stamp(0), stamp(1))["protocol_version"]
        )
        for value in ("", " ", [], 3):
            with self.subTest(value=value), self.assertRaises(ValueError):
                accounting.collect([], stamp(0), stamp(1), protocol_version=value)

    def test_parallel_union_conflicts_and_gaps_reconcile(self):
        events = [
            interval(1, 6, "tooling_setup_repair"),
            interval(3, 8, "tooling_setup_repair"),
            interval(7, 9, "execution_rendered_review"),
        ]
        result = accounting.collect(events, stamp(0), stamp(10))
        self.assertEqual(result["activity_seconds"]["tooling_setup_repair"], 6)
        self.assertEqual(result["activity_seconds"]["execution_rendered_review"], 1)
        self.assertEqual(result["activity_seconds"]["unallocated"], 3)
        self.assertEqual(result["activity_seconds_sum"], 10)
        self.assertIn("overlap_conflict", [row["reason"] for row in result["segments"]])

    def test_legacy_milestone_cannot_invent_activity(self):
        event = {"event": "B5_exact_proof", "timestamp": stamp(4)}
        result = accounting.collect([event], stamp(0), stamp(10))
        self.assertEqual(result["activity_seconds"]["unallocated"], 10)
        self.assertEqual(result["observations"], [event])
        self.assertEqual(result["usage_status"], "unavailable")
        self.assertIsNone(result["tokens_total"])

    def test_tokens_deduplicate_and_require_observed_activity_boundary(self):
        usage = {
            "event": "request_usage",
            "request_id": "one",
            "tokens": {"input": 100, "cached_input": 90},
            "activity": "tooling_setup_repair",
            "evidence_ref": "synthetic-request",
        }
        attributed = dict(usage, request_id="two", activity_boundary_observed=True)
        result = accounting.collect([usage, usage, attributed], stamp(0), stamp(10))
        self.assertEqual(
            result["activity_token_observed"]["unallocated"],
            {"input": 100, "cached_input": 90},
        )
        self.assertEqual(
            result["activity_token_observed"]["tooling_setup_repair"]["input"], 100
        )
        self.assertEqual(result["request_count_observed"], 2)
        self.assertIsNone(result["tokens_total"])
        self.assertEqual(result["usage_status"], "partial")
        with self.assertRaises(ValueError):
            accounting.collect(
                [usage, dict(usage, tokens={"input": 101})], stamp(0), stamp(10)
            )

    def test_invalid_interval_or_token_counters_are_rejected(self):
        for event in [
            interval(4, 2, "handoff_wait"),
            interval(1, 12, "handoff_wait"),
            interval(1, 2, "invented"),
            {
                "event": "request_usage",
                "request_id": "one",
                "evidence_ref": "record",
                "tokens": {"input": -1},
            },
        ]:
            with self.subTest(event=event), self.assertRaises(ValueError):
                accounting.collect([event], stamp(0), stamp(10))
        with self.assertRaises(ValueError):
            accounting.collect([], "2026-09-19T00:00:00", stamp(10))

    def test_disjoint_intervals_keep_gaps_and_timezone_offsets(self):
        events = [interval(1, 3, "handoff_wait"), interval(6, 8, "handoff_wait")]
        events.append(dict(interval(8, 8, "execution_rendered_review")))
        result = accounting.collect(events, "2026-09-18T20:00:00-04:00", stamp(10))
        self.assertEqual(result["activity_seconds"]["handoff_wait"], 4)
        self.assertEqual(result["activity_seconds"]["unallocated"], 6)
        self.assertEqual(result["activity_seconds_sum"], 10)
        self.assertEqual(accounting.collect([], stamp(0), stamp(0))["segments"], [])

    def test_malformed_usage_is_rejected_without_claiming_coverage(self):
        base = {
            "event": "request_usage",
            "request_id": "one",
            "evidence_ref": "host",
            "tokens": {"input": 1},
        }
        changes = [{"tokens": value} for value in (None, [], {}, "100")]
        changes += [
            {"tokens": {"input": value}}
            for value in (-1, 1.5, float("inf"), float("nan"), True, "10", None)
        ]
        changes += [
            {"tokens": {"": 1}},
            {"tokens": {1: 1}},
            {"request_id": []},
            {"request_id": " "},
            {"evidence_ref": True},
            {"evidence_ref": " "},
        ]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                accounting.collect([dict(base, **change)], stamp(0), stamp(10))
        for event in (
            None,
            [],
            "event",
            dict(interval(1, 2, "handoff_wait"), start=None),
        ):
            with self.subTest(event=event), self.assertRaises(ValueError):
                accounting.collect([event], stamp(0), stamp(10))


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.attempt = {
            "attempt_id": "example_r01",
            "session_id": "fresh-session",
            "deadline": stamp(10),
        }
        self.handoff = {
            "event": "block_handoff",
            "attempt_id": "example_r01",
            "session_id": "fresh-session",
            "handoff_id": "turn-2",
            "host_task_completed": True,
            "current_block": "B3",
            "next_block": "B2",
        }
        self.now = datetime(2026, 9, 19, 0, 0, 5, tzinfo=timezone.utc)
        self.receipts = {}
        self.calls = []

    def send(self, **kwargs):
        self.calls.append(kwargs)
        return {"host_receipt": "accepted"}

    def invoke(self, **kwargs):
        defaults = dict(
            attempt=self.attempt,
            handoff=self.handoff,
            now=self.now,
            receipts=self.receipts,
        )
        defaults.update(kwargs)
        return continuation.continue_handoff(**defaults)

    def test_campaign_protocol_is_separate_from_adapter_schema(self):
        self.attempt["protocol_version"] = "frozen-test-protocol"
        result = self.invoke(send=self.send)
        self.assertEqual(result["protocol_version"], "frozen-test-protocol")
        self.assertEqual(result["schema_version"], "same-session-continuation-v1")
        self.assertEqual(
            self.invoke(send=self.send)["protocol_version"], "frozen-test-protocol"
        )
        for value in ("", [], 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.invoke(
                    attempt=dict(self.attempt, protocol_version=value), send=self.send
                )
        self.assertEqual(len(self.calls), 1)

    def test_revisit_keeps_session_deadline_and_frozen_message(self):
        self.assertEqual(self.invoke(send=self.send)["status"], "dispatched")
        call = self.calls[0]
        self.assertEqual(call["session_id"], self.attempt["session_id"])
        self.assertEqual(call["deadline"], self.attempt["deadline"])
        self.assertEqual(call["message"], continuation.CONTINUATION)
        self.assertEqual(self.invoke(send=self.send)["status"], "already_dispatched")
        self.assertEqual(len(self.calls), 1)

    def test_unavailable_or_expired_host_never_sends(self):
        self.assertEqual(self.invoke()["status"], "unsupported")
        expired = self.now.replace(second=10)
        self.assertEqual(self.invoke(now=expired, send=self.send)["status"], "stopped")
        self.assertEqual(self.calls, [])
        self.assertEqual(self.receipts, {})

    def test_nonhandoff_and_cross_attempt_rejected(self):
        for changes in (
            {"session_id": "replacement"},
            {"attempt_id": "other"},
            {"host_task_completed": False},
            {"host_task_completed": "true"},
            {"next_block": "new_attempt"},
            {"handoff_id": ""},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.invoke(handoff=dict(self.handoff, **changes), send=self.send)
        self.assertEqual(self.calls, [])

    def test_failed_host_send_does_not_claim_dispatch(self):
        def failure(**kwargs):
            raise RuntimeError("host unavailable")

        with self.assertRaises(RuntimeError):
            self.invoke(send=failure)
        self.assertEqual(self.receipts, {})

    def test_identity_keys_cannot_collide_and_include_session(self):
        first_attempt = dict(self.attempt, attempt_id="a:b")
        first_handoff = dict(self.handoff, attempt_id="a:b", handoff_id="c")
        self.invoke(attempt=first_attempt, handoff=first_handoff, send=self.send)
        second_attempt = dict(self.attempt, attempt_id="a")
        second_handoff = dict(self.handoff, attempt_id="a", handoff_id="b:c")
        self.assertEqual(
            self.invoke(attempt=second_attempt, handoff=second_handoff, send=self.send)[
                "status"
            ],
            "dispatched",
        )
        self.assertNotEqual(
            self.calls[0]["idempotency_key"], self.calls[1]["idempotency_key"]
        )

    def test_stopped_attempt_and_invalid_clock_never_send(self):
        self.assertEqual(
            self.invoke(attempt=dict(self.attempt, stopped=True), send=self.send)[
                "status"
            ],
            "stopped",
        )
        for attempt in (
            dict(self.attempt, session_id=[]),
            dict(self.attempt, attempt_id=" "),
            dict(self.attempt, deadline=None),
            dict(self.attempt, deadline="2026-09-19T00:00:10"),
        ):
            with self.subTest(attempt=attempt), self.assertRaises(ValueError):
                self.invoke(attempt=attempt, send=self.send)
        with self.assertRaises(ValueError):
            self.invoke(now=self.now.replace(tzinfo=None), send=self.send)
        with self.assertRaises(ValueError):
            self.invoke(handoff=dict(self.handoff, handoff_id=True), send=self.send)
        self.assertEqual(self.calls, [])

    def test_offset_equivalent_deadline_and_last_instant(self):
        attempt = dict(self.attempt, deadline="2026-09-18T20:00:10-04:00")
        self.assertEqual(
            self.invoke(
                attempt=attempt, now=self.now.replace(second=10), send=self.send
            )["status"],
            "stopped",
        )
        self.assertEqual(
            self.invoke(
                attempt=attempt,
                now=self.now.replace(second=9, microsecond=999999),
                send=self.send,
            )["status"],
            "dispatched",
        )
        self.assertEqual(self.calls[0]["deadline"], attempt["deadline"])


if __name__ == "__main__":
    unittest.main()
