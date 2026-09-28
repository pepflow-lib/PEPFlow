#!/usr/bin/env python3
"""Restore exact post-hoc validation copies from frozen primary attempts."""

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

# Standalone restoration uses the common, hash-checked source reader.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from examples_peppy._evaluations.supplementary.tools.source_edits import (  # noqa: E402
    SourceEdits,
    load_source_edits,
)

HERE = Path(__file__).absolute().parent
CAMPAIGN = HERE.parent
CAMPAIGN_ID = "20260923T140754Z_paper5_pgm_sos_6x5_isolation1"
CASES = {"feg_r03": "feg/r03", "pgm_without_sos_r02": "pgm_without_sos/r02"}


class Refusal(ValueError):
    pass


def parts(value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise Refusal(f"Unsafe relative path: {value!r}")
    result = value.split("/")
    reserved = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    reserved.update(f"{kind}{n}" for kind in ("COM", "LPT") for n in range(1, 10))
    for p in result:
        if (
            p in {"", ".", ".."}
            or p.endswith((" ", "."))
            or any(ord(c) < 32 or c in '<>:"|?*' for c in p)
            or p.split(".")[0].upper() in reserved
        ):
            raise Refusal(f"Unsafe path component: {p!r}")
    return tuple(result)


def check_path(path):
    for p in (*reversed(path.parents), path):
        try:
            info = p.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 1024:
            raise Refusal(f"Link or junction: {p}")
        if p != path and not stat.S_ISDIR(info.st_mode):
            raise Refusal(f"Non-directory ancestor: {p}")


def source_bytes(path, source_newline=None, source_edits: SourceEdits | None = None):
    check_path(path)
    if not path.is_file() or not stat.S_ISREG(path.lstat().st_mode):
        raise Refusal(f"Missing regular file: {path}")
    before = path.stat()
    data = source_edits.read_bytes(path) if source_edits else path.read_bytes()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise Refusal(f"File changed during read: {path}")
    if source_newline == "LF":
        data = data.replace(b"\r\n", b"\n")
    elif source_newline is not None:
        raise Refusal("Unsupported source newline conversion")
    return data


def digest(path, source_newline=None, source_edits: SourceEdits | None = None):
    data = source_bytes(path, source_newline, source_edits)
    return len(data), hashlib.sha256(data).hexdigest()


def load_entries():
    map_path = HERE / "artifact-map.json"
    check_path(map_path)
    info = json.loads(map_path.read_text(encoding="utf-8"))
    if info.get("schema_version") != 1 or info.get("campaign_id") != CAMPAIGN_ID:
        raise Refusal("Unexpected map version or campaign")
    entries = info.get("entries")
    if not isinstance(entries, list):
        raise Refusal("Missing map entries")
    seen = set()
    parsed = []
    for entry in entries:
        dst = parts(entry["path"])
        src = parts(entry["canonical"])
        source_newline = entry.get("source_newline")
        shared = (
            len(dst) >= 7
            and src[:4] == ("supplementary", "tools", "framework", "pepflow")
            and dst[3:6] == ("supplementary", "approved", "pepflow")
            and src[4:] == dst[6:]
            and source_newline == "LF"
        )
        if source_newline not in (None, "LF") or (
            source_newline is not None and not shared
        ):
            raise Refusal("Invalid shared-source newline conversion")
        if (
            len(dst) < 4
            or dst[0] != HERE.name
            or dst[1] not in CASES
            or dst[2] != "validation"
            or (not shared and src[:2] != tuple(CASES[dst[1]].split("/")))
            or len(src) < 3
        ):
            raise Refusal(f"Unexpected map path: {entry['path']}")
        size, sha = entry["bytes"], entry["sha256"]
        if (
            type(size) is not int
            or size < 0
            or not isinstance(sha, str)
            or len(sha) != 64
            or any(c not in "0123456789abcdef" for c in sha)
        ):
            raise Refusal(f"Invalid fingerprint: {entry['path']}")
        folded = "/".join(dst).casefold()
        if folded in seen:
            raise Refusal(f"Duplicate Windows destination: {entry['path']}")
        seen.add(folded)
        parsed.append((dst[1], dst, src, (size, sha), source_newline))
    canon = {"/".join(src).casefold() for _, _, src, _, _ in parsed}
    if canon & seen:
        raise Refusal("Canonical source is also omitted")
    return parsed


def plan(case, output, source_edits: SourceEdits | None = None):
    entries = [
        (dst, CAMPAIGN.joinpath(*src), expected, source_newline)
        for selected, dst, src, expected, source_newline in load_entries()
        if selected == case
    ]
    if not entries:
        raise Refusal(f"No entries for {case}")
    mapped_paths = {"/".join(dst).casefold() for dst, _, _, _ in entries}
    result = []
    if output != CAMPAIGN:
        scope = HERE / case
        check_path(scope)
        for directory, dirs, files in os.walk(scope, followlinks=False):
            for name in dirs + files:
                check_path(Path(directory) / name)
            for name in files:
                source = Path(directory) / name
                relative = parts(source.relative_to(CAMPAIGN).as_posix())
                if "/".join(relative).casefold() in mapped_paths:
                    continue
                result.append(
                    (relative, source, digest(source, source_edits=source_edits), None)
                )
    result.extend(entries)
    seen = set()
    for dst, _, _, _ in result:
        folded = "/".join(dst).casefold()
        if folded in seen:
            raise Refusal(f"Case-colliding destination: {'/'.join(dst)}")
        seen.add(folded)
    for dst, _, _, _ in result:
        if any("/".join(dst[:n]).casefold() in seen for n in range(1, len(dst))):
            raise Refusal("Planned file is an ancestor of another destination")
    return result, len(entries)


def restore(case, output):
    check_path(CAMPAIGN)
    check_path(output)
    src_root = str(CAMPAIGN).casefold().rstrip("\\/")
    dst_root = str(output).casefold().rstrip("\\/")
    if output != CAMPAIGN and (
        dst_root.startswith(src_root + os.sep) or src_root.startswith(dst_root + os.sep)
    ):
        raise Refusal("Fresh output overlaps the campaign")
    source_edits = load_source_edits(CAMPAIGN)
    items, mapped = plan(case, output, source_edits)
    pending = []
    for relative, source, expected, source_newline in items:
        if digest(source, source_newline, source_edits) != expected:
            raise Refusal(f"Source differs from recorded bytes: {source}")
        target = output.joinpath(*relative)
        check_path(target)
        if target.exists():
            if digest(target) != expected:
                raise Refusal(f"Conflicting destination: {target}")
        else:
            pending.append((source, target, expected, source_newline))
    for source, target, expected, source_newline in pending:
        payload = source_bytes(source, source_newline, source_edits)
        if (len(payload), hashlib.sha256(payload).hexdigest()) != expected:
            raise Refusal(f"Source changed before copy: {source}")
        check_path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(payload)
        if digest(target) != expected:
            raise Refusal(f"Restored hash mismatch: {target}")
    return {
        "case": case,
        "mapped": mapped,
        "copied": len(pending),
        "already_present": len(items) - len(pending),
        "output": str(output),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(CASES), required=True)
    parser.add_argument("--out", type=Path, help="Fresh campaign-root directory")
    args = parser.parse_args()
    output = args.out.absolute() if args.out else CAMPAIGN
    try:
        print(json.dumps(restore(args.case, output), indent=2))
    except Refusal as error:
        parser.exit(2, f"Refused: {error}\n")


if __name__ == "__main__":
    main()
