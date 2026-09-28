import datetime as dt
import json
import shutil
from pathlib import Path

from peppy_astra_prepare_review import (  # ty: ignore[unresolved-import]  # Historical controller imports its sibling helper from the original tmp directory.
    digest,
    fs_path,
    read,
    verify_submission,
)

ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "examples_peppy/_evaluations/20260923T140754Z_paper5_pgm_sos_6x5_isolation1"
stamp = dt.datetime.now(dt.timezone.utc)
P = (
    C
    / "supplementary/reevaluations"
    / stamp.strftime("%Y%m%dT%H%M%SZ_mathematical_reassessment")
)
inventory = {}
for file in fs_path(C).rglob("*"):
    if file.is_file() and not any(
        x in {".runtime", "__pycache__"} for x in file.relative_to(fs_path(C)).parts
    ):
        inventory[file.relative_to(fs_path(C)).as_posix()] = digest(file)
P.mkdir(parents=True)
(ROOT / "tmp/current_peppy_posthoc.txt").write_text(str(P))


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


write(P / "original-inventory.json", inventory)
(P / "original-summary").mkdir()
for name in ["results.md", "progress.md"]:
    shutil.copyfile(C / name, P / "original-summary" / name)
policy = ROOT / "plugins/pepflow-workflows/optional/evaluate-peppy"
(P / "policy").mkdir()
for name in [
    "SKILL.md",
    "references/evaluation-rubric.md",
    "references/evaluation-operations.md",
    "references/clean-room.md",
]:
    dest = P / "policy" / Path(name).name
    shutil.copyfile(policy / name, dest)
manifest = read(C / "supplementary/manifest.json")
settings = {
    "campaign": str(C),
    "created_at": stamp.isoformat(),
    "model": "gpt-6-astra",
    "reasoning_effort": "medium",
    "review_wall_limit_seconds": 7200,
    "token_cap": None,
    "generation_rerun": False,
    "fresh_reviews": ["feg_r03", "pgm_without_sos_r02"],
    "preserve_completed_mathematics": True,
    "policy": "User-authorized post hoc separation of mathematical validity, delivery completion, and actual prohibited mathematical exposure. Generic dependency-path and display issues are operational. Frozen mathematical criteria unchanged.",
    "isolation": "instruction_only",
    "original_protocol": manifest["protocol_version"],
    "original_inventory_excludes": [".runtime", "__pycache__"],
    "reviews": {},
}
for aid in settings["fresh_reviews"]:
    attempt = next(a for a in manifest["attempts"] if a["attempt_id"] == aid)
    original, hashes = verify_submission(C, attempt)
    R = P / aid
    V = R / "validation"
    V.mkdir(parents=True)
    for name in hashes:
        dest = V / name
        fs_path(dest.parent).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(fs_path(original / name), fs_path(dest))
        assert digest(dest) == hashes[name]
    oldreview = C / "supplementary/evaluation" / aid
    for name in [
        "input.md",
        "rubric.md",
        "review-schema.json",
        "own-generation-host-access-calls.json",
    ]:
        source = oldreview / name
        if source.exists():
            shutil.copyfile(source, R / name)
    shutil.copyfile(oldreview / "review.json", R / "historical-review.json")
    write(R / "submission-hashes.json", hashes)
    settings["reviews"][aid] = {
        "original_submission": str(original),
        "directory": str(R),
        "status": "prepared",
    }
write(P / "settings.json", settings)
print(P)
