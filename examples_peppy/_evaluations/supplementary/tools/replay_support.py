"""Portable, fail-closed execution support for the archived trial notebooks."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import os
import sys
from pathlib import Path, PurePosixPath

CAMPAIGN_ID = "20260923T140754Z_paper5_pgm_sos_6x5_isolation1"
CONDITIONS = ("bppm", "dual_feg", "feg", "ogm", "pgm_with_sos", "pgm_without_sos")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def historical_bytes(data: bytes, expected: str) -> tuple[bytes, str]:
    """Recover line endings only if the entire resulting historical hash matches."""
    variants = ((data, "unchanged"), (data.replace(b"\r\n", b"\n"), "LF"))
    variants += ((variants[1][0].replace(b"\n", b"\r\n"), "CRLF"),)
    for candidate, label in variants:
        if sha256(candidate) == expected:
            return candidate, label
    raise ValueError(f"Historical SHA-256 does not match: expected {expected}, found {sha256(data)}")


def safe_relative(value: str) -> Path:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or ":" in normalized:
        raise ValueError(f"Unsafe archive-relative path: {value}")
    return Path(*path.parts)


def parse_trial(value: str) -> tuple[str, str]:
    match = re.fullmatch(r"(.+)[/_](r0[1-5])", value)
    if not match or match[1] not in CONDITIONS:
        raise ValueError(f"Unknown trial {value!r}; use a condition followed by /r01 through /r05")
    return match[1], match[2]


def prepare_trial(campaign: Path, framework: Path, trial: str, destination: Path,
                  imported_baseline: dict | None = None, publication: dict | None = None,
                  shared_files=None) -> dict:
    """Make an independent copy; never repair or execute inside the archive."""
    condition, repeat = parse_trial(trial)
    source = campaign / condition / repeat
    if destination.exists():
        raise FileExistsError(f"Replay destination already exists: {destination}")
    shutil.copytree(source, destination)
    inventory_path = campaign / "supplementary" / "submissions" / f"{condition}_{repeat}-hashes.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8-sig"))
    report = {"trial": f"{condition}/{repeat}", "inventory_sha256": sha256(inventory_path.read_bytes()),
              "reconstructed_line_endings": [], "restored_workflow": [], "missing_cache": [],
              "unresolved_inventory": [], "accepted_imported_sources": [], "restored_framework": [],
              "verified_publication_files": [], "accepted_publication_sources": [],
              "materialized_shared_files": []}
    # Store identical framework files once in the archive, then restore each
    # trial's exact published bytes before checking historical inventory pins.
    if shared_files is None and (campaign / "supplementary/tools/shared-files.json").is_file():
        from shared_storage import load_shared_files
        shared_files = load_shared_files(campaign)
    if shared_files is not None:
        for archived, record in shared_files.entries.items():
            try:
                relative = archived.relative_to(source.resolve())
            except ValueError:
                continue
            data = shared_files.read_bytes(archived)
            copied = destination / relative
            if copied.is_file():
                if copied.read_bytes() != data:
                    raise ValueError(f"Copied shared file differs from its manifest: {relative.as_posix()}")
                continue
            copied.parent.mkdir(parents=True, exist_ok=True)
            copied.write_bytes(data)
            report["materialized_shared_files"].append({"path": relative.as_posix(),
                "canonical": record["canonical"], "sha256": sha256(data)})
    # The manifest describes a public derivative. It never changes a historical
    # inventory pin or grants acceptance to a different, unrecorded file version.
    publication = publication or {}
    invalid_publication = set()
    for archived, record in publication.items():
        try:
            relative = archived.relative_to(source.resolve())
        except ValueError:
            continue
        copied = destination / relative
        data = copied.read_bytes() if copied.is_file() else None
        normalized = relative.as_posix()
        if (data is None or sha256(data) != record["published_sha256"]
                or len(data) != record["published_bytes"]):
            invalid_publication.add(normalized)
            report["unresolved_inventory"].append({"path": normalized,
                "reason": "Published file does not match publication manifest"})
        else:
            report["verified_publication_files"].append({"path": normalized,
                "published_sha256": record["published_sha256"]})
    for relative, expected in inventory.items():
        path = destination / safe_relative(relative)
        normalized = relative.replace("\\", "/")
        if normalized in invalid_publication:
            continue
        publication_record = publication.get((source / safe_relative(relative)).resolve())
        if publication_record:
            variants = (("original_sha256", "unchanged"), ("original_lf_sha256", "LF"),
                        ("original_crlf_sha256", "CRLF"))
            matched = next((mode for key, mode in variants if publication_record[key] == expected), None)
            if matched is not None:
                report["accepted_publication_sources"].append({"path": normalized,
                    "historical_sha256": expected, "original_sha256": publication_record["original_sha256"],
                    "published_sha256": publication_record["published_sha256"],
                    "historical_line_endings": matched})
                continue
        if not path.exists():
            prefix = "supplementary/approved/"
            if normalized.startswith(prefix + "plugins/pepflow-workflows/"):
                origin = framework / safe_relative(normalized[len(prefix):])
                if origin.is_file():
                    data, ending = historical_bytes(origin.read_bytes(), expected)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                    report["restored_workflow"].append({"path": normalized, "sha256": expected})
                    continue
            if normalized.startswith(".ruff_cache/"):
                report["missing_cache"].append(normalized)
                continue
            report["unresolved_inventory"].append({"path": normalized, "reason": "missing"})
            continue
        try:
            data, ending = historical_bytes(path.read_bytes(), expected)
        except ValueError as exc:
            prefix = "supplementary/approved/"
            if normalized.startswith((prefix + "pepflow/", prefix + "plugins/pepflow-workflows/")):
                origin = framework / safe_relative(normalized[len(prefix):])
                if origin.is_file():
                    try:
                        recovered, ending = historical_bytes(origin.read_bytes(), expected)
                    except ValueError:
                        pass
                    else:
                        path.write_bytes(recovered)
                        report["restored_framework"].append({"path": normalized, "sha256": expected})
                        continue
            baseline = (imported_baseline or {}).get(f"{condition}/{repeat}/{normalized}")
            if (baseline and baseline["category"] == "different"
                    and baseline["expected_sha256"] == expected
                    and baseline["current_sha256"] == sha256(path.read_bytes())):
                report["accepted_imported_sources"].append({"path": normalized,
                    "historical_sha256": expected, "imported_sha256": baseline["current_sha256"]})
            else:
                report["unresolved_inventory"].append({"path": normalized, "reason": str(exc)})
            continue
        if ending != "unchanged":
            path.write_bytes(data)
            report["reconstructed_line_endings"].append({"path": normalized, "mode": ending,
                                                        "sha256": expected})
    return report


class HistoricalPaths:
    """Map only the recorded trial and its framework; leave JSON provenance intact."""

    def __init__(self, work: Path, trial: str):
        self.work = work.resolve()
        condition, repeat = parse_trial(trial)
        self.markers = (f"/examples_peppy/_evaluations/{CAMPAIGN_ID}/{condition}/{repeat}",
                        f"/examples_peppy/_evaluations/{condition}/{repeat}")
        self.events: list[dict] = []

    def map(self, value: str) -> str:
        normalized = value.replace("\\", "/")
        for marker in self.markers:
            index = normalized.lower().find(marker.lower())
            if index >= 0 and (index + len(marker) == len(normalized)
                               or normalized[index + len(marker)] == "/"):
                suffix = normalized[index + len(marker):].lstrip("/")
                mapped = self.work / safe_relative(suffix) if suffix else self.work
                result = str(mapped)
                if result != value:
                    event = {"original": value, "mapped": result}
                    if event not in self.events:
                        self.events.append(event)
                return result
        return value


def guard_writes(work: Path, report_directory: Path) -> None:
    """Refuse writes outside copies and external process/network calls.

    This guards accidental notebook side effects; it is not an OS sandbox.
    """
    roots = (work.resolve(), report_directory.resolve())

    def check_path(value):
        if isinstance(value, int) or value is None:
            return
        path = Path(os.fsdecode(value)).resolve()
        if not any(path.is_relative_to(root) for root in roots):
            raise PermissionError(f"Replay write outside disposable directory refused: {path}")

    def audit(event, args):
        if event == "open":
            mode, flags = args[1], args[2]
            writable = isinstance(mode, str) and any(ch in mode for ch in "wax+")
            writable = writable or (isinstance(flags, int) and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
            if writable:
                check_path(args[0])
        elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.truncate"):
            check_path(args[0])
        elif event in ("os.rename", "os.link", "os.symlink"):
            check_path(args[0])
            check_path(args[1])
        elif event in ("subprocess.Popen", "os.system", "socket.connect", "socket.connect_ex"):
            raise PermissionError(f"External process/network call refused during notebook replay: {event}")

    sys.addaudithook(audit)


# These fixed plans were inspected against the actual submitted r01 notebooks.
# They establish only the stated symbolic scope, not the earlier numeric linkage.
PROOF_PLANS = {
    "feg/r01": {
        "scripts": ["supplementary/b5_symbolic.py"],
        "scope": "Original trial proof script: coefficient derivation, exact step/base/boundary identities and positivity assertions.",
    },
    "ogm/r01": {
        "cells": ["1153c85d", "47c6b3f0", "bb293e6b", "b47d8d28", "a039499d", "c69af3c9"],
        "scope": "Original notebook cells and documented final-cell segment: symbolic step/base/terminal/boundary/N=1/normalization identities. Sign rationale remains prose, not a newly executed sign proof.",
    },
    "pgm_with_sos/r01": {
        "cells": ["f328347c", "91536d07", "8d3ad687", "7d21d817", "cfc42b56", "52c0fd4a"],
        "scope": "Original whole notebook cells: exact coefficient derivation and step/base/terminal/N=1 identities. Signs/domain remain the notebook prose; no saved signs=True flag is used.",
    },
    "pgm_without_sos/r01": {
        "scripts": ["supplementary/verify_b5_native.py", "supplementary/b5_signs.py"],
        "scope": "Original trial proof scripts: step/base/terminal/N=1 component identities, exact SOS polynomial positivity identities and saved-matrix checks.",
    },
}

PROOF_PLANS.update({
    "bppm/r01": {
        "cells": ["1d24a99d", "22825051", "c4b49ec5", "e1056de2", "f5f719fb"],
        "segments": {"1d24a99d": {"sha256": "25a03c055af148c0cc8024cad63703db76353d0869a698e6c4a855be3af3844b", "execute_lines": [[1, 4], [13, 95]], "excluded_lines": [[5, 12]], "reason": "Exclude saved numerical certificate linkage; retain complete symbolic derivation and its assertions."}},
        "scope": "Original symbolic derivation segment and whole step/base/boundary/sign/domain/normalization cells. Numerical-to-symbolic linkage assertions in the excluded prelude are not claimed.",
    },
    "dual_feg/r01": {
        "cells": ["ea083026", "b5549301", "1440d348", "9d1cebb7", "f306ab06"],
        "segments": {"ea083026": {"sha256": "42f544258342aa8fdfbe20681bf0a5258b681fdbc2019b1668d7f882ffbd500c", "execute_lines": [[1, 5], [13, 72]], "excluded_lines": [[6, 12]], "reason": "Exclude saved numerical certificate linkage; retain complete symbolic derivation and its assertions."}},
        "scope": "Original symbolic derivation segment and whole step/base/last/boundary/sign cells. Numerical-to-symbolic linkage assertions in the excluded prelude are not claimed.",
    },
})

PROOF_PLANS["ogm/r01"]["segments"] = {'c69af3c9': {'sha256': '7940eefea81e346493e545fe4443f74c5497d6714602360402e785d2ba4b7c53', 'execute_lines': [[1, 3]], 'excluded_lines': [[4, 5]], 'reason': 'Exclude final narrative claim about earlier numerical verification; keep all symbolic assertions.'}}
