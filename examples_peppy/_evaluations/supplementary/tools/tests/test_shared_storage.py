"""Shared storage preserves submitted bytes and rejects new drift or escape."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
# These sibling tools become importable after the test path setup above.
import audit_archive as audit  # noqa: E402
import shared_storage as storage  # noqa: E402


class SharedStorageTests(unittest.TestCase):
    def fixture(self, directory):
        campaign = Path(directory) / "campaign"
        source = campaign / "supplementary/tools/framework/pepflow/example.py"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"first\r\nsecond\r\n")
        logical = campaign / "ogm/r01/supplementary/approved/pepflow/example.py"
        target = b"first\nsecond\n"
        entry = {
            "path": logical.relative_to(campaign).as_posix(),
            "canonical": source.relative_to(campaign).as_posix(),
            "source_newline": "LF",
            "bytes": len(target),
            "sha256": hashlib.sha256(target).hexdigest(),
        }
        manifest = {
            "schema_version": 1,
            "campaign_id": storage.CAMPAIGN_ID,
            "files": [entry],
        }
        manifest_path = campaign / "supplementary/tools/shared-files.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return campaign, source, logical, target, manifest, manifest_path

    def test_missing_copy_reconstructs_exact_lf_bytes_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, logical, target, manifest, path = self.fixture(directory)
            before = source.read_bytes()
            shared = storage.load_shared_files(campaign)
            self.assertTrue(shared.contains(logical))
            self.assertEqual(shared.read_bytes(logical), target)
            self.assertFalse(logical.exists())
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(set(shared.entries), {logical.resolve()})

    def test_canonical_tampering_is_rejected_both_at_load_and_on_read(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, logical, target, manifest, path = self.fixture(directory)
            shared = storage.load_shared_files(campaign)
            source.write_bytes(b"changed\r\n")
            with self.assertRaisesRegex(
                ValueError, "Shared canonical integrity mismatch"
            ):
                shared.read_bytes(logical)
            with self.assertRaisesRegex(
                ValueError, "Shared canonical integrity mismatch"
            ):
                storage.load_shared_files(campaign)

    def test_present_copy_must_match_instead_of_being_silently_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, logical, target, manifest, path = self.fixture(directory)
            logical.parent.mkdir(parents=True)
            logical.write_bytes(target)
            shared = storage.load_shared_files(campaign)
            self.assertEqual(shared.read_bytes(logical), target)
            logical.write_bytes(source.read_bytes())
            with self.assertRaisesRegex(
                ValueError, "Present shared file integrity mismatch"
            ):
                shared.read_bytes(logical)
            self.assertEqual(logical.read_bytes(), source.read_bytes())

    def test_unlisted_missing_file_stays_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, logical, target, manifest, path = self.fixture(directory)
            shared = storage.load_shared_files(campaign)
            unknown = logical.with_name("not_listed.py")
            self.assertFalse(shared.contains(unknown))
            with self.assertRaises(FileNotFoundError):
                shared.read_bytes(unknown)

    def test_escape_and_nonframework_mappings_are_rejected(self):
        cases = (
            ("path", "../outside.py"),
            ("path", "C:/outside.py"),
            ("path", "/outside.py"),
            ("path", "ogm/r01/notebook.ipynb"),
            ("canonical", "../outside.py"),
            ("canonical", "supplementary/tools/other.py"),
        )
        for field, value in cases:
            with (
                self.subTest(field=field, value=value),
                tempfile.TemporaryDirectory() as directory,
            ):
                campaign, source, logical, target, manifest, path = self.fixture(
                    directory
                )
                manifest["files"][0][field] = value
                path.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaises(ValueError):
                    storage.load_shared_files(campaign)

    def test_invalid_size_hash_conversion_and_duplicate_are_rejected(self):
        cases = (
            ("bytes", 0),
            ("bytes", True),
            ("sha256", "0" * 64),
            ("sha256", "invalid"),
            ("source_newline", "CRLF"),
        )
        for field, value in cases:
            with (
                self.subTest(field=field, value=value),
                tempfile.TemporaryDirectory() as directory,
            ):
                campaign, source, logical, target, manifest, path = self.fixture(
                    directory
                )
                manifest["files"][0][field] = value
                path.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaises(ValueError):
                    storage.load_shared_files(campaign)
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, logical, target, manifest, path = self.fixture(directory)
            manifest["files"].append(dict(manifest["files"][0]))
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                storage.load_shared_files(campaign)

    def test_request_outside_campaign_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, logical, target, manifest, path = self.fixture(directory)
            shared = storage.load_shared_files(campaign)
            outside = Path(directory) / "outside.txt"
            outside.write_text("private", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "leaves its campaign"):
                shared.read_bytes(outside)

    def test_historical_difference_is_not_hidden_by_storage_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, logical, target, manifest, path = self.fixture(directory)
            shared = storage.load_shared_files(campaign)
            audit.fingerprints.cache_clear()
            expected = hashlib.sha256(target).hexdigest()
            self.assertEqual(
                audit.comparison(logical, expected, shared=shared)["category"], "exact"
            )
            original = hashlib.sha256(b"unrecovered historical code").hexdigest()
            result = audit.comparison(logical, original, shared=shared)
            self.assertEqual(result["category"], "different")
            self.assertEqual(result["current_sha256"], expected)
            effective = storage.transformed_bytes(source.read_bytes(), "LF")
            result = audit.comparison(source, expected, data=effective)
            self.assertEqual(result["category"], "exact")
            self.assertEqual(result["current_bytes"], len(target))


if __name__ == "__main__":
    unittest.main()
