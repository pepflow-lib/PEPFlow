import contextlib
import hashlib
import json
import os
import traceback
from pathlib import Path

root = Path.cwd().resolve()
settings = json.loads((root.parent / "settings.json").read_text())
for name, expected in settings["submission_hashes"].items():
    assert (
        hashlib.sha256(Path("\\\\?\\" + str(root / name)).read_bytes()).hexdigest()
        == expected
    ), name
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    p = root / "review_runtime" / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
nb = json.loads((root / "bppm_example_lyap.ipynb").read_text(encoding="utf-8"))
ns = {"__name__": "__main__"}
completed = []
with (
    (root / "replay.log").open("w", encoding="utf-8") as log,
    contextlib.redirect_stdout(log),
    contextlib.redirect_stderr(log),
):
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        if cell["id"] == "950b3261":
            source = source.split("ns = [row")[0]  # Omit only plotting; no rendering.
        print("REPLAY CELL", cell["id"], flush=True)
        try:
            exec(compile(source, cell["id"], "exec"), ns)
        except BaseException:
            traceback.print_exc()
            raise
        completed.append(cell["id"])
    summary = {
        "completed_cells": completed,
        "hashes_verified": len(settings["submission_hashes"]),
        "certificate_checks_N4": ns["b2"]["numerical_checks"],
        "rank_samples": ns["rank_samples"],
        "rank_search": ns["rank_search"],
        "reconstruction": ns["component_residuals"],
        "coefficient_residuals": ns["coefficient_residuals"],
        "exact_residuals": ns["exact_residuals"],
        "proof_checks": ns["proof_checks"],
    }
(root / "replay_summary.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8"
)
print("Completed", len(completed), "code cells; plot omitted; no fresh solver calls.")
