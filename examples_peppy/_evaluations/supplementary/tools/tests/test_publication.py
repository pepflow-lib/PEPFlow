"""Publication manifests explain export changes without hiding source drift."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "audit_archive.py"
spec = importlib.util.spec_from_file_location("peppy_publication_audit", MODULE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        audit.fingerprints.cache_clear()
        audit.resolved.cache_clear()

    def fixture(self, root, original=b"old-project\nvalue\n", published=b"project\nvalue\n"):
        campaign = root / "campaign"
        source = campaign / "trial/file.txt"
        source.parent.mkdir(parents=True)
        source.write_bytes(published)
        lf = original.replace(b"\r\n", b"\n")
        entry = {
            "path": "trial/file.txt",
            "original_sha256": audit.sha256(original),
            "original_lf_sha256": audit.sha256(lf),
            "original_crlf_sha256": audit.sha256(lf.replace(b"\n", b"\r\n")),
            "published_sha256": audit.sha256(published),
            "original_bytes": len(original),
            "published_bytes": len(published),
            "replacements": 1,
            "transformations": ["checkout_directory_basename"],
        }
        manifest = {"schema_version": 1, "campaign_id": audit.CAMPAIGN_ID, "files": [entry]}
        manifest_path = root / "publication-manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return campaign, source, manifest_path, manifest

    def test_export_match_is_distinct_from_exact_historical_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, manifest_path, manifest = self.fixture(Path(directory))
            records = audit.load_publication_manifest(campaign, manifest_path)
            entry = manifest["files"][0]
            result = audit.comparison(source, entry["original_sha256"], records)
            self.assertEqual(result["category"], "matches_before_publication_normalization")
            self.assertEqual(result["current_sha256"], entry["published_sha256"])
            self.assertNotEqual(result["current_sha256"], result["expected_sha256"])
            self.assertEqual(result["publication_original_bytes"], entry["original_bytes"])
            self.assertEqual(audit.comparison(source, entry["published_sha256"], records)["category"], "exact")

    def test_prepublication_newline_variants_are_explicit(self):
        cases = (
            (b"old-project\nvalue\n", "original_crlf_sha256", "crlf"),
            (b"old-project\r\nvalue\r\n", "original_lf_sha256", "lf"),
        )
        for original, field, ending in cases:
            with self.subTest(ending=ending), tempfile.TemporaryDirectory() as directory:
                campaign, source, manifest_path, manifest = self.fixture(Path(directory), original)
                records = audit.load_publication_manifest(campaign, manifest_path)
                result = audit.comparison(source, manifest["files"][0][field], records)
                self.assertEqual(result["category"], "matches_before_publication_normalization_after_" + ending + "_conversion")

    def test_unexplained_historical_difference_stays_different(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, manifest_path, manifest = self.fixture(Path(directory))
            records = audit.load_publication_manifest(campaign, manifest_path)
            self.assertEqual(audit.comparison(source, audit.sha256(b"unrecovered historical source"), records)["category"], "different")
            self.assertEqual(audit.comparison(source, None, records)["category"], "no_submission_pin")

    def test_new_export_drift_and_newline_drift_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, manifest_path, manifest = self.fixture(Path(directory))
            audit.load_publication_manifest(campaign, manifest_path)
            for changed in (b"unreviewed change", b"project\r\nvalue\r\n"):
                with self.subTest(changed=changed):
                    source.write_bytes(changed)
                    with self.assertRaisesRegex(ValueError, "Published file integrity mismatch"):
                        audit.load_publication_manifest(campaign, manifest_path)
            source.unlink()
            with self.assertRaisesRegex(ValueError, "Published file integrity mismatch"):
                audit.load_publication_manifest(campaign, manifest_path)

    def test_manifest_cannot_trust_its_own_published_length(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, manifest_path, manifest = self.fixture(Path(directory))
            manifest["files"][0]["published_bytes"] += 1
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Published file integrity mismatch"):
                audit.load_publication_manifest(campaign, manifest_path)

    def test_duplicate_and_outside_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, manifest_path, manifest = self.fixture(Path(directory))
            entry = manifest["files"][0]
            duplicate = dict(entry, path="trial/./file.txt")
            manifest["files"].append(duplicate)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate publication path"):
                audit.load_publication_manifest(campaign, manifest_path)
            for relative in ("../outside", "/absolute", "C:/outside"):
                with self.subTest(relative=relative):
                    manifest["files"] = [dict(entry, path=relative)]
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Not an archive-relative path"):
                        audit.load_publication_manifest(campaign, manifest_path)

    def test_invalid_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, manifest_path, manifest = self.fixture(Path(directory))
            entry = manifest["files"][0]
            for field, value in (("original_sha256", "not a hash"), ("original_bytes", -1), ("replacements", 0), ("replacements", True)):
                with self.subTest(field=field, value=value):
                    manifest["files"] = [dict(entry, **{field: value})]
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Invalid"):
                        audit.load_publication_manifest(campaign, manifest_path)

    def test_map_fingerprint_updates_can_have_zero_name_replacements(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, manifest_path, manifest = self.fixture(Path(directory))
            entry = manifest["files"][0]
            entry["replacements"] = 0
            entry["transformations"] = ["deduplicated_artifact_fingerprints"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside known maps"):
                audit.load_publication_manifest(campaign, manifest_path)
            entry["path"] = "supplementary/artifact-map.json"
            destination = campaign / entry["path"]
            destination.parent.mkdir(parents=True)
            source.rename(destination)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            records = audit.load_publication_manifest(campaign, manifest_path)
            self.assertEqual(records[destination.resolve()]["replacements"], 0)
            self.assertEqual(audit.comparison(destination, entry["original_sha256"], records)["category"], "matches_before_publication_normalization")
            entry["transformations"] = ["unknown_export_change"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Invalid transformations"):
                audit.load_publication_manifest(campaign, manifest_path)

    def test_storage_support_updates_are_limited_to_restore_helpers(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, source, manifest_path, manifest = self.fixture(Path(directory))
            entry = manifest["files"][0]
            entry["replacements"] = 0
            entry["transformations"] = ["storage_support_update"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside known helpers"):
                audit.load_publication_manifest(campaign, manifest_path)
            entry["path"] = "supplementary/restore-artifacts.py"
            destination = campaign / entry["path"]
            destination.parent.mkdir(parents=True)
            source.rename(destination)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            records = audit.load_publication_manifest(campaign, manifest_path)
            result = audit.comparison(destination, entry["original_sha256"], records)
            self.assertEqual(result["category"], "matches_before_publication_normalization")
            self.assertEqual(records[destination.resolve()]["replacements"], 0)

    def test_direct_matches_and_missing_files_keep_their_meaning(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "file.txt"
            source.write_bytes(b"unchanged\n")
            self.assertEqual(audit.comparison(source, audit.sha256(b"unchanged\n"))["category"], "exact")
            self.assertEqual(audit.comparison(source, audit.sha256(b"unchanged\r\n"))["category"], "matches_after_crlf_conversion")
            missing = source.with_name("missing.txt")
            self.assertEqual(audit.comparison(missing, audit.sha256(b"anything"))["category"], "missing")


if __name__ == "__main__":
    unittest.main()
