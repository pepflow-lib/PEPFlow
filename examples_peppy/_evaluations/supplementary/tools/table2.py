"""Recompute Table 2 from frozen campaign records using only the standard library.

Run ``python examples_peppy/_evaluations/supplementary/tools/table2.py --check`` to validate inputs
and compare both checked-in reports. Omit --check to regenerate the reports.
This reads archived measurements and verdicts; it does not verify proofs or rerun
generation. Original delivery and post hoc mathematical validity stay separate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import TypedDict

CAMPAIGN = "20260923T140754Z_paper5_pgm_sos_6x5_isolation1"
CONDITIONS = {
    "ogm": "OGM",
    "bppm": "BPPM",
    "feg": "FEG",
    "dual_feg": "Dual-FEG",
    "pgm_without_sos": "PGM without supplied SOS",
    "pgm_with_sos": "PGM with supplied SOS",
}
BLOCKS = tuple(f"B{i}" for i in range(1, 6))
SOURCES = {
    "runs": "supplementary/runs.csv",
    "blocks": "supplementary/blocks.csv",
    "assessment": "posthoc_20260924T024014Z/assessment.json",
}


class Measurement(TypedDict):
    """Validated values for one attempt; time and token fields remain numeric."""

    condition: str
    blocks: dict[str, int | float]
    generation_seconds: int | float
    generation_tokens: int | float
    review_seconds: int | float
    review_tokens: int | float
    mathematical_verdict: str
    delivery_complete: bool


class InvalidRecords(ValueError):
    """Missing, ambiguous, or inconsistent campaign measurements."""


def require(condition, message):
    if not condition:
        raise InvalidRecords(message)


def number(value, label, *, integer=False, allow_roundoff=False):
    try:
        require(not isinstance(value, bool), f"{label}: expected a number")
        result = int(str(value)) if integer else float(value)
    except (ValueError, TypeError, OverflowError) as error:
        raise InvalidRecords(f"{label}: invalid number {value!r}") from error
    require(math.isfinite(result), f"{label}: non-finite measurement")
    require(
        result >= (-1e-6 if allow_roundoff else 0), f"{label}: negative measurement"
    )
    return result


def boolean(value, label):
    require(value in ("True", "False"), f"{label}: expected True or False")
    return value == "True"


def close(left, right, label):
    require(
        math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-6),
        f"{label}: accounting mismatch ({left} != {right})",
    )


def indexed(rows, fields, label):
    result = {}
    for row in rows:
        key = tuple(row[field] for field in fields)
        require(key not in result, f"{label}: duplicate {key}")
        result[key] = row
    return result


def summary(values):
    """Arithmetic mean and sample standard deviation (denominator n - 1)."""
    return {"mean": statistics.mean(values), "sample_sd": statistics.stdev(values)}


def compute_table(runs, blocks, assessment):
    """Validate all 30 attempts, then aggregate all five in every condition."""
    expected = {
        f"{condition}_r{repeat:02d}": (condition, repeat)
        for condition in CONDITIONS
        for repeat in range(1, 6)
    }
    run_map = indexed(runs, ("attempt_id",), "runs")
    review_map = indexed(assessment["attempts"], ("attempt_id",), "assessment")
    block_map = indexed(blocks, ("attempt_id", "block_id"), "blocks")
    review_blocks = indexed(
        assessment["blocks"], ("attempt_id", "block_id"), "assessment blocks"
    )
    ids = {(attempt,) for attempt in expected}
    block_ids = {(attempt, block) for attempt in expected for block in BLOCKS}
    require(
        set(run_map) == ids,
        "runs: expected six conditions x five repetitions (30 unique IDs)",
    )
    require(set(review_map) == ids, "assessment: expected the same 30 attempt IDs")
    require(
        set(block_map) == block_ids,
        "blocks: expected B1-B5 for all 30 attempts (150 rows)",
    )
    require(
        set(review_blocks) == block_ids,
        "assessment blocks: expected the same 150 block IDs",
    )
    require(
        assessment["original_records_unchanged"] is True,
        "assessment must preserve original records",
    )
    require(
        assessment["original_delivery_not_backfilled"] is True,
        "assessment must not backfill original delivery",
    )
    measurements: dict[str, Measurement] = {}
    campaigns = {row["campaign_id"] for row in runs + blocks}
    require(
        len(campaigns) == 1 and "" not in campaigns,
        "records must identify one campaign",
    )
    protocols = {row["protocol_version"] for row in runs + blocks}
    require(
        protocols == {assessment["original_protocol"]}, "protocol versions disagree"
    )
    for attempt, (condition, repeat) in expected.items():
        run, review = run_map[(attempt,)], review_map[(attempt,)]
        for label, row in (("run", run), ("assessment", review)):
            require(
                row["condition_id"] == condition,
                f"{attempt} {label}: condition mismatch",
            )
            require(
                number(row["repetition"], attempt, integer=True) == repeat,
                f"{attempt} {label}: repetition mismatch",
            )
        require(boolean(run["started"], attempt), f"{attempt}: attempt never started")
        require(
            run["usage_status"] == run["evaluation_usage_status"] == "complete",
            f"{attempt}: generation/review cost coverage is incomplete",
        )
        generation = number(run["attempt_wall_seconds"], attempt)
        tokens = number(run["generation_tokens_total"], attempt, integer=True)
        review_seconds = number(run["evaluation_wall_seconds"], attempt)
        review_tokens = number(run["evaluation_tokens_total"], attempt, integer=True)
        require(
            tokens == number(run["generation_tokens_observed"], attempt, integer=True),
            f"{attempt}: generation token coverage mismatch",
        )
        for key, measured in (
            ("original_generation_seconds", generation),
            ("original_generation_tokens", tokens),
            ("original_review_seconds", review_seconds),
            ("original_review_tokens", review_tokens),
        ):
            close(measured, number(review[key], f"{attempt} {key}"), f"{attempt} {key}")
        delivery = review["original_delivery_status"].upper()
        require(
            delivery in {"COMPLETE", "INCOMPLETE"},
            f"{attempt}: unknown delivery status",
        )
        completed = delivery == "COMPLETE"
        require(
            completed == boolean(run["workflow_complete"], attempt),
            f"{attempt}: original delivery records disagree",
        )
        require(
            review["original_generation_status"] == run["run_status"],
            f"{attempt}: original generation statuses disagree",
        )
        verdict = review["mathematical_verdict"]
        require(
            verdict in {"PASS", "FAIL", "REVIEW", "NOT_EVALUATED"},
            f"{attempt}: unknown mathematical verdict",
        )
        seconds_by_block, block_tokens = {}, 0
        for block in BLOCKS:
            row = block_map[(attempt, block)]
            require(
                row["condition_id"] == condition
                and number(row["repetition"], attempt, integer=True) == repeat,
                f"{attempt} {block}: condition/repetition mismatch",
            )
            require(
                row["usage_status"] == "complete",
                f"{attempt} {block}: incomplete costs",
            )
            require(
                boolean(row["reached"], attempt),
                f"{attempt} {block}: block not reached",
            )
            seconds_by_block[block] = number(row["wall_seconds"], f"{attempt} {block}")
            amount = number(row["tokens_total"], f"{attempt} {block}", integer=True)
            require(
                amount == number(row["tokens_observed"], attempt, integer=True),
                f"{attempt} {block}: token coverage mismatch",
            )
            block_tokens += amount
        seconds = sum(seconds_by_block.values())
        close(
            seconds,
            number(run["block_wall_seconds_sum"], attempt),
            f"{attempt} block seconds",
        )
        close(
            seconds + number(run["unallocated_seconds"], attempt, allow_roundoff=True),
            generation,
            f"{attempt} generation seconds",
        )
        require(
            block_tokens == number(run["block_tokens_sum"], attempt, integer=True),
            f"{attempt}: block token sum mismatch",
        )
        require(
            block_tokens + number(run["unallocated_tokens"], attempt, integer=True)
            == tokens,
            f"{attempt}: generation token accounting mismatch",
        )
        measurements[attempt] = dict(
            condition=condition,
            blocks=seconds_by_block,
            generation_seconds=generation,
            generation_tokens=tokens,
            review_seconds=review_seconds,
            review_tokens=review_tokens,
            mathematical_verdict=verdict,
            delivery_complete=completed,
        )
    rows = []
    for condition, label in CONDITIONS.items():
        items = [
            value for value in measurements.values() if value["condition"] == condition
        ]
        rows.append(
            {
                "condition_id": condition,
                "label": label,
                "attempts": len(items),
                "mathematical_verdict_counts": {
                    verdict: sum(
                        item["mathematical_verdict"] == verdict for item in items
                    )
                    for verdict in ("PASS", "FAIL", "REVIEW", "NOT_EVALUATED")
                },
                "original_complete_delivery": sum(
                    item["delivery_complete"] for item in items
                ),
                "block_minutes": {
                    block: summary([item["blocks"][block] / 60 for item in items])
                    for block in BLOCKS
                },
                "generation_tokens_millions": summary(
                    [item["generation_tokens"] / 1e6 for item in items]
                ),
            }
        )
    totals = {
        key: sum(item[key] for item in measurements.values())
        for key in (
            "generation_seconds",
            "generation_tokens",
            "review_seconds",
            "review_tokens",
        )
    }
    totals["original_complete_delivery"] = sum(
        item["delivery_complete"] for item in measurements.values()
    )
    totals["posthoc_mathematical_pass"] = sum(
        item["mathematical_verdict"] == "PASS" for item in measurements.values()
    )
    return {
        "campaign_id": next(iter(campaigns)),
        "attempts": len(runs),
        "blocks": len(blocks),
        "aggregation": "All five attempts per condition; sample standard deviation (n - 1).",
        "token_accounting": "Input plus output; repeated context included; cached input and reasoning are subsets.",
        "cost_scope": "Original generation and review only. Post hoc review, preparation, and controller costs excluded.",
        "rows": rows,
        "totals": totals,
    }


def load_campaign(campaign):
    records, hashes = {}, {}
    for name, relative in SOURCES.items():
        path = campaign / relative
        payload = path.read_bytes()
        hashes[relative] = hashlib.sha256(payload).hexdigest()
        if path.suffix == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as handle:
                records[name] = list(csv.DictReader(handle))
        else:
            records[name] = json.loads(payload)
    result = compute_table(**records)
    result["source_sha256"] = hashes
    return result


def markdown(result):
    lines = [
        "# Table 2: reproducibility evaluation",
        "",
        "Generated by `python examples_peppy/_evaluations/supplementary/tools/table2.py`. "
        "Validate with the same command plus `--check`.",
        "",
        result["aggregation"],
        "",
        "| Condition | Post hoc mathematical PASS | Original complete delivery | B1 min | B2 min | B3 min | B4 min | B5 min | Generation tokens (M) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    def display(value):
        return f"{value['mean']:.1f} ± {value['sample_sd']:.1f}"

    for row in result["rows"]:
        cells = [
            row["label"],
            f"{row['mathematical_verdict_counts']['PASS']}/{row['attempts']}",
            f"{row['original_complete_delivery']}/{row['attempts']}",
        ]
        cells.extend(display(row["block_minutes"][block]) for block in BLOCKS)
        cells.append(display(row["generation_tokens_millions"]))
        lines.append("| " + " | ".join(cells) + " |")
    total = result["totals"]
    lines.extend(
        [
            "",
            "Every originally incomplete delivery remains in the cost denominator. "
            "Block times include revisits. Mathematical verdicts come from the dated post hoc "
            "assessment; delivery and costs come from the original run records.",
            "",
            result["token_accounting"],
            "",
            result["cost_scope"],
            "",
            f"Summed generation: {total['generation_seconds'] / 3600:.2f} hours, "
            f"{total['generation_tokens'] / 1e6:.2f} million tokens. "
            f"Summed original review: {total['review_seconds'] / 3600:.2f} hours, "
            f"{total['review_tokens'] / 1e6:.2f} million tokens. "
            "Concurrent durations are not campaign elapsed time.",
            "",
            "[Full precision values and source SHA-256 hashes](table2.json). "
            "This calculation checks recorded accounting, not mathematical proof validity.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--campaign", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument(
        "--check", action="store_true", help="Compare reports without writing files"
    )
    args = parser.parse_args(argv)
    try:
        result = load_campaign(args.campaign)
        reports = {
            "table2.json": json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            "table2.md": markdown(result),
        }
        if args.check:
            for name, content in reports.items():
                require(
                    (args.output_dir / name).read_text(encoding="utf-8") == content,
                    f"{name}: differs from the recomputed report; regenerate and review changes",
                )
        else:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            for name, content in reports.items():
                (args.output_dir / name).write_text(
                    content, encoding="utf-8", newline="\n"
                )
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Table 2 validation failed: {error}", file=sys.stderr)
        return 1
    print(
        f"Table 2 {'verified' if args.check else 'generated'}: 30 attempts, 150 blocks; "
        f"{result['totals']['posthoc_mathematical_pass']} mathematical PASS, "
        f"{result['totals']['original_complete_delivery']} original complete deliveries."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
