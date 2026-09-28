import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "feg_example_lyap.ipynb"
nb = json.loads(p.read_text(encoding="utf-8"))
for c in nb["cells"]:
    s = "".join(c["source"])
    if c["cell_type"] == "markdown":
        assert s.count("$") % 2 == 0 and not any(
            x in s for x in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r")
        )
for i in (23, 25, 26):
    assert nb["cells"][i]["execution_count"] is not None
    assert not any(o["output_type"] == "error" for o in nb["cells"][i]["outputs"])
checklist = root / "supplementary/feg_example_lyap_checklist.md"
lines = checklist.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B3"
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(p.read_bytes()).hexdigest()
    if line.startswith("| 9 |"):
        lines[i] = (
            "| 9 | partial-sum Lyapunov construction and rank profile | verified | 21–27 | Visible certificate replay, complete grouping/coverage/sign checks; rank two at N=6,8 with exclusions (1,1), original Gram coordinates and tolerance 1e-4. |"
        )
    if line.startswith("| 10 |"):
        lines[i] = line.replace("| 22 |", "| 28 |")
    if line.startswith("| 11 |") or line.startswith("| 12 |"):
        lines[i] = line.replace("| 23 |", "| 29 |")
checklist.write_text("\n".join(lines))
record = dict(
    current_block="B3",
    completion_status="complete",
    next_block="B4",
    entry_exit_reason="Rank two confirmed at N6 and N8 with fixed exclusions and complete coverage; selected N6 partial sums saved.",
    operational_status="awaiting_same_session_continuation",
    sources=[
        "Own N6/N8 certificates and generated replay/grouping source",
        "approved/pepflow/utils.py",
        "Previously consulted B3 workflow",
    ],
    commands=[
        "Python -I -B supplementary/b3_trial8.py",
        "Python -I -B supplementary/b3_finalize.py",
        "Python -I -B supplementary/b3_notebook.py",
        "Python -I -B supplementary/execute_notebook.py",
        "Approved static adapter b3-static-001/002.json",
        "Own notebook output/source inspection",
    ],
    incidents=[
        dict(
            classification="Static dict invariance diagnostic",
            repair="Annotate parameter dictionary using framework numeric type alias; execute and recheck.",
        )
    ],
    access_control="instruction_only",
    prohibited_exposure_observed=False,
    unresolved=["B4 basis reconstruction", "B5 exact theorem and proof"],
)
(root / "supplementary/b3-access-handoff.json").write_text(json.dumps(record, indent=2))
print("B3 checklist updated")
