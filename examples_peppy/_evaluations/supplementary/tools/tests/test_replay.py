"""Integrity/isolation regression checks; no numerical dependency required."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "replay_support.py"
sys.path.insert(0, str(MODULE.parent))
spec = importlib.util.spec_from_file_location("peppy_replay_support", MODULE)
assert spec is not None and spec.loader is not None
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class ReplayTests(unittest.TestCase):
    def test_exact_newline_recovery(self):
        original = b"first\r\nsecond\r\n"
        recovered, mode = replay.historical_bytes(
            b"first\nsecond\n", replay.sha256(original)
        )
        self.assertEqual(recovered, original)
        self.assertEqual(mode, "CRLF")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            replay.historical_bytes(b"changed\n", replay.sha256(original))

    def test_inventory_cannot_escape_copy(self):
        for value in ("../outside", "/absolute", "C:/outside", "a/../../outside"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                replay.safe_relative(value)

    def test_historical_mapping_is_trial_specific(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory).resolve()
            mapper = replay.HistoricalPaths(work, "bppm/r01")
            historical = (
                "C:/machine/project/examples_peppy/_evaluations/"
                + replay.CAMPAIGN_ID
                + "/bppm/r01/state/a.json"
            )
            self.assertEqual(mapper.map(historical), str(work / "state/a.json"))
            self.assertEqual(mapper.events[0]["original"], historical)
            other = historical.replace("/bppm/r01/", "/bppm/r02/")
            self.assertEqual(mapper.map(other), other)
            flattened = historical.replace("/" + replay.CAMPAIGN_ID, "")
            self.assertEqual(mapper.map(flattened), str(work / "state/a.json"))
            for unexpected in (
                flattened.replace("/bppm/r01/", "/bppm/r02/"),
                flattened.replace("/bppm/r01/", "/bppm/r010/"),
            ):
                self.assertEqual(mapper.map(unexpected), unexpected)
            with self.assertRaises(ValueError):
                mapper.map(flattened.replace("state/a.json", "../other-trial"))

    def test_preparation_preserves_archive_and_accepts_only_known_imported_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign = root / "campaign"
            trial = campaign / "bppm/r01"
            trial.mkdir(parents=True)
            (trial / "good.py").write_bytes(b"hello\n")
            (trial / "helper.py").write_bytes(b"imported")
            framework = root / "framework"
            workflow = "plugins/pepflow-workflows/skills/example/SKILL.md"
            origin = framework / workflow
            origin.parent.mkdir(parents=True)
            origin.write_bytes(b"skill\r\n")
            old, current = replay.sha256(b"historical"), replay.sha256(b"imported")
            inventory = {
                "good.py": replay.sha256(b"hello\r\n"),
                "helper.py": old,
                "supplementary/approved/" + workflow: replay.sha256(b"skill\r\n"),
                ".ruff_cache/cache": "unused",
            }
            submissions = campaign / "supplementary/submissions"
            submissions.mkdir(parents=True)
            (submissions / "bppm_r01-hashes.json").write_text(json.dumps(inventory))
            baseline = {
                "bppm/r01/helper.py": {
                    "category": "different",
                    "expected_sha256": old,
                    "current_sha256": current,
                }
            }
            report = replay.prepare_trial(
                campaign, framework, "bppm/r01", root / "copy", baseline
            )
            self.assertEqual((trial / "good.py").read_bytes(), b"hello\n")
            self.assertEqual((root / "copy/good.py").read_bytes(), b"hello\r\n")
            self.assertEqual(
                (root / "copy/supplementary/approved" / workflow).read_bytes(),
                b"skill\r\n",
            )
            self.assertEqual(len(report["accepted_imported_sources"]), 1)
            self.assertFalse(report["unresolved_inventory"])
            self.assertEqual(report["missing_cache"], [".ruff_cache/cache"])
            with self.assertRaises(FileExistsError):
                replay.prepare_trial(
                    campaign, framework, "bppm/r01", root / "copy", baseline
                )
            (trial / "helper.py").write_bytes(b"new unreviewed edit")
            report = replay.prepare_trial(
                campaign, framework, "bppm/r01", root / "second", baseline
            )
            self.assertEqual(len(report["unresolved_inventory"]), 1)
            self.assertFalse(report["accepted_imported_sources"])

    def shared_fixture(self, root):
        campaign = root / "campaign"
        trial = campaign / "bppm/r01"
        trial.mkdir(parents=True)
        tools = campaign / "supplementary/tools"
        canonical = tools / "framework/pepflow/__init__.py"
        canonical.parent.mkdir(parents=True)
        historical = b"shared = True\r\n"
        published = historical.replace(b"\r\n", b"\n")
        canonical.write_bytes(historical)
        shared_path = "bppm/r01/supplementary/approved/pepflow/__init__.py"
        manifest = {
            "schema_version": 1,
            "campaign_id": replay.CAMPAIGN_ID,
            "files": [
                {
                    "path": shared_path,
                    "canonical": "supplementary/tools/framework/pepflow/__init__.py",
                    "source_newline": "LF",
                    "bytes": len(published),
                    "sha256": replay.sha256(published),
                }
            ],
        }
        (tools / "shared-files.json").write_text(json.dumps(manifest))
        submissions = campaign / "supplementary/submissions"
        submissions.mkdir(parents=True)
        (submissions / "bppm_r01-hashes.json").write_text(
            json.dumps(
                {
                    "supplementary/approved/pepflow/__init__.py": replay.sha256(
                        historical
                    )
                }
            )
        )
        return campaign, canonical, campaign / shared_path, published, historical

    def test_shared_framework_materializes_only_in_replay_then_restores_historical_bytes(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign, canonical, logical, published, historical = self.shared_fixture(
                root
            )
            report = replay.prepare_trial(
                campaign, canonical.parents[1], "bppm/r01", root / "copy"
            )
            self.assertFalse(logical.exists())
            self.assertEqual(canonical.read_bytes(), historical)
            self.assertEqual(
                (root / "copy/supplementary/approved/pepflow/__init__.py").read_bytes(),
                historical,
            )
            self.assertFalse(report["unresolved_inventory"])
            self.assertEqual(len(report["materialized_shared_files"]), 1)
            self.assertEqual(
                report["materialized_shared_files"][0]["sha256"],
                replay.sha256(published),
            )
            self.assertEqual(len(report["reconstructed_line_endings"]), 1)

    def test_shared_framework_rejects_modified_canonical_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign, canonical, logical, _, _ = self.shared_fixture(root)
            canonical.write_bytes(b"unrecorded framework edit\r\n")
            with self.assertRaises(ValueError):
                replay.prepare_trial(
                    campaign, canonical.parents[1], "bppm/r01", root / "copy"
                )
            self.assertFalse(logical.exists())

    def test_shared_framework_rejects_modified_present_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign, canonical, logical, _, _ = self.shared_fixture(root)
            logical.parent.mkdir(parents=True)
            logical.write_bytes(b"unrecorded per-trial edit\n")
            with self.assertRaises(ValueError):
                replay.prepare_trial(
                    campaign, canonical.parents[1], "bppm/r01", root / "copy"
                )
            self.assertEqual(logical.read_bytes(), b"unrecorded per-trial edit\n")

    def publication_fixture(self, root, expected=None):
        campaign = root / "campaign"
        trial = campaign / "bppm/r01"
        trial.mkdir(parents=True)
        original = b"checkout=OldCheckout\n"
        published = b"checkout=PublicCheckout\n"
        file = trial / "source.py"
        file.write_bytes(published)
        submissions = campaign / "supplementary/submissions"
        submissions.mkdir(parents=True)
        expected = expected or replay.sha256(original.replace(b"\n", b"\r\n"))
        inventory = {"source.py": expected}
        (submissions / "bppm_r01-hashes.json").write_text(json.dumps(inventory))
        record = {
            "path": "bppm/r01/source.py",
            "original_sha256": replay.sha256(original),
            "original_lf_sha256": replay.sha256(original),
            "original_crlf_sha256": replay.sha256(original.replace(b"\n", b"\r\n")),
            "published_sha256": replay.sha256(published),
            "original_bytes": len(original),
            "published_bytes": len(published),
            "replacements": 1,
        }
        return campaign, file, {file.resolve(): record}, expected

    def test_publication_mapping_accepts_only_declared_original_pin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign, file, publication, expected = self.publication_fixture(root)
            published = file.read_bytes()
            report = replay.prepare_trial(
                campaign,
                root / "framework",
                "bppm/r01",
                root / "copy",
                publication=publication,
            )
            self.assertFalse(report["unresolved_inventory"])
            self.assertFalse(report["accepted_imported_sources"])
            self.assertEqual(len(report["verified_publication_files"]), 1)
            accepted = report["accepted_publication_sources"][0]
            self.assertEqual(accepted["historical_sha256"], expected)
            self.assertEqual(accepted["historical_line_endings"], "CRLF")
            self.assertEqual(file.read_bytes(), published)
            self.assertEqual((root / "copy/source.py").read_bytes(), published)
            inventory = json.loads(
                (
                    campaign / "supplementary/submissions/bppm_r01-hashes.json"
                ).read_text()
            )
            self.assertEqual(inventory["source.py"], expected)

    def test_publication_mapping_rejects_modified_export(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign, file, publication, expected = self.publication_fixture(root)
            file.write_bytes(b"tampered after export")
            baseline = {
                "bppm/r01/source.py": {
                    "category": "different",
                    "expected_sha256": expected,
                    "current_sha256": replay.sha256(file.read_bytes()),
                }
            }
            report = replay.prepare_trial(
                campaign,
                root / "framework",
                "bppm/r01",
                root / "copy",
                baseline,
                publication,
            )
            self.assertEqual(len(report["unresolved_inventory"]), 1)
            self.assertFalse(report["accepted_publication_sources"])
            self.assertFalse(report["accepted_imported_sources"])

    def test_publication_mapping_does_not_accept_unrelated_pin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            campaign, file, publication, expected = self.publication_fixture(
                root, replay.sha256(b"unrelated historical version")
            )
            report = replay.prepare_trial(
                campaign,
                root / "framework",
                "bppm/r01",
                root / "copy",
                publication=publication,
            )
            self.assertEqual(len(report["unresolved_inventory"]), 1)
            self.assertFalse(report["accepted_publication_sources"])
            baseline = {
                "bppm/r01/source.py": {
                    "category": "different",
                    "expected_sha256": expected,
                    "current_sha256": replay.sha256(file.read_bytes()),
                }
            }
            opted_in = replay.prepare_trial(
                campaign,
                root / "framework",
                "bppm/r01",
                root / "opted-in",
                baseline,
                publication,
            )
            self.assertFalse(opted_in["unresolved_inventory"])
            self.assertEqual(len(opted_in["accepted_imported_sources"]), 1)
            self.assertFalse(opted_in["accepted_publication_sources"])

    def test_optimized_python_is_refused(self):
        result = subprocess.run(
            [
                sys.executable,
                "-O",
                str(MODULE.with_name("replay.py")),
                "--trial",
                "bppm/r01",
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires active Python assertions", result.stderr)

    def test_write_guard_protects_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / "work"
            work.mkdir()
            code = "\n".join(
                [
                    "import sys",
                    "from pathlib import Path",
                    "sys.path.insert(0, " + repr(str(MODULE.parent)) + ")",
                    "from replay_support import guard_writes",
                    "work = Path(" + repr(str(work)) + ")",
                    "guard_writes(work, work)",
                    "(work / 'allowed.txt').write_text('ok')",
                    "try:",
                    "    (work.parent / 'archive.txt').write_text('bad')",
                    "except PermissionError:",
                    "    pass",
                    "else:",
                    "    raise AssertionError('external write allowed')",
                ]
            )
            result = subprocess.run(
                [sys.executable, "-B", "-c", code], capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((work / "allowed.txt").read_text(), "ok")
            self.assertFalse((root / "archive.txt").exists())


if __name__ == "__main__":
    unittest.main()
