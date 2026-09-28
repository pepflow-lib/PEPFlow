#!/usr/bin/env python3
"""Restore selected evaluator copies without changing primary artifacts.

Fresh destinations receive retained scope files and mapped omissions. In-place
restoration recreates only mapped omissions. Preflight is complete before any
writes; filesystem operations are not an atomic transaction against other writers.
"""

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

# Standalone restoration uses the common, hash-checked source reader.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from examples_peppy._evaluations.supplementary.tools.source_edits import (  # noqa: E402
    SourceEdits,
    load_source_edits,
)


class Refusal(ValueError):
    """An unsafe path, changed source, or conflicting destination."""


def relative(value, label):
    if not isinstance(value, str) or not value or "\\" in value:
        raise Refusal(f"{label}: expected a nonempty forward-slash relative path")
    parts = value.split("/")
    reserved = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
    reserved.update(f"{kind}{n}" for kind in ("COM", "LPT") for n in "123456789¹²³")
    for part in parts:
        if (
            part in {"", ".", ".."}
            or part.endswith((" ", "."))
            or any(ord(c) < 32 or c in '<>:"|?*' for c in part)
            or part.split(".")[0].rstrip(" ").upper() in reserved
        ):
            raise Refusal(f"{label}: unsafe Windows path component {part!r}")
    return tuple(parts)


def key(parts):
    return "/".join(parts).casefold()


def within(parts, root):
    return len(parts) >= len(root) and key(parts[: len(root)]) == key(root)


def register(parts, names):
    """Reject differently cased spellings of any file or directory component."""
    for count in range(1, len(parts) + 1):
        prefix = parts[:count]
        folded = key(prefix)
        if folded in names and names[folded] != prefix:
            raise Refusal(f"Windows case collision: {'/'.join(prefix)}")
        names[folded] = prefix


def absolute(value):
    return Path(os.path.abspath(os.fspath(value)))


def safe_path(path):
    """Check existing ancestors without following symlinks or junctions."""
    chain = list(reversed(path.parents)) + [path]
    for index, part in enumerate(chain):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 1024:
            raise Refusal(f"Symlink or reparse point: {part}")
        if index < len(chain) - 1 and not stat.S_ISDIR(info.st_mode):
            raise Refusal(f"Non-directory ancestor: {part}")
        if part.parent != part:
            matches = [
                name
                for name in os.listdir(part.parent)
                if name.casefold() == part.name.casefold()
            ]
            if any(name != part.name for name in matches):
                raise Refusal(f"Existing Windows case collision: {part}")


def overlap(first, second):
    a, b = (
        os.path.normcase(str(first)).casefold(),
        os.path.normcase(str(second)).casefold(),
    )
    separator = os.sep
    return (
        a == b
        or a.startswith(b.rstrip(separator) + separator)
        or b.startswith(a.rstrip(separator) + separator)
    )


def inventory(root):
    """Read a tree, rejecting every link, special file, and case collision."""
    safe_path(root)
    if not root.is_dir():
        raise Refusal(f"Scope directory is unavailable: {root}")
    files, names = {}, {}
    for directory, dirs, filenames in os.walk(root, followlinks=False):
        parent = Path(directory)
        for name in dirs + filenames:
            item = parent / name
            parts = relative(item.relative_to(root).as_posix(), "Existing scope path")
            register(parts, names)
            info = item.lstat()
            if (
                stat.S_ISLNK(info.st_mode)
                or getattr(info, "st_file_attributes", 0) & 1024
            ):
                raise Refusal(f"Symlink or reparse point in scope: {item}")
            if name in dirs:
                if not stat.S_ISDIR(info.st_mode):
                    raise Refusal(f"Unexpected directory type: {item}")
            elif stat.S_ISREG(info.st_mode):
                files[parts] = item
            else:
                raise Refusal(f"Special file in scope: {item}")
    return files, names


def fingerprint(path, source_newline=None, source_edits: SourceEdits | None = None):
    safe_path(path)
    if not path.is_file():
        raise Refusal(f"Source or destination is not a regular file: {path}")
    before = path.stat()
    payload = source_edits.read_bytes(path) if source_edits else path.read_bytes()
    if source_newline == "LF":
        payload = payload.replace(b"\r\n", b"\n")
    elif source_newline is not None:
        raise Refusal("Unsupported source newline conversion")
    size = len(payload)
    digest = hashlib.sha256(payload)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (
        after.st_size,
        after.st_mtime_ns,
        after.st_ino,
    ):
        raise Refusal(f"File changed while reading: {path}")
    return size, digest.hexdigest()


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise Refusal(f"Duplicate JSON key: {name}")
        result[name] = value
    return result


def read_map(path):
    safe_path(path)
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle, object_pairs_hook=unique_object)
    if (
        not isinstance(data, dict)
        or type(data.get("schema_version")) is not int
        or data["schema_version"] != 1
        or not isinstance(data.get("scopes"), dict)
        or not data["scopes"]
        or not isinstance(data.get("entries"), list)
        or not all(
            isinstance(data.get(k), str) and data[k]
            for k in ("campaign_id", "created_at")
        )
    ):
        raise Refusal("Unsupported or malformed artifact map")
    scopes, entries, destinations, names = {}, [], set(), {}
    for scope, item in data["scopes"].items():
        if len(relative(scope, "Scope ID")) != 1 or not isinstance(item, dict):
            raise Refusal(f"Invalid scope: {scope}")
        parts = relative(item.get("path"), "Scope path")
        primary = relative(item.get("primary"), "Primary path")
        if parts != ("supplementary", "evaluation", scope):
            raise Refusal(f"Scope is not its declared evaluation directory: {scope}")
        register(parts, names)
        register(primary, names)
        scopes[scope] = (parts, primary)
    for scope_parts, _ in scopes.values():
        if any(
            within(primary, scope_parts) or within(scope_parts, primary)
            for _, primary in scopes.values()
        ):
            raise Refusal("Primary and evaluator scopes overlap")
    for item in data["entries"]:
        if not isinstance(item, dict) or item.get("scope") not in scopes:
            raise Refusal("Entry has an unknown scope")
        parts = relative(item.get("path"), "Omitted path")
        canonical = relative(item.get("canonical"), "Canonical path")
        scope_parts, _ = scopes[item["scope"]]
        size, digest = item.get("bytes"), item.get("sha256")
        if (
            not within(parts, scope_parts)
            or len(parts) <= len(scope_parts)
            or type(size) is not int
            or size < 0
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-fA-F]{64}", digest) is None
        ):
            raise Refusal(f"Invalid restoration entry: {item.get('path')}")
        register(parts, names)
        register(canonical, names)
        if key(parts) in destinations:
            raise Refusal(f"Duplicate restoration destination: {'/'.join(parts)}")
        destinations.add(key(parts))
        source_newline = item.get("source_newline")
        if source_newline not in (None, "LF"):
            raise Refusal("Unsupported source newline conversion")
        if source_newline is not None and canonical[:4] != (
            "supplementary",
            "tools",
            "framework",
            "pepflow",
        ):
            raise Refusal("Newline conversion is limited to the shared framework")
        entries.append(
            (item["scope"], parts, canonical, size, digest.lower(), source_newline)
        )
    for _, parts, canonical, _, _, _ in entries:
        if key(canonical) in destinations:
            raise Refusal("Canonical source is also omitted (chain or cycle)")
        if any(key(parts[:n]) in destinations for n in range(1, len(parts))):
            raise Refusal("Mapped file is an ancestor of another destination")
    return scopes, entries


def restore(map_path, selected, destination):
    map_path = absolute(map_path)
    source = map_path.parent.parent
    safe_path(source)
    source_edits = load_source_edits(source)
    scopes, entries = read_map(map_path)
    if selected is None:
        selected = list(scopes)
    selected = list(dict.fromkeys(selected))
    if not selected or any(scope not in scopes for scope in selected):
        raise Refusal("Select at least one known scope")
    target = source if destination is None else absolute(destination)
    safe_path(target)
    if target.exists() and not target.is_dir():
        raise Refusal("Destination is not a directory")
    in_place = (
        os.path.normcase(str(target)).casefold()
        == os.path.normcase(str(source)).casefold()
    )
    selected_entries = [entry for entry in entries if entry[0] in selected]
    protected = [source.joinpath(*p) for pair in scopes.values() for p in pair]
    protected += [source.joinpath(*entry[2]) for entry in entries]
    if not in_place and (
        overlap(target, map_path) or any(overlap(target, p) for p in protected)
    ):
        raise Refusal("Destination overlaps a source, primary, canonical, or map path")
    plan, all_names = {}, {}
    cached = {}

    def checked(path, expected=None, source_newline=None):
        cache_key = (path, source_newline)
        if cache_key not in cached:
            cached[cache_key] = fingerprint(path, source_newline, source_edits)
        actual = cached[cache_key]
        if expected is not None and actual != expected:
            raise Refusal(f"Source bytes/hash do not match the map: {path}")
        return actual

    for scope in selected:
        scope_parts = scopes[scope][0]
        live, _ = inventory(source.joinpath(*scope_parts))
        if not in_place:
            for tail, src in live.items():
                parts = scope_parts + tail
                register(parts, all_names)
                size, digest = checked(src)
                plan[parts] = (src, size, digest, None)
        dest_scope = target.joinpath(*scope_parts)
        safe_path(dest_scope)
        if dest_scope.exists():
            existing, existing_names = inventory(dest_scope)
            for tail in existing_names.values():
                register(scope_parts + tail, all_names)
    for _, parts, canonical, size, digest, source_newline in selected_entries:
        src = source.joinpath(*canonical)
        checked(src, (size, digest), source_newline)
        register(parts, all_names)
        if parts in plan and plan[parts][1:3] != (size, digest):
            raise Refusal(
                f"Retained secondary bytes disagree with map: {'/'.join(parts)}"
            )
        plan[parts] = (src, size, digest, source_newline)
    planned_paths = {key(parts) for parts in plan}
    for parts in plan:
        if any(key(parts[:n]) in planned_paths for n in range(1, len(parts))):
            raise Refusal("Planned file is an ancestor of another destination")
    identical = 0
    for parts, (_, size, digest, _) in plan.items():
        dest = target.joinpath(*parts)
        safe_path(dest)
        if dest.exists():
            if fingerprint(dest) != (size, digest):
                raise Refusal(f"Refusing to overwrite differing destination: {dest}")
            identical += 1
    # All sources and all existing destination collisions have now been checked.
    created, written = 0, 0
    for parts, (src, size, digest, source_newline) in sorted(plan.items()):
        dest = target.joinpath(*parts)
        safe_path(src)
        payload = source_edits.read_bytes(src)
        if source_newline == "LF":
            payload = payload.replace(b"\r\n", b"\n")
        if len(payload) != size or hashlib.sha256(payload).hexdigest() != digest:
            raise Refusal(f"Source changed after preflight: {src}")
        safe_path(dest)
        if dest.exists():
            if fingerprint(dest) != (size, digest):
                raise Refusal(f"Destination changed after preflight: {dest}")
            continue
        safe_path(dest.parent)
        dest.parent.mkdir(parents=True, exist_ok=True)
        safe_path(dest)
        with dest.open("xb") as handle:
            handle.write(payload)
        if fingerprint(dest) != (size, digest):
            raise Refusal(f"Restored file failed verification: {dest}")
        created += 1
        written += size
    return {
        "mode": "in-place" if in_place else "fresh-destination",
        "scopes": selected,
        "created_files": created,
        "created_bytes": written,
        "identical_files": identical,
        "planned_files": len(plan),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--scope", action="append", help="Review scope ID; repeatable"
    )
    selection.add_argument(
        "--all", action="store_true", help="Restore all mapped scopes"
    )
    parser.add_argument("--destination", type=Path, help="Fresh campaign-layout root")
    parser.add_argument(
        "--map", type=Path, default=Path(__file__).with_name("artifact-map.json")
    )
    args = parser.parse_args()
    try:
        result = restore(args.map, None if args.all else args.scope, args.destination)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(1, f"Restore refused: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
