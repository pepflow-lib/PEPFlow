"""Maintenance reconstruction preserves original pins and rejects byte drift."""

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
# The tools are siblings of this tests directory, so resolve that path first.
import audit_archive as audit  # noqa: E402
import replay_support as replay  # noqa: E402
import shared_storage as storage  # noqa: E402
import source_edits as edits  # noqa: E402


class SourceEditTests(unittest.TestCase):
    def fixture(
        self, directory, current=b"value: int = 1\n", archived=b"value = 1\r\n"
    ):
        campaign = Path(directory) / "campaign"
        path = campaign / "ogm/r01/helper.py"
        path.parent.mkdir(parents=True)
        path.write_bytes(current)
        entry = {
            "path": path.relative_to(campaign).as_posix(),
            "archived_sha256": edits.sha256(archived),
            "archived_bytes": len(archived),
            "current_sha256": edits.sha256(current),
            "current_bytes": len(current),
            "edits": [
                {"start": 0, "end": len(current), "text": archived.decode("utf-8")}
            ],
        }
        manifest: dict[str, Any] = {
            "schema_version": 1,
            "campaign_id": edits.CAMPAIGN_ID,
            "base_commit": "1" * 40,
            "files": [entry],
        }
        manifest_path = campaign / "supplementary/tools/source-edits.json"
        manifest_path.parent.mkdir(parents=True)
        return campaign, path, current, archived, manifest, manifest_path

    def save(self, manifest, manifest_path):
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def test_optional_absent_manifest_keeps_raw_reads_and_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, path, current, _, _, manifest_path = self.fixture(directory)
            view = edits.load_source_edits(campaign)
            self.assertEqual(view.read_bytes(path), current)
            self.assertEqual(view.entries, {})
            self.assertIsNone(view.identity())
            with self.assertRaises(FileNotFoundError):
                view.read_bytes(campaign / "missing.py")
            with self.assertRaises(FileNotFoundError):
                edits.load_source_edits(campaign, manifest_path)

    def test_exact_unicode_and_newline_roundtrip_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as directory:
            values = self.fixture(
                directory, 'name: str = "?"\n'.encode(), 'name = "?"\r\n'.encode()
            )
            campaign, path, current, archived, manifest, manifest_path = values
            self.save(manifest, manifest_path)
            before = manifest_path.read_bytes()
            view = edits.load_source_edits(campaign)
            self.assertEqual(view.read_bytes(path), archived)
            self.assertEqual(path.read_bytes(), current)
            self.assertEqual(manifest_path.read_bytes(), before)
            identity = view.identity()
            assert identity is not None
            self.assertEqual(identity["current_files_verified"], 1)
            self.assertEqual(identity["archived_views_verified"], 1)
            self.assertEqual(identity["sha256"], edits.sha256(before))

    def test_multiple_byte_offset_edits_apply_in_reverse_order(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, path, _, archived, manifest, manifest_path = self.fixture(
                directory, b"abcd", b"aLONGcY!"
            )
            manifest["files"][0]["edits"] = [
                {"start": 1, "end": 2, "text": "LONG"},
                {"start": 3, "end": 4, "text": "Y"},
                {"start": 4, "end": 4, "text": "!"},
            ]
            self.save(manifest, manifest_path)
            self.assertEqual(
                edits.load_source_edits(campaign).read_bytes(path), archived
            )

    def test_notebook_source_is_allowed_and_unlisted_data_is_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, path, current, archived, manifest, manifest_path = self.fixture(
                directory, b'{"cells": []}\n', b'{"cells":[]}\n'
            )
            notebook = path.with_suffix(".ipynb")
            path.rename(notebook)
            manifest["files"][0]["path"] = notebook.relative_to(campaign).as_posix()
            data = campaign / "records.json"
            data.write_bytes(b'{"result":42}\n')
            self.save(manifest, manifest_path)
            view = edits.load_source_edits(campaign)
            self.assertEqual(view.read_bytes(notebook), archived)
            self.assertEqual(notebook.read_bytes(), current)
            self.assertEqual(view.read_bytes(data), data.read_bytes())

    def test_current_tampering_is_rejected_at_load_and_on_later_read(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, path, _, _, manifest, manifest_path = self.fixture(directory)
            self.save(manifest, manifest_path)
            view = edits.load_source_edits(campaign)
            path.write_bytes(b"changed after load\n")
            with self.assertRaisesRegex(ValueError, "Current source integrity"):
                view.read_bytes(path)
            with self.assertRaisesRegex(ValueError, "Current source integrity"):
                edits.load_source_edits(campaign)

    def test_archived_tampering_is_rejected(self):
        for key, value in [
            ("archived_sha256", "0" * 64),
            ("archived_bytes", 999),
            ("edits", [{"start": 0, "end": 14, "text": "other"}]),
        ]:
            with self.subTest(field=key), tempfile.TemporaryDirectory() as directory:
                campaign, _, _, _, manifest, manifest_path = self.fixture(directory)
                manifest["files"][0][key] = value
                self.save(manifest, manifest_path)
                with self.assertRaises(ValueError):
                    edits.load_source_edits(campaign)

    def test_path_escape_data_and_frozen_snapshot_are_rejected(self):
        for path in [
            "../outside.py",
            "/absolute.py",
            "C:/outside.py",
            "ogm\\r01\\helper.py",
            "ogm//r01/helper.py",
            "records.json",
            "supplementary/tools/framework/pepflow/operator.py",
        ]:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as directory:
                campaign, _, _, _, manifest, manifest_path = self.fixture(directory)
                manifest["files"][0]["path"] = path
                self.save(manifest, manifest_path)
                with self.assertRaises(ValueError):
                    edits.load_source_edits(campaign)

    def test_outside_read_and_manifest_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, _, _, _, manifest, manifest_path = self.fixture(directory)
            self.save(manifest, manifest_path)
            view = edits.load_source_edits(campaign)
            outside = Path(directory) / "outside.py"
            outside.write_bytes(b"outside")
            with self.assertRaises(ValueError):
                view.read_bytes(outside)
            with self.assertRaises(ValueError):
                edits.load_source_edits(campaign, outside)

    def test_duplicate_paths_and_unknown_fields_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, _, _, _, original, manifest_path = self.fixture(directory)
            variants = []
            duplicate = copy.deepcopy(original)
            duplicate["files"].append(copy.deepcopy(duplicate["files"][0]))
            variants.append(duplicate)
            for level in ("manifest", "entry", "edit"):
                variant = copy.deepcopy(original)
                target = variant if level == "manifest" else variant["files"][0]
                if level == "edit":
                    target = target["edits"][0]
                target["unknown"] = True
                variants.append(variant)
            for variant in variants:
                with self.subTest(manifest=variant):
                    self.save(variant, manifest_path)
                    with self.assertRaises(ValueError):
                        edits.load_source_edits(campaign)

    def test_invalid_lengths_hashes_schema_and_base_commit_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, _, _, _, original, manifest_path = self.fixture(directory)
            changes = [
                ("schema_version", True),
                ("schema_version", 2),
                ("campaign_id", "wrong"),
                ("base_commit", "short"),
                ("files", {}),
                ("current_bytes", True),
                ("archived_bytes", -1),
                ("current_sha256", "bad"),
                ("archived_sha256", 123),
                ("edits", {}),
            ]
            for key, value in changes:
                with self.subTest(field=key, value=value):
                    manifest = copy.deepcopy(original)
                    target = manifest if key in manifest else manifest["files"][0]
                    target[key] = value
                    self.save(manifest, manifest_path)
                    with self.assertRaises(ValueError):
                        edits.load_source_edits(campaign)

    def test_invalid_overlapping_and_utf8_split_offsets_are_rejected(self):
        cases = [
            [{"start": -1, "end": 0, "text": ""}],
            [{"start": True, "end": 0, "text": ""}],
            [{"start": 2, "end": 1, "text": ""}],
            [{"start": 0, "end": 100, "text": ""}],
            [{"start": 0, "end": 2, "text": ""}, {"start": 1, "end": 3, "text": ""}],
            [{"start": 2, "end": 3, "text": ""}, {"start": 0, "end": 1, "text": ""}],
            [{"start": 0, "end": 0, "text": ""}, {"start": 0, "end": 0, "text": ""}],
            [{"start": 1, "end": 2, "text": ""}],
            [{"start": 0, "end": 2, "text": 3}],
        ]
        for ranges in cases:
            with self.subTest(edits=ranges), tempfile.TemporaryDirectory() as directory:
                campaign, _, _, _, manifest, manifest_path = self.fixture(
                    directory, "?X".encode(), b"x"
                )
                manifest["files"][0]["edits"] = ranges
                self.save(manifest, manifest_path)
                with self.assertRaises(ValueError):
                    edits.load_source_edits(campaign)

    def test_shared_reader_and_audit_distinguish_physical_from_archived_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, path, current, archived, manifest, manifest_path = self.fixture(
                directory
            )
            self.save(manifest, manifest_path)
            shared = storage.SharedFiles(campaign, {}, campaign / "shared.json")
            self.assertEqual(shared.read_bytes(path), archived)
            result = audit.comparison(path, edits.sha256(archived), shared=shared)
            self.assertEqual(result["category"], "exact")
            self.assertEqual(result["comparison_view"], "archived_source")
            self.assertEqual(result["current_sha256"], edits.sha256(archived))
            self.assertEqual(result["maintained_current_sha256"], edits.sha256(current))
            self.assertEqual(
                audit.comparison(path, edits.sha256(archived))["category"], "different"
            )

    def test_original_publication_manifest_checks_reconstructed_archived_source(self):
        with tempfile.TemporaryDirectory() as directory:
            current = b'name: str = "project"\n'
            archived = b'name = "project"\n'
            original = b'name = "old-project"\n'
            campaign, path, _, _, manifest, manifest_path = self.fixture(
                directory, current, archived
            )
            self.save(manifest, manifest_path)
            publication_path = campaign / "publication.json"
            original_lf = original.replace(b"\r\n", b"\n")
            entry = {
                "path": path.relative_to(campaign).as_posix(),
                "original_sha256": edits.sha256(original),
                "original_lf_sha256": edits.sha256(original_lf),
                "original_crlf_sha256": edits.sha256(
                    original_lf.replace(b"\n", b"\r\n")
                ),
                "published_sha256": edits.sha256(archived),
                "original_bytes": len(original),
                "published_bytes": len(archived),
                "replacements": 1,
                "transformations": ["checkout_directory_basename"],
            }
            publication_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "campaign_id": edits.CAMPAIGN_ID,
                        "files": [entry],
                    }
                ),
                encoding="utf-8",
            )
            before = publication_path.read_bytes()
            shared = storage.SharedFiles(campaign, {}, campaign / "shared.json")
            records = audit.load_publication_manifest(
                campaign, publication_path, shared
            )
            record = audit.comparison(
                path, edits.sha256(original), records, shared=shared
            )
            self.assertEqual(
                record["category"], "matches_before_publication_normalization"
            )
            self.assertEqual(record["maintained_current_sha256"], edits.sha256(current))
            self.assertEqual(publication_path.read_bytes(), before)
            self.assertEqual(path.read_bytes(), current)
            with self.assertRaises(ValueError):
                audit.load_publication_manifest(campaign, publication_path)

    def test_preparation_restores_archived_bytes_before_original_pin_check(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, path, current, archived, manifest, manifest_path = self.fixture(
                directory
            )
            self.save(manifest, manifest_path)
            inventory = campaign / "supplementary/submissions/ogm_r01-hashes.json"
            inventory.parent.mkdir(parents=True)
            inventory.write_text(
                json.dumps({"helper.py": edits.sha256(archived)}), encoding="utf-8"
            )
            destination = Path(directory) / "replay"
            report = replay.prepare_trial(
                campaign, campaign / "framework", "ogm/r01", destination
            )
            self.assertEqual(report["unresolved_inventory"], [])
            self.assertEqual((destination / "helper.py").read_bytes(), archived)
            self.assertEqual(path.read_bytes(), current)
            self.assertEqual(
                report["restored_archived_sources"],
                [
                    {
                        "path": "helper.py",
                        "current_sha256": edits.sha256(current),
                        "archived_sha256": edits.sha256(archived),
                    }
                ],
            )

    def test_restore_is_confined_to_trial_and_refuses_copied_source_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, path, current, _, manifest, manifest_path = self.fixture(
                directory
            )
            extra = copy.deepcopy(manifest["files"][0])
            extra["path"] = "bppm/r01/helper.py"
            second = campaign / extra["path"]
            second.parent.mkdir(parents=True)
            second.write_bytes(current)
            manifest["files"].append(extra)
            self.save(manifest, manifest_path)
            view = edits.load_source_edits(campaign)
            destination = Path(directory) / "replay"
            shutil.copytree(path.parent, destination)
            (destination / "helper.py").write_bytes(b"changed copy")
            with self.assertRaises(ValueError):
                view.restore_trial(path.parent, destination)
            self.assertEqual((destination / "helper.py").read_bytes(), b"changed copy")
            (destination / "helper.py").write_bytes(current)
            self.assertEqual(len(view.restore_trial(path.parent, destination)), 1)
            self.assertEqual(second.read_bytes(), current)
            with self.assertRaises(ValueError):
                view.restore_trial(path.parent, campaign / "bad-destination")
            with self.assertRaises(ValueError):
                view.restore_trial(campaign, destination)

    def test_preparation_rejects_tampering_before_creating_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            campaign, path, _, _, manifest, manifest_path = self.fixture(directory)
            self.save(manifest, manifest_path)
            path.write_bytes(b"tampered")
            destination = Path(directory) / "replay"
            with self.assertRaises(ValueError):
                replay.prepare_trial(
                    campaign, campaign / "framework", "ogm/r01", destination
                )
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
