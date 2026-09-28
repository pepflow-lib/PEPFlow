"""Prepare a review after every generation slot stops. Never execute on import."""

import datetime as dt
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = ["pgm_with_sos", "pgm_without_sos", "ogm", "bppm", "feg", "dual_feg"]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def parse(value):
    stamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(stamp.tzinfo is not None, "Timestamps must include timezone")
    return stamp


def contained(root, name):
    root = root.resolve()
    path = (root / name).resolve()
    require(
        path != root and path.is_relative_to(root),
        f"Path escapes approved root: {name}",
    )
    return path


def digest(path):
    return hashlib.sha256(fs_path(path).read_bytes()).hexdigest()


def fs_path(path):
    """Use Windows extended paths for deep validation snapshots."""
    path = Path(path).absolute()
    return (
        Path("\\\\?\\" + str(path))
        if os.name == "nt" and not str(path).startswith("\\\\?\\")
        else path
    )


def validate_campaign(m):
    require(
        m["selected_conditions"] == CONDITIONS and m["repetitions"] == 5,
        "Expected frozen 6x5 campaign",
    )
    require(
        (m["M"], m["planned_attempts"], m["planned_blocks"], m["planned_pairs"])
        == (6, 30, 150, 5),
        "Count metadata mismatch",
    )
    attempts = m["attempts"]
    require(
        len(attempts) == 30 and len({a["attempt_id"] for a in attempts}) == 30,
        "Duplicate/missing slots",
    )
    require(
        {(a["condition_id"], a["repetition"]) for a in attempts}
        == {(c, r) for c in CONDITIONS for r in range(1, 6)},
        "Slot mismatch",
    )
    for a in attempts:
        rep = f"r{a['repetition']:02d}"
        require(
            a["attempt_id"] == a["condition_id"] + "_" + rep
            and a["repetition_id"] == rep,
            "Attempt ID mismatch",
        )
        require(
            a["campaign_id"] == m["campaign_id"]
            and a["protocol_version"] == m["protocol_version"],
            "Campaign provenance mismatch",
        )
        pgm = a["condition_id"].startswith("pgm_")
        require(a["case_id"] == ("pgm" if pgm else a["condition_id"]), "Case mismatch")
        require(a["pair_id"] == ("pgm_" + rep if pgm else None), "Pair mismatch")
        require(
            a["run_status"]
            in {
                "completed",
                "timeout",
                "error",
                "contaminated",
                "stopped_at_horizon_limit",
                "needs_guidance",
                "not_started",
            },
            "All generation must terminate before review/reporting",
        )
        require(
            bool(a.get("stopped_at")),
            "Every slot requires an explicit stop, including recorded unstarted slots",
        )
    queues = m["round_queues"]
    require(
        len(queues) == 5 and {q["repetition"] for q in queues} == set(range(1, 6)),
        "Round mismatch",
    )
    for q in queues:
        require(
            len(q["queue"]) == 6 and set(q["queue"]) == set(CONDITIONS), "Invalid queue"
        )
        require(set(q["queue"][:2]) == set(CONDITIONS[:2]), "PGM must lead queue")
    require(
        sorted(sum(q["queue"][0] == p for q in queues) for p in CONDITIONS[:2])
        == [2, 3],
        "Unbalanced PGM order",
    )


def verify_submission(campaign, a):
    out = contained(campaign, a["output"])
    require(
        out == (campaign / a["condition_id"] / a["repetition_id"]).resolve(),
        "Unexpected attempt root",
    )
    hashes = read(
        contained(campaign / "supplementary/submissions", a["submission_hashes"])
    )
    require(isinstance(hashes, dict), "Invalid hash inventory")
    actual = {
        str(p.relative_to(out))
        for p in out.rglob("*")
        if p.is_file()
        and not any(part in {".runtime", "__pycache__"} for part in p.parts)
    }
    require(actual == set(hashes), "Frozen submission inventory changed")
    for name, expected in hashes.items():
        require(not Path(name).is_absolute(), "Snapshot names must be relative")
        path = contained(out, name)
        require(
            path.is_file() and digest(path) == expected,
            f"Frozen submission changed: {name}",
        )
    return out, hashes


def main():
    preparation_started = dt.datetime.now(dt.timezone.utc)
    campaign = Path(
        (ROOT / "tmp/current_peppy_astra_medium_6x5_campaign.txt")
        .read_text(encoding="utf-8")
        .strip()
    ).resolve()
    sup = campaign / "supplementary"
    manifest = sup / "manifest.json"
    m = read(manifest)
    validate_campaign(m)
    a = next(a for a in m["attempts"] if a["attempt_id"] == sys.argv[1])
    aid = a["attempt_id"]
    out, hashes = verify_submission(campaign, a)
    require(not a.get("review_status"), "Review already prepared or dispatched")
    packet = contained(sup / "inputs", a["packet"])
    require(digest(packet) == a["packet_sha256"], "Input packet drift")
    for name in ["evaluation-rubric.md", "clean-room.md", "evaluation-operations.md"]:
        key = "references/" + name
        require(
            digest(sup / "evaluation/protocol" / key) == m["protocol_hashes"][key],
            f"Frozen protocol drift: {name}",
        )
    review = sup / "evaluation" / aid
    review.mkdir(exist_ok=False)
    shutil.copyfile(packet, review / "input.md")
    shutil.copyfile(
        ROOT / "tmp/peppy_astra_review_schema.json", review / "review-schema.json"
    )
    for suffix in [".json", "-access-calls.json"]:
        host = sup / "host" / f"{a.get('agent_name', 'gen_' + aid)}{suffix}"
        if host.exists():
            shutil.copyfile(host, review / f"own-generation-host{suffix}")
    rubric = (sup / "evaluation/protocol/references/evaluation-rubric.md").read_text(
        encoding="utf-8"
    )
    keys = {
        "pgm": "| PGM (",
        "ogm": "| OGM |",
        "bppm": "| BPPM |",
        "feg": "| FEG |",
        "dual_feg": "| Dual-FEG |",
    }
    lines = []
    for line in rubric.splitlines():
        if (
            line.startswith("| ")
            and any(key in line for key in keys.values())
            and not line.startswith(keys[a["case_id"]])
        ):
            continue
        if line == "## Controller-only historical attribution":
            break
        lines.append(line)
    (review / "rubric.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for name in ["clean-room.md", "evaluation-operations.md"]:
        shutil.copyfile(sup / "evaluation/protocol/references" / name, review / name)
    validation = review / "validation"
    validation.mkdir()
    for name, expected in hashes.items():
        dst = contained(validation, name)
        fs_path(dst.parent).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(fs_path(contained(out, name)), fs_path(dst))
        require(digest(dst) == expected, f"Snapshot changed while copying: {name}")
    verify_submission(campaign, a)
    # Freeze dispatch initiation after substantive copying; prompt/save/launch latency is charged.
    stamp = dt.datetime.now(dt.timezone.utc)
    deadline = stamp + dt.timedelta(seconds=m["review_wall_limit_seconds"])
    a.update(
        review_dispatch_at=stamp.isoformat(),
        review_deadline=deadline.isoformat(),
        review_status="running",
        review_preparation_started_at=preparation_started.isoformat(),
        review_preparation_stopped_at=stamp.isoformat(),
        review_preparation_wall_seconds=(stamp - preparation_started).total_seconds(),
    )
    settings = dict(
        attempt_id=aid,
        model=m["evaluator_model"],
        reasoning_effort=m["evaluator_reasoning_effort"],
        review_started_at=stamp.isoformat(),
        deadline=deadline.isoformat(),
        review_wall_limit_seconds=m["review_wall_limit_seconds"],
        token_cap=m["review_token_cap"],
        original_submission=str(out),
        validation_copy=str(validation),
        generation_status=a["run_status"],
        generation_stop_reason=a.get("stop_reason"),
        submission_hashes=hashes,
        python=str(ROOT / ".venv/Scripts/python.exe"),
        review_output=str(review / "review.json"),
        isolation="instruction_only",
        schema_sha256=digest(review / "review-schema.json"),
        clock_scope="Controller dispatch initiation after copying; final prompt/save/native launch latency charged",
    )
    write(review / "settings.json", settings)
    instructions = f"""Independent evaluation of {aid}. All campaign generation has stopped. Model {settings["model"]}, reasoning {settings["reasoning_effort"]}. Review starts {stamp.isoformat()}, deadline {deadline.isoformat()}, budget {settings["review_wall_limit_seconds"]} seconds, token cap {settings["token_cap"]}. Read settings.json, input.md, rubric.md, clean-room.md, evaluation-operations.md, review-schema.json and submitted generic skills. Review only this submission. Do not repair its proof or consult other attempts, papers, reference solutions or history. Linked resources outside this allowlist remain prohibited.

Original artifacts at {out} are read-only. Execute only from {validation}; inspect and redirect every absolute write/helper/temp/cache path before execution. Keep all mutable kernel/solver/cache state within {review}. Python -I -B with only own approved package/helper roots. No browser, rendering or exports. These are instruction-only controls, not OS-enforced isolation.

Assess the exact target using frozen submitted evidence only, separately from workflow and operational status. Inspect evidence rather than trusting completion flags. Distinguish checks replayed from inspected. Do not invent an essential missing lemma or coefficient. An undecidable substantive candidate at the deadline is REVIEW; an absent/incomplete argument is FAIL. Only concrete operational/access ineligibility warrants NOT_EVALUATED. Instruction-only observability limits alone do not establish contamination.

Write {review / "review.json"} with exactly B1-B5, actual checks/reasons/evidence and UTC review stop time. Evidence refs MUST use campaign-relative paths (for example {a["condition_id"]}/{a["repetition_id"]}/FILE or supplementary/evaluation/{aid}/validation/FILE), optionally #cell-id anchors. All PASS judgments require inspectable evidence. notebook_path must likewise be campaign-relative or null. Do not spawn agents. Readable repository scope: this review directory and own original submission including its approved generic resources. Pinned installed dependencies/stdlib are trusted. Do not modify frozen submissions, sources or skills. Return a concise completion notice.
"""
    (review / "instructions.md").write_text(instructions, encoding="utf-8")
    write(manifest, m)
    print(str(review / "instructions.md"))


if __name__ == "__main__":
    main()
