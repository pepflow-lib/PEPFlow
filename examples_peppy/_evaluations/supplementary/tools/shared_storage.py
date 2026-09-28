"""Read explicitly mapped trial framework files from one verified shared copy.

The manifest describes storage only. It never changes a historical hash pin or
accepts an unlisted missing file. Every logical file is checked byte for byte
against its public SHA-256 and size, whether stored locally or reconstructed.
Other maintained sources use the separately verified archived source view.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath

from source_edits import SourceEdits, load_source_edits

CAMPAIGN_ID = "20260923T140754Z_paper5_pgm_sos_6x5_isolation1"
CONDITIONS = {"ogm", "bppm", "feg", "dual_feg", "pgm_with_sos", "pgm_without_sos"}


def safe_relative(base: Path, value: str) -> Path:
    """Resolve a local manifest path, including a check against symlink escape."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Shared file paths must be nonempty POSIX relative paths.")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or ":" in value
        or path.as_posix() != value
    ):
        raise ValueError(f"Invalid shared file path: {value!r}")
    result = base.joinpath(*path.parts).resolve()
    if not result.is_relative_to(base.resolve()):
        raise ValueError(f"Shared file path leaves its campaign: {value!r}")
    return result


def transformed_bytes(data: bytes, source_newline: str | None) -> bytes:
    """Apply only the explicitly declared storage newline conversion."""
    if source_newline is None:
        return data
    if source_newline == "LF":
        return data.replace(b"\r\n", b"\n")
    raise ValueError(f"Unsupported shared source newline: {source_newline!r}")


class SharedFiles:
    def __init__(
        self,
        campaign: Path,
        entries: dict[Path, dict],
        manifest_path: Path,
        source_edits: SourceEdits | None = None,
    ):
        self.campaign = campaign.resolve()
        self.entries = entries
        self.manifest_path = manifest_path.resolve()
        self.source_edits = source_edits or load_source_edits(campaign)

    def contains(self, path: Path) -> bool:
        return path.resolve() in self.entries

    def read_bytes(self, path: Path) -> bytes:
        logical = path.resolve()
        if not logical.is_relative_to(self.campaign):
            raise ValueError("Requested shared file leaves its campaign.")
        entry = self.entries.get(logical)
        if entry is None:
            return self.source_edits.read_bytes(logical)
        canonical = safe_relative(self.campaign, entry["canonical"])
        data = transformed_bytes(canonical.read_bytes(), entry["source_newline"])
        if (
            len(data) != entry["bytes"]
            or hashlib.sha256(data).hexdigest() != entry["sha256"]
        ):
            raise ValueError(f"Shared canonical integrity mismatch: {entry['path']}")
        if logical.exists():
            present = self.source_edits.read_bytes(logical)
            if present != data:
                raise ValueError(
                    f"Present shared file integrity mismatch: {entry['path']}"
                )
        return data


def load_shared_files(campaign: Path, manifest_path: Path | None = None) -> SharedFiles:
    campaign = campaign.resolve()
    manifest_path = manifest_path or campaign / "supplementary/tools/shared-files.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if (
        manifest.get("schema_version") != 1
        or manifest.get("campaign_id") != CAMPAIGN_ID
    ):
        raise ValueError("Unsupported shared files manifest schema or campaign.")
    if not isinstance(manifest.get("files"), list):
        raise ValueError("Shared files must be a list.")
    entries = {}
    for entry in manifest["files"]:
        if not isinstance(entry, dict):
            raise ValueError("Shared file records must be objects.")
        logical = safe_relative(campaign, entry.get("path"))
        canonical = safe_relative(campaign, entry.get("canonical"))
        parts = PurePosixPath(entry["path"]).parts
        if (
            len(parts) != 6
            or parts[0] not in CONDITIONS
            or re.fullmatch(r"r0[1-5]", parts[1]) is None
            or parts[2:5] != ("supplementary", "approved", "pepflow")
            or not parts[5].endswith(".py")
        ):
            raise ValueError(
                f"Shared path is outside approved trial framework files: {entry['path']}"
            )
        expected_source = "supplementary/tools/framework/pepflow/" + parts[5]
        if entry["canonical"] != expected_source or canonical == logical:
            raise ValueError(f"Unexpected shared canonical path: {entry['canonical']}")
        if entry.get("source_newline") != "LF":
            raise ValueError(
                "Shared framework entries require explicit LF reconstruction."
            )
        if type(entry.get("bytes")) is not int or entry["bytes"] < 0:
            raise ValueError("Shared file byte length must be a nonnegative integer.")
        if (
            not isinstance(entry.get("sha256"), str)
            or re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is None
        ):
            raise ValueError(
                "Shared file SHA-256 must contain 64 lowercase hex digits."
            )
        if logical in entries:
            raise ValueError(f"Duplicate shared file path: {entry['path']}")
        entries[logical] = dict(entry)
    result = SharedFiles(campaign, entries, manifest_path)
    for logical in entries:
        result.read_bytes(logical)
    return result
