import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
settings = json.loads((root.parent / "settings.json").read_text())
original = Path(settings["original_submission"])
bad = []
for rel, expected in settings["submission_hashes"].items():
    p = original / rel
    assert p.resolve().is_relative_to(original.resolve())
    if hashlib.sha256(p.read_bytes()).hexdigest() != expected:
        bad.append(rel)
nb = json.loads((original / "pgm_example_lyap.ipynb").read_text())
code = [(i, c) for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"]
errors = [
    (i, o) for i, c in code for o in c.get("outputs", []) if o["output_type"] == "error"
]
static = json.loads((original / "supplementary/b5-static-002.json").read_text())
calls = json.loads((root.parent / "own-generation-host-access-calls.json").read_text())
absolute = set()
for c in calls:
    for path in re.findall(r"C:[/\\][^\s\"\'<>]+", c["arguments"]):
        absolute.add(path.replace("\\\\", "/").replace("\\", "/"))
own = str(original).replace("\\", "/").lower()
outside = sorted(
    p for p in absolute if not p.lower().startswith(own) and "/.venv/" not in p.lower()
)
audit = dict(
    frozen_hash_count=len(settings["submission_hashes"]),
    hash_mismatches=bad,
    notebook_hash=hashlib.sha256(
        (original / "pgm_example_lyap.ipynb").read_bytes()
    ).hexdigest(),
    code_cells=len(code),
    unexecuted_cells=[i for i, c in code if c.get("execution_count") is None],
    saved_error_outputs=errors,
    comparison_plot_present=any(
        "image/png" in o.get("data", {}) for _, c in code for o in c.get("outputs", [])
    ),
    final_static_commands=[
        {k: c[k] for k in ("label", "returncode", "stdout")}
        for c in static["commands"]
        if c["label"] in ("source_ruff", "source_ty")
    ],
    host_access_call_count=len(calls),
    absolute_path_candidates_outside_own_attempt_and_venv=outside,
    host_scan_limit="Textual command-path scan and inspected access records; not OS read tracing.",
)
(root / "audit_results.json").write_text(json.dumps(audit, indent=2))
print(json.dumps(audit, indent=2))
