import hashlib
import json
import re
from pathlib import Path

root = Path.cwd()
path = root / "bppm_example_lyap.ipynb"
nb = json.loads(path.read_text())
for i, c in enumerate(nb["cells"]):
    source = "".join(c["source"])
    assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in source)
    if c["cell_type"] == "markdown":
        assert "\\(" not in source and "\\[" not in source
    else:
        assert c["execution_count"] is not None and all(
            o["output_type"] != "error" for o in c["outputs"]
        )
streams = "".join(
    "".join(o.get("text", "")) for c in nb["cells"][14:] for o in c.get("outputs", [])
)
assert (
    "rank V_4: 4" in streams
    and "N=6: 5 retained indices" in streams
    and "Coverage checked" in streams
)
b3 = json.loads((root / "state/bppm_b3.json").read_text())
assert b3["rank_search"]["status"] == "confirmed"
assert max(b3["grouping_residuals"].values()) < 1e-5
static = json.loads((root / "supplementary/b3-static-003.json").read_text())
assert all(
    row["returncode"] == 0
    for row in static["commands"]
    if row["label"] in ("source_ruff", "source_ty")
)
checkpath = root / "supplementary/bppm_example_lyap_checklist.md"
check = checkpath.read_text(encoding="utf-8-sig").replace(
    "Last reviewed block: B2", "Last reviewed block: B3"
)
check = re.sub(
    r"SHA-256: [a-f0-9]+",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    check,
)
lines = check.splitlines()
for i, line in enumerate(lines):
    if line.startswith("| 9."):
        parts = line.split("|")
        parts[2] = " verified "
        parts[3] = " 14–19 "
        parts[4] = (
            " Complete saved-certificate revalidation, visible grouping and rank construction, coverage/sign checks, and rank 4 at N=4 and N=6 with fixed exclusions (1,1), absolute tolerance 1e-4. Fresh-kernel execution passed; no visual review per presentation override. "
        )
        lines[i] = "|".join(parts)
checkpath.write_text("\n".join(lines))
record = dict(
    current_block="B3",
    completion_status="complete",
    next_block="B4",
    entry_exit_reason="Both complete saved certificates revalidated; same grouping gives confirmed cross-horizon ranks and full-coordinate coverage; notebook execution and static checks passed.",
    run_status="awaiting_continuation",
    sources=[
        "approved lyap-define workflow",
        "own selected N4 and supplementary N6 certificates",
        "own saved grouping/revalidation sources",
        "allowlisted framework sources checked against recorded hashes",
    ],
    commands=[
        "run_b3_selected.py",
        "run_b3_N6.py",
        "prepare_b3_assess.py",
        "save_b3.py",
        "update_b3_notebook.py",
        "static adapter checks b3-static-001/002/003.json",
        "finalize_b3.py",
    ],
    incidents=[
        dict(
            classification="source lint",
            issue="Unused generic PSDConstraint import",
            repair="Removed unused import; static checks passed.",
        )
    ],
    access_control="instruction_only",
    prohibited_content_observed=False,
    observability_limit="No exhaustive OS read trace.",
    rank_evidence="supplementary/rank_search.json",
    grouping_residuals=b3["grouping_residuals"],
    unresolved_work="B4 basis and all-index reconstruction; B5 exact Lyapunov theorem and proof.",
    deadline_utc="2026-09-23T17:01:13.976153+00:00",
)
(root / "supplementary/b3-access-handoff.json").write_text(json.dumps(record, indent=2))
print("B3 delivery checks passed. Coverage residuals:", b3["grouping_residuals"])
