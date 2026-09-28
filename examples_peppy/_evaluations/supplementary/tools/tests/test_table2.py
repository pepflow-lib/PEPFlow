"""Accounting regressions for the standalone Table 2 calculator."""

import copy
import importlib.util
import math
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "table2.py"
SPEC = importlib.util.spec_from_file_location("table2", MODULE_PATH)
table2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(table2)


def campaign_fixture():
    """Five deliberately unequal measurements, including an incomplete delivery."""
    runs, blocks, reviews, review_blocks = [], [], [], []
    for condition in table2.CONDITIONS:
        for repeat in range(1, 6):
            attempt = f"{condition}_r{repeat:02d}"
            completed = repeat != 2
            common = {"campaign_id": "test-campaign", "protocol_version": "test-protocol",
                      "attempt_id": attempt, "condition_id": condition, "repetition": str(repeat)}
            runs.append({**common, "started": "True", "usage_status": "complete",
                         "evaluation_usage_status": "complete", "workflow_complete": str(completed),
                         "run_status": "completed" if completed else "error",
                         "attempt_wall_seconds": str(300 * repeat),
                         "block_wall_seconds_sum": str(300 * repeat), "unallocated_seconds": "0",
                         "generation_tokens_total": str(1_000_000 * repeat),
                         "generation_tokens_observed": str(1_000_000 * repeat),
                         "block_tokens_sum": str(1_000_000 * repeat), "unallocated_tokens": "0",
                         "evaluation_wall_seconds": str(2 * repeat),
                         "evaluation_tokens_total": str(10 * repeat),
                         "historical_mathematical_verdict": "PASS" if completed else "NOT_EVALUATED"})
            reviews.append({"attempt_id": attempt, "condition_id": condition, "repetition": repeat,
                            "original_delivery_status": "COMPLETE" if completed else "incomplete",
                            "original_generation_status": "completed" if completed else "error",
                            "mathematical_verdict": "PASS", "original_generation_seconds": 300 * repeat,
                            "original_generation_tokens": 1_000_000 * repeat,
                            "original_review_seconds": 2 * repeat, "original_review_tokens": 10 * repeat})
            for block in table2.BLOCKS:
                blocks.append({**common, "block_id": block, "reached": "True", "usage_status": "complete",
                               "wall_seconds": str(60 * repeat), "tokens_total": str(200_000 * repeat),
                               "tokens_observed": str(200_000 * repeat)})
                review_blocks.append({"attempt_id": attempt, "block_id": block})
    return runs, blocks, {"attempts": reviews, "blocks": review_blocks,
                          "original_protocol": "test-protocol", "original_records_unchanged": True,
                          "original_delivery_not_backfilled": True,
                          "additional_verification_costs": [{"wall_seconds": 999, "tokens_total": 999}]}


class Table2Tests(unittest.TestCase):
    def setUp(self):
        self.runs, self.blocks, self.assessment = campaign_fixture()

    def compute(self):
        return table2.compute_table(self.runs, self.blocks, self.assessment)

    def test_sample_sd_all_attempts_and_separate_accounting(self):
        result = self.compute()
        for row in result["rows"]:
            self.assertEqual(row["attempts"], 5)
            self.assertEqual(row["mathematical_verdict_counts"]["PASS"], 5)
            self.assertEqual(row["original_complete_delivery"], 4)
            self.assertEqual(row["block_minutes"]["B1"]["mean"], 3)
            self.assertAlmostEqual(row["block_minutes"]["B1"]["sample_sd"], math.sqrt(2.5))
            self.assertEqual(row["generation_tokens_millions"]["mean"], 3)
        self.assertEqual(result["totals"]["generation_tokens"], 90_000_000)
        self.assertEqual(result["totals"]["generation_seconds"], 27_000)
        self.assertEqual(result["totals"]["review_seconds"], 180)
        self.assertEqual(result["totals"]["review_tokens"], 900)

    def test_missing_run_is_rejected(self):
        self.runs.pop()
        with self.assertRaisesRegex(table2.InvalidRecords, "30 unique IDs"):
            self.compute()

    def test_duplicate_run_is_rejected(self):
        self.runs.append(copy.deepcopy(self.runs[0]))
        with self.assertRaisesRegex(table2.InvalidRecords, "runs: duplicate"):
            self.compute()

    def test_missing_block_is_rejected(self):
        self.blocks.pop()
        with self.assertRaisesRegex(table2.InvalidRecords, "150 rows"):
            self.compute()

    def test_duplicate_block_is_rejected(self):
        self.blocks.append(copy.deepcopy(self.blocks[0]))
        with self.assertRaisesRegex(table2.InvalidRecords, "blocks: duplicate"):
            self.compute()

    def test_incomplete_cost_coverage_is_rejected(self):
        self.blocks[0]["usage_status"] = "partial"
        with self.assertRaisesRegex(table2.InvalidRecords, "incomplete costs"):
            self.compute()

    def test_token_double_count_is_rejected(self):
        self.blocks[0]["tokens_total"] = self.blocks[0]["tokens_observed"] = "400000"
        with self.assertRaisesRegex(table2.InvalidRecords, "token sum mismatch"):
            self.compute()

    def test_nonfinite_measurement_is_rejected(self):
        self.blocks[0]["wall_seconds"] = "NaN"
        with self.assertRaisesRegex(table2.InvalidRecords, "non-finite"):
            self.compute()

    def test_delivery_cannot_be_backfilled(self):
        self.assessment["attempts"][1]["original_delivery_status"] = "COMPLETE"
        with self.assertRaisesRegex(table2.InvalidRecords, "delivery records disagree"):
            self.compute()

    def test_posthoc_cost_cannot_replace_original_cost(self):
        self.assessment["attempts"][0]["original_review_seconds"] = 999
        with self.assertRaisesRegex(table2.InvalidRecords, "accounting mismatch"):
            self.compute()

    def test_floating_point_partition_roundoff_is_allowed(self):
        self.runs[0]["unallocated_seconds"] = "-4.547473508864641e-13"
        self.compute()


if __name__ == "__main__":
    unittest.main()
