#!/usr/bin/env python3
"""Audit archived bytes and historical pins without executing or changing them.

Run with --check to compare the current findings with archive-audit.json.
Known historical differences are reported, not silently repaired or interpreted
as evidence of a mathematical error. This script uses the standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path, PurePosixPath

CAMPAIGN_ID = "20260923T140754Z_paper5_pgm_sos_6x5_isolation1"
HERE = Path(__file__).resolve().parent
DEFAULT_CAMPAIGN = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
# This module is also loaded by file path; set up its sibling imports first.
from shared_storage import (  # noqa: E402
    SharedFiles,
    load_shared_files,
    transformed_bytes,
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@lru_cache(maxsize=None)
def resolved(path: Path) -> Path:
    return path.resolve()


def relative_file(base: Path, relative: str) -> Path:
    """Resolve an archive-relative path; never read outside its named base."""
    relative = relative.replace("\\", "/")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts or ":" in relative:
        raise ValueError(f"Not an archive-relative path: {relative!r}")
    result = base.joinpath(*parts.parts)
    if not resolved(result).is_relative_to(resolved(base)):
        raise ValueError(f"Path leaves its archive root: {relative!r}")
    return result


@lru_cache(maxsize=None)
def fingerprints(path: Path) -> tuple[str, str, str, int] | None:
    if not path.is_file():
        return None
    data = path.read_bytes()
    lf = data.replace(b"\r\n", b"\n")
    return sha256(data), sha256(lf), sha256(lf.replace(b"\n", b"\r\n")), len(data)


def load_publication_manifest(
    campaign: Path, manifest_path: Path, shared: SharedFiles | None = None
) -> dict[Path, dict]:
    """Validate every exported file before using its documented imported hashes.

    Original hashes describe the imported file immediately before publication;
    they are not assumed to equal a historical submission pin. The archived
    publication view must match its published hash without newline conversion.
    Maintained sources are checked independently before reconstruction.
    """
    resolved.cache_clear()
    fingerprints.cache_clear()
    manifest = read_json(manifest_path)
    if (
        manifest.get("schema_version") != 1
        or manifest.get("campaign_id") != CAMPAIGN_ID
    ):
        raise ValueError("Unsupported publication manifest schema or campaign.")
    if not isinstance(manifest.get("files"), list):
        raise ValueError("Publication manifest files must be a list.")
    records = {}
    hash_fields = (
        "original_sha256",
        "original_lf_sha256",
        "original_crlf_sha256",
        "published_sha256",
    )
    for entry in manifest["files"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ValueError("Publication entries require a relative file path.")
        path = resolved(relative_file(campaign, entry["path"]))
        if path in records:
            raise ValueError(f"Duplicate publication path: {entry['path']}")
        for field in hash_fields:
            if (
                not isinstance(entry.get(field), str)
                or re.fullmatch(r"[0-9a-f]{64}", entry[field]) is None
            ):
                raise ValueError(
                    f"Invalid {field} for publication path: {entry['path']}"
                )
        for field in ("original_bytes", "published_bytes", "replacements"):
            value = entry.get(field)
            if type(value) is not int or value < 0:
                raise ValueError(
                    f"Invalid {field} for publication path: {entry['path']}"
                )
        transformations = entry.get("transformations", [])
        allowed_transformations = {
            "checkout_directory_basename",
            "deduplicated_artifact_fingerprints",
            "storage_support_update",
        }
        if (
            not isinstance(transformations, list)
            or any(not isinstance(item, str) for item in transformations)
            or not transformations
            or len(set(transformations)) != len(transformations)
            or not set(transformations).issubset(allowed_transformations)
        ):
            raise ValueError(
                f"Invalid transformations for publication path: {entry['path']}"
            )
        if ("checkout_directory_basename" in transformations) != (
            entry["replacements"] > 0
        ):
            raise ValueError(
                f"Invalid replacements for publication path: {entry['path']}"
            )
        if "deduplicated_artifact_fingerprints" in transformations:
            allowed_maps = {
                "supplementary/artifact-map.json",
                "posthoc_20260924T024014Z/artifact-map.json",
            }
            if entry["path"] not in allowed_maps:
                raise ValueError(
                    f"Artifact fingerprint update outside known maps: {entry['path']}"
                )
        if "storage_support_update" in transformations:
            allowed_helpers = {
                "supplementary/restore-artifacts.py",
                "posthoc_20260924T024014Z/restore-artifacts.py",
            }
            if entry["path"] not in allowed_helpers:
                raise ValueError(
                    f"Storage support update outside known helpers: {entry['path']}"
                )
        if entry["original_sha256"] == entry["published_sha256"]:
            raise ValueError(
                f"Publication manifest lists an unchanged file: {entry['path']}"
            )
        hashes = effective_fingerprints(path, shared)
        if (
            hashes is None
            or hashes[0] != entry["published_sha256"]
            or hashes[3] != entry["published_bytes"]
        ):
            raise ValueError(f"Published file integrity mismatch: {entry['path']}")
        records[path] = entry
    return records


def effective_fingerprints(
    path: Path, shared: SharedFiles | None = None, data: bytes | None = None
) -> tuple[str, str, str, int] | None:
    if data is None:
        if shared is None:
            return fingerprints(path)
        if not path.is_file() and not shared.contains(path):
            return None
        data = shared.read_bytes(path)
    lf = data.replace(b"\r\n", b"\n")
    return sha256(data), sha256(lf), sha256(lf.replace(b"\n", b"\r\n")), len(data)


def comparison(
    path: Path,
    expected: str | None,
    publication: dict[Path, dict] | None = None,
    *,
    shared: SharedFiles | None = None,
    data: bytes | None = None,
) -> dict:
    hashes = effective_fingerprints(path, shared, data)
    if hashes is None:
        return {
            "expected_sha256": expected,
            "current_sha256": None,
            "category": "missing",
        }
    current, lf_hash, crlf_hash, length = hashes
    category = "no_submission_pin" if expected is None else "different"
    if current == expected:
        category = "exact"
    elif expected is not None:
        if lf_hash == expected:
            category = "matches_after_lf_conversion"
        elif crlf_hash == expected:
            category = "matches_after_crlf_conversion"
    exported = (publication or {}).get(resolved(path))
    if exported is not None:
        if (
            current != exported["published_sha256"]
            or length != exported["published_bytes"]
        ):
            raise ValueError(f"Published file integrity mismatch: {exported['path']}")
        if category == "different":
            if expected == exported["original_sha256"]:
                category = "matches_before_publication_normalization"
            elif expected == exported["original_lf_sha256"]:
                category = (
                    "matches_before_publication_normalization_after_lf_conversion"
                )
            elif expected == exported["original_crlf_sha256"]:
                category = (
                    "matches_before_publication_normalization_after_crlf_conversion"
                )
    record = {
        "expected_sha256": expected,
        "current_sha256": current,
        "current_bytes": length,
        "category": category,
    }
    if shared is not None:
        maintained = shared.source_edits.entries.get(path.resolve())
        if maintained is not None:
            record["comparison_view"] = "archived_source"
            record["maintained_current_sha256"] = maintained["current_sha256"]
            record["maintained_current_bytes"] = maintained["current_bytes"]
    if exported is not None:
        record["publication_original_sha256"] = exported["original_sha256"]
        record["publication_original_bytes"] = exported["original_bytes"]
    return record


def summarize(records: list[dict]) -> dict:
    return {
        "total": len(records),
        "categories": dict(sorted(Counter(r["category"] for r in records).items())),
    }


def audit(
    campaign: Path, framework: Path, publication_manifest: Path | None = None
) -> dict:
    resolved.cache_clear()
    fingerprints.cache_clear()
    publication_path = (
        publication_manifest
        if publication_manifest is not None
        else HERE / "publication-manifest.json"
    )
    shared_path = HERE / "shared-files.json"
    shared = load_shared_files(campaign, shared_path)
    publication = load_publication_manifest(campaign, publication_path, shared)
    manifest = read_json(campaign / "supplementary/manifest.json")
    if manifest["campaign_id"] != CAMPAIGN_ID:
        raise ValueError("This audit is for the shipped thirty-attempt campaign.")
    source_manifest = read_json(HERE / "framework-manifest.json")
    framework_records = []
    declared = {f["path"]: f["sha256"] for f in source_manifest["files"]}
    if declared != manifest["source_hashes"]:
        raise ValueError("Framework manifest differs from campaign source_hashes.")
    if source_manifest["source_revision"] != manifest["framework_revision"]:
        raise ValueError("Framework revision differs from the campaign manifest.")
    for name, expected in sorted(manifest["source_hashes"].items()):
        framework_records.append(
            {
                "path": name,
                **comparison(relative_file(framework, name), expected),
            }
        )

    inventories = {}
    missing_records = []
    notebook_records = []
    shared_records = []
    for pin_path in sorted(
        (campaign / "supplementary/submissions").glob("*-hashes.json")
    ):
        attempt = pin_path.name.removesuffix("-hashes.json")
        condition, repetition = attempt.rsplit("_", 1)
        primary = f"{condition}/{repetition}"
        pins = {p.replace("\\", "/"): h for p, h in read_json(pin_path).items()}
        inventories[attempt] = pins
        for name, expected in sorted(pins.items()):
            primary_path = f"{primary}/{name}"
            file_path = relative_file(campaign, primary_path)
            if name.endswith(".ipynb") and "/" not in name:
                notebook_records.append(
                    {
                        "attempt": attempt,
                        "path": primary_path,
                        **comparison(file_path, expected, publication, shared=shared),
                    }
                )
            if shared.contains(file_path):
                shared_records.append(
                    {
                        "attempt": attempt,
                        "path": primary_path,
                        "canonical": shared.entries[file_path.resolve()]["canonical"],
                        "source_newline": "LF",
                        **comparison(file_path, expected, publication, shared=shared),
                    }
                )
                continue
            if file_path.is_file():
                continue
            record = {
                "attempt": attempt,
                "path": primary_path,
                "expected_sha256": expected,
                "current_sha256": None,
                "category": "missing",
            }
            prefix = "supplementary/approved/"
            if name.startswith(prefix):
                source = name.removeprefix(prefix)
                if source in declared:
                    recovered = comparison(relative_file(framework, source), expected)
                    record["framework_source"] = source
                    record["framework_sha256"] = recovered["current_sha256"]
                    record["category"] = (
                        "recoverable_from_exact_framework_snapshot"
                        if recovered["category"] == "exact"
                        else "framework_snapshot_does_not_match"
                    )
            if name.startswith(".ruff_cache/") and record["category"] == "missing":
                record["category"] = "missing_ruff_cache"
            missing_records.append(record)

    artifact_map = read_json(campaign / "supplementary/artifact-map.json")
    validation_records = []
    map_source_records = []
    for entry in sorted(artifact_map["entries"], key=lambda e: (e["scope"], e["path"])):
        canonical = relative_file(campaign, entry["canonical"])
        source_data = transformed_bytes(
            shared.read_bytes(canonical), entry.get("source_newline")
        )
        map_record = {
            "path": entry["path"],
            "canonical": entry["canonical"],
            **comparison(canonical, entry["sha256"], publication, data=source_data),
        }
        if (
            map_record["category"] == "exact"
            and map_record["current_bytes"] != entry["bytes"]
        ):
            map_record["category"] = "map_byte_length_differs"
        elif map_record["category"] == "matches_before_publication_normalization":
            if map_record["publication_original_bytes"] != entry["bytes"]:
                map_record["category"] = "map_byte_length_differs"
        map_source_records.append(map_record)
        scope = artifact_map["scopes"][entry["scope"]]
        validation_prefix = scope["path"] + "/validation/"
        if not entry["path"].startswith(validation_prefix):
            continue
        name = entry["path"].removeprefix(validation_prefix)
        # A failed preparation is a separate storage scope of the same attempt.
        # Its primary mapping supplies the original submission inventory.
        attempt = scope["primary"].replace("/", "_")
        expected = inventories[attempt].get(name)
        # Historical comparisons belong to the logical primary trial file,
        # even when its current bytes are stored in the shared framework.
        logical_name = scope["primary"] + "/" + name
        logical = relative_file(campaign, logical_name)
        validation_records.append(
            {
                "scope": entry["scope"],
                "attempt": attempt,
                "path": entry["path"],
                "canonical": logical_name,
                **comparison(logical, expected, publication, shared=shared),
            }
        )

    protocol_records = []
    for name, expected in sorted(manifest["protocol_hashes"].items()):
        path = "supplementary/evaluation/protocol/" + name
        protocol_records.append(
            {
                "path": path,
                **comparison(
                    relative_file(campaign, path), expected, publication, shared=shared
                ),
            }
        )

    summaries = {
        "framework_sources": summarize(framework_records),
        "primary_notebooks": summarize(notebook_records),
        "missing_submission_inventory_paths": summarize(missing_records),
        "shared_submission_files": summarize(shared_records),
        "mapped_validation_files": summarize(validation_records),
        "deduplicated_copy_sources": summarize(map_source_records),
        "evaluation_protocol": summarize(protocol_records),
        "publication_normalized_files": {
            "total": len(publication),
            "categories": {"matches_publication_manifest": len(publication)},
        },
    }
    return {
        "schema_version": 3,
        "campaign_id": CAMPAIGN_ID,
        "source_revision": manifest["framework_revision"],
        "path_base": "campaign, except framework_sources and framework_source fields",
        "scope": "Static file-hash, newline, documented source-maintenance and publication-normalization comparison; no notebook execution or mathematical verification.",
        "publication_manifest": {
            "file": publication_path.name,
            "sha256": sha256(publication_path.read_bytes()),
            "validated_files": len(publication),
        },
        "shared_files_manifest": {
            "file": shared_path.name,
            "sha256": sha256(shared_path.read_bytes()),
            "validated_files": len(shared.entries),
        },
        "source_maintenance_manifest": shared.source_edits.identity(),
        "interpretation": [
            "Exact means the effective comparison bytes match the original recorded SHA-256.",
            "Listed maintained source files are checked against their current physical hash and length, then reconstructed and checked against their archived hash and length before historical comparison.",
            "For maintained sources, current_sha256 and current_bytes describe the archived comparison view; maintained_current_sha256 and maintained_current_bytes identify the physical source where recorded.",
            "Newline-conversion matches are calculated in memory; no archived bytes are rewritten.",
            "Publication matches mean the exact published bytes are validated and the manifest's prepublication hash matches the historical pin, optionally after newline conversion.",
            "The publication manifest records imported bytes before export; these are not presumed identical to historical submission bytes.",
            "Different means the effective comparison bytes, newline variants and documented prepublication variants do not match the pin; the historical difference remains unresolved.",
            "The six differing evaluation-protocol files were not recovered at their exact campaign-time hashes.",
            "Shared framework files are reconstructed in memory from the declared canonical file and LF conversion, then checked against their own published byte hash and size.",
            "Sharing storage does not change historical comparisons: every original inventory pin is still checked against its logical trial file.",
            "Repeated workflow copies are represented by one exact framework snapshot; original missing archive paths are not populated.",
            "The failed-preparation scope uses the original inventory of its mapped primary attempt, so its files also occur in another scope.",
            "A matching release baseline preserves these disclosed findings; it does not declare every historical discrepancy resolved.",
        ],
        "summary": summaries,
        "framework_sources": framework_records,
        "primary_notebooks": notebook_records,
        "missing_submission_inventory_paths": missing_records,
        "shared_submission_files": shared_records,
        "mapped_validation_files": validation_records,
        "deduplicated_copy_source_differences": [
            r for r in map_source_records if r["category"] != "exact"
        ],
        "evaluation_protocol": protocol_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, default=DEFAULT_CAMPAIGN)
    parser.add_argument("--framework", type=Path, default=HERE / "framework")
    parser.add_argument(
        "--publication-manifest", type=Path, default=HERE / "publication-manifest.json"
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--write-report", type=Path, metavar="PATH")
    output.add_argument(
        "--check",
        nargs="?",
        const=HERE / "archive-audit.json",
        type=Path,
        metavar="BASELINE",
        help="Fail if findings differ from the shipped or named JSON baseline.",
    )
    args = parser.parse_args()
    try:
        report = audit(
            args.campaign.resolve(),
            args.framework.resolve(),
            args.publication_manifest.resolve(),
        )
        print(json.dumps(report["summary"], indent=2))
        if args.check is not None:
            if report != read_json(args.check):
                print(
                    "FAIL: archive findings differ from the release audit baseline.",
                    file=sys.stderr,
                )
                return 1
            print("PASS: archive findings match the disclosed release audit baseline.")
        if args.write_report is not None:
            destination = args.write_report.resolve()
            if (
                destination.is_relative_to(args.campaign.resolve())
                and destination != HERE / "archive-audit.json"
            ):
                raise ValueError(
                    "Write audit reports outside the experimental records or to the shipped tools/archive-audit.json."
                )
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
            print(f"Wrote {destination}")
    except (OSError, ValueError, KeyError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
