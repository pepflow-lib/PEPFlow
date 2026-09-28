import hashlib
import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
path = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
for c in nb.cells:
    if c.cell_type == "markdown":
        assert not any(
            s in c.source for s in ("\x0c", "\r", "\t", "\\(", "\\[", "\\)", "\\]")
        )
    assert all(o.output_type != "error" for o in c.get("outputs", []))
start = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Partial-sum Lyapunov")
)
for i in range(start, start + 4):
    print(
        i,
        nb.cells[i].cell_type,
        [o.output_type for o in nb.cells[i].get("outputs", [])],
    )
checkpath = root / "supplementary/pgm_example_lyap_checklist.md"
lines = (
    checkpath.read_text()
    .replace("Last reviewed block: B2", "Last reviewed block: B3")
    .splitlines()
)
lines = [
    ("SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest())
    if l.startswith("SHA-256:")
    else l
    for l in lines  # noqa: E741 - retain symbolic notation
]
lines = [
    l.replace(
        "| pending | Later-block requirement |",
        f"| verified | {start}-{start + 3}: explicit grouping and signed increments; complete certificate replay, all-coordinate coverage and PSD-piece checks; rank 4 confirmed at N=4,6 with fixed exclusions (1,1) |",
    )
    if l.startswith("| 9.")
    else l
    for l in lines  # noqa: E741 - retain symbolic notation
]
checkpath.write_text("\n".join(lines))
e = json.loads((root / "supplementary/b3-blend-static-001.json").read_text())
assert e["status"] == "passed"
record = dict(
    current_block="B3",
    completion_status="complete",
    next_block="B4",
    entry_exit_reason="Fixed 7/10 supplied plus 3/10 aligned PSD-piece blend; same certificates and common rank reconfirmed with full numerical coverage",
    operational_status="awaiting_same_session_continuation",
    state="state/pgm_b3.json",
    rank_evidence="supplementary/rank_search.json",
    static_evidence="supplementary/b3-blend-static-001.json",
    notebook_execution="supplementary/b3-blend-notebook-console.txt",
    sources="Own generated B3 scripts and saved B2 states; approved resources already recorded",
    commands=[
        "finalize_b3.py",
        "update_b3_notebook.py",
        "execute_notebook.py",
        "approved check_static.py check",
    ],
    access_control="instruction_only",
    access_status="no_observed_prohibited_exposure",
    original_deadline_utc="2026-09-23T18:17:47.370960+00:00",
    unresolved_work="B4 all-index basis reconstruction and B5 analytic proof",
)
(root / "supplementary/b3-blend-handoff.json").write_text(json.dumps(record, indent=2))
