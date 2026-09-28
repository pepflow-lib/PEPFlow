"""Recover archived source bytes from explicitly recorded maintenance edits.

The working source and reconstructed archived source must both match their own
recorded SHA-256 and byte length. Historical inventories are never changed.
Only UTF-8 Python/notebook sources outside the frozen framework are eligible.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, TypedDict

CAMPAIGN_ID = "20260923T140754Z_paper5_pgm_sos_6x5_isolation1"
CONDITIONS = {"ogm", "bppm", "feg", "dual_feg", "pgm_with_sos", "pgm_without_sos"}


class ReverseEdit(TypedDict):
    start: int
    end: int
    text: str


class SourceEdit(TypedDict):
    path: str
    archived_sha256: str
    archived_bytes: int
    current_sha256: str
    current_bytes: int
    edits: list[ReverseEdit]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_path(campaign: Path, value: str) -> Path:
    """Require a canonical relative source path, including symlink confinement."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Source edit paths must be nonempty POSIX relative paths.")
    relative = PurePosixPath(value)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or ":" in value
        or relative.as_posix() != value
        or relative.suffix not in {".py", ".ipynb"}
    ):
        raise ValueError(f"Invalid source edit path: {value!r}")
    path = campaign.joinpath(*relative.parts).resolve()
    if not path.is_relative_to(campaign):
        raise ValueError(f"Source edit path leaves its campaign: {value!r}")
    framework = (campaign / "supplementary/tools/framework").resolve()
    if relative.parts[:3] == (
        "supplementary",
        "tools",
        "framework",
    ) or path.is_relative_to(framework):
        raise ValueError("Source edits cannot alter the frozen framework snapshot.")
    return path


def reconstruct(current: bytes, entry: SourceEdit) -> bytes:
    """Validate current bytes, reverse byte-offset edits, and validate the result."""
    if (
        len(current) != entry["current_bytes"]
        or sha256(current) != entry["current_sha256"]
    ):
        raise ValueError(f"Current source integrity mismatch: {entry['path']}")
    try:
        current.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"Source is not UTF-8: {entry['path']}") from error
    boundaries = {index for index, value in enumerate(current) if value & 0xC0 != 0x80}
    boundaries.add(len(current))
    previous_start, previous_end = -1, 0
    for edit in entry["edits"]:
        if not isinstance(edit, dict) or set(edit) != {"start", "end", "text"}:
            raise ValueError("Source edits require only start, end, and text fields.")
        start, end, text = edit["start"], edit["end"], edit["text"]
        if (
            type(start) is not int
            or type(end) is not int
            or not isinstance(text, str)
            or start < previous_end
            or start <= previous_start
            or start < 0
            or end < start
            or end > len(current)
            or start not in boundaries
            or end not in boundaries
        ):
            raise ValueError(
                f"Invalid or overlapping source edit ranges: {entry['path']}"
            )
        previous_start, previous_end = start, end
    archived = current
    try:
        for edit in reversed(entry["edits"]):
            archived = (
                archived[: edit["start"]]
                + edit["text"].encode("utf-8")
                + archived[edit["end"] :]
            )
        archived.decode("utf-8")
    except UnicodeError as error:
        raise ValueError(f"Archived source is not UTF-8: {entry['path']}") from error
    if (
        len(archived) != entry["archived_bytes"]
        or sha256(archived) != entry["archived_sha256"]
    ):
        raise ValueError(f"Archived source integrity mismatch: {entry['path']}")
    return archived


class SourceEdits:
    def __init__(
        self,
        campaign: Path,
        entries: dict[Path, SourceEdit],
        manifest_path: Path,
        manifest_sha256: str | None = None,
        base_commit: str | None = None,
    ):
        self.campaign = campaign.resolve()
        self.entries = entries
        self.manifest_path = manifest_path.resolve()
        self.manifest_sha256 = manifest_sha256
        self.base_commit = base_commit

    def read_bytes(self, path: Path) -> bytes:
        path = path.resolve()
        if not path.is_relative_to(self.campaign):
            raise ValueError("Requested source leaves its campaign.")
        current = path.read_bytes()
        entry = self.entries.get(path)
        return reconstruct(current, entry) if entry is not None else current

    def identity(self) -> dict[str, Any] | None:
        if self.manifest_sha256 is None:
            return None
        return {
            "file": self.manifest_path.relative_to(self.campaign).as_posix(),
            "sha256": self.manifest_sha256,
            "base_commit": self.base_commit,
            "current_files_verified": len(self.entries),
            "archived_views_verified": len(self.entries),
            "comparison_view": "archived source reconstructed after checking current source bytes",
        }

    def restore_trial(self, source: Path, destination: Path) -> list[dict[str, str]]:
        """Restore only one trial's sources in its disposable replay copy."""
        source, destination = source.resolve(), destination.resolve()
        if not source.is_relative_to(self.campaign):
            raise ValueError("Source trial leaves its campaign.")
        parts = source.relative_to(self.campaign).parts
        if (
            len(parts) != 2
            or parts[0] not in CONDITIONS
            or re.fullmatch(r"r0[1-5]", parts[1]) is None
        ):
            raise ValueError("Source restoration requires one named campaign trial.")
        if destination.is_relative_to(self.campaign):
            raise ValueError(
                "Source restoration destination must be outside the campaign."
            )
        planned = []
        for path, entry in self.entries.items():
            if not path.is_relative_to(source):
                continue
            relative = path.relative_to(source)
            target = (destination / relative).resolve()
            if not target.is_relative_to(destination):
                raise ValueError("Source restoration target leaves its replay copy.")
            archived = self.read_bytes(path)
            copied = target.read_bytes()
            if (
                len(copied) != entry["current_bytes"]
                or sha256(copied) != entry["current_sha256"]
            ):
                raise ValueError(
                    f"Copied current source integrity mismatch: {relative.as_posix()}"
                )
            planned.append((target, archived, entry, relative.as_posix()))
        records = []
        for target, archived, entry, relative in planned:
            target.write_bytes(archived)
            records.append(
                {
                    "path": relative,
                    "current_sha256": entry["current_sha256"],
                    "archived_sha256": entry["archived_sha256"],
                }
            )
        return records


def load_source_edits(campaign: Path, manifest_path: Path | None = None) -> SourceEdits:
    campaign = campaign.resolve()
    optional = manifest_path is None
    manifest_path = (
        manifest_path or campaign / "supplementary/tools/source-edits.json"
    ).resolve()
    if not manifest_path.is_relative_to(campaign):
        raise ValueError("Source edits manifest leaves its campaign.")
    if optional and not manifest_path.exists():
        return SourceEdits(campaign, {}, manifest_path)
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema_version",
        "campaign_id",
        "base_commit",
        "files",
    }:
        raise ValueError("Unsupported source edits manifest fields.")
    if (
        type(manifest["schema_version"]) is not int
        or manifest["schema_version"] != 1
        or manifest["campaign_id"] != CAMPAIGN_ID
    ):
        raise ValueError("Unsupported source edits manifest schema or campaign.")
    if (
        not isinstance(manifest["base_commit"], str)
        or re.fullmatch(r"[0-9a-f]{40}", manifest["base_commit"]) is None
    ):
        raise ValueError("Source edits base_commit must be a full Git commit SHA.")
    if not isinstance(manifest["files"], list):
        raise ValueError("Source edit files must be a list.")
    entries: dict[Path, SourceEdit] = {}
    fields = {
        "path",
        "archived_sha256",
        "archived_bytes",
        "current_sha256",
        "current_bytes",
        "edits",
    }
    for entry in manifest["files"]:
        if not isinstance(entry, dict) or set(entry) != fields:
            raise ValueError("Unsupported source edit record fields.")
        path = source_path(campaign, entry["path"])
        if path in entries:
            raise ValueError(f"Duplicate source edit path: {entry['path']}")
        for key in ("archived_bytes", "current_bytes"):
            if type(entry[key]) is not int or entry[key] < 0:
                raise ValueError("Source byte lengths must be nonnegative integers.")
        for key in ("archived_sha256", "current_sha256"):
            if (
                not isinstance(entry[key], str)
                or re.fullmatch(r"[0-9a-f]{64}", entry[key]) is None
            ):
                raise ValueError("Source hashes must contain 64 lowercase hex digits.")
        if not isinstance(entry["edits"], list):
            raise ValueError("Source edits must be a list.")
        entries[path] = entry
    result = SourceEdits(
        campaign, entries, manifest_path, sha256(raw), manifest["base_commit"]
    )
    for path in entries:
        result.read_bytes(path)
    return result
