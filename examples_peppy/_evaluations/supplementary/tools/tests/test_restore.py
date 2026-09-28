"""Shared-source restoration checks for both archived evaluator restore tools."""

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

CAMPAIGN = Path(__file__).resolve().parents[3]
CAMPAIGN_ID = "20260923T140754Z_paper5_pgm_sos_6x5_isolation1"
POSTHOC = "posthoc_20260924T024014Z"
HELPERS = {
    "original": CAMPAIGN / "supplementary/restore-artifacts.py",
    "posthoc": CAMPAIGN / POSTHOC / "restore-artifacts.py",
}


def module_for(kind):
    spec = importlib.util.spec_from_file_location("restore_" + kind, HELPERS[kind])
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(root, kind):
    module = module_for(kind)
    campaign = root / "campaign"
    canonical = campaign / "supplementary/tools/framework/pepflow/__init__.py"
    canonical.parent.mkdir(parents=True)
    raw = b"first = 1\r\nsecond = 2\r\n"
    expected = raw.replace(b"\r\n", b"\n")
    canonical.write_bytes(raw)
    data: dict[str, Any]
    if kind == "original":
        scope = "bppm_r01"
        scope_relative = "supplementary/evaluation/" + scope
        mapped_relative = scope_relative + "/supplementary/approved/pepflow/__init__.py"
        map_path = campaign / "supplementary/artifact-map.json"
        data = {
            "schema_version": 1,
            "campaign_id": CAMPAIGN_ID,
            "created_at": "2026-09-28T00:00:00Z",
            "scopes": {scope: {"path": scope_relative, "primary": "bppm/r01"}},
        }
    else:
        scope = "feg_r03"
        scope_relative = POSTHOC + "/" + scope
        mapped_relative = (
            scope_relative + "/validation/supplementary/approved/pepflow/__init__.py"
        )
        map_path = campaign / POSTHOC / "artifact-map.json"
        data = {"schema_version": 1, "campaign_id": CAMPAIGN_ID}
        module.CAMPAIGN = campaign
        module.HERE = map_path.parent
    live = campaign / scope_relative
    live.mkdir(parents=True)
    (live / "review.txt").write_bytes(b"retained review\n")
    entry = {
        "scope": scope,
        "path": mapped_relative,
        "canonical": canonical.relative_to(campaign).as_posix(),
        "source_newline": "LF",
        "bytes": len(expected),
        "sha256": hashlib.sha256(expected).hexdigest(),
    }
    data["entries"] = [entry]
    map_path.parent.mkdir(parents=True, exist_ok=True)
    output = root / "restored"

    def save():
        map_path.write_text(json.dumps(data), encoding="utf-8")

    def restore():
        save()
        if kind == "original":
            return module.restore(map_path, [scope], output)
        return module.restore(scope, output)

    return dict(
        module=module,
        campaign=campaign,
        canonical=canonical,
        raw=raw,
        expected=expected,
        entry=entry,
        live=live,
        output=output,
        target=output / mapped_relative,
        review=output / scope_relative / "review.txt",
        restore=restore,
    )


class RestoreTests(unittest.TestCase):
    def test_shared_crlf_source_restores_exact_lf_and_retained_review(self):
        for kind in HELPERS:
            with self.subTest(helper=kind), tempfile.TemporaryDirectory() as directory:
                case = fixture(Path(directory), kind)
                case["restore"]()
                self.assertEqual(case["target"].read_bytes(), case["expected"])
                self.assertEqual(case["review"].read_bytes(), b"retained review\n")
                self.assertEqual(case["canonical"].read_bytes(), case["raw"])
                self.assertFalse((case["campaign"] / case["entry"]["path"]).exists())
                before = {
                    p.relative_to(case["output"]): p.read_bytes()
                    for p in case["output"].rglob("*")
                    if p.is_file()
                }
                case["restore"]()
                after = {
                    p.relative_to(case["output"]): p.read_bytes()
                    for p in case["output"].rglob("*")
                    if p.is_file()
                }
                self.assertEqual(before, after)

    def test_bad_shared_hash_refused_before_writes(self):
        for kind in HELPERS:
            with self.subTest(helper=kind), tempfile.TemporaryDirectory() as directory:
                case = fixture(Path(directory), kind)
                case["entry"]["sha256"] = "0" * 64
                with self.assertRaises(case["module"].Refusal):
                    case["restore"]()
                self.assertFalse(case["output"].exists())

    def test_unknown_newline_mode_refused_before_writes(self):
        for kind in HELPERS:
            with self.subTest(helper=kind), tempfile.TemporaryDirectory() as directory:
                case = fixture(Path(directory), kind)
                case["entry"]["source_newline"] = "CRLF"
                with self.assertRaises(case["module"].Refusal):
                    case["restore"]()
                self.assertFalse(case["output"].exists())

    def test_newline_conversion_outside_framework_refused_before_writes(self):
        for kind in HELPERS:
            with self.subTest(helper=kind), tempfile.TemporaryDirectory() as directory:
                case = fixture(Path(directory), kind)
                case["entry"]["canonical"] = "bppm/r01/other.py"
                with self.assertRaises(case["module"].Refusal):
                    case["restore"]()
                self.assertFalse(case["output"].exists())

    def test_conflicting_destination_refused_before_any_other_write(self):
        for kind in HELPERS:
            with self.subTest(helper=kind), tempfile.TemporaryDirectory() as directory:
                case = fixture(Path(directory), kind)
                case["target"].parent.mkdir(parents=True)
                case["target"].write_bytes(b"keep this existing file\n")
                with self.assertRaises(case["module"].Refusal):
                    case["restore"]()
                self.assertEqual(
                    case["target"].read_bytes(), b"keep this existing file\n"
                )
                self.assertFalse(case["review"].exists())

    def test_canonical_traversal_refused_before_writes(self):
        for kind in HELPERS:
            with self.subTest(helper=kind), tempfile.TemporaryDirectory() as directory:
                case = fixture(Path(directory), kind)
                case["entry"]["canonical"] = "../outside.py"
                with self.assertRaises(case["module"].Refusal):
                    case["restore"]()
                self.assertFalse(case["output"].exists())

    def test_planned_parent_file_conflict_refused_before_writes(self):
        for kind in HELPERS:
            with self.subTest(helper=kind), tempfile.TemporaryDirectory() as directory:
                case = fixture(Path(directory), kind)
                prefix = case["live"] / ("validation" if kind == "posthoc" else "")
                prefix.mkdir(parents=True, exist_ok=True)
                (prefix / "supplementary").write_bytes(
                    b"retained file blocks mapped directory\n"
                )
                with self.assertRaises(case["module"].Refusal):
                    case["restore"]()
                self.assertFalse(case["output"].exists())


if __name__ == "__main__":
    unittest.main()
