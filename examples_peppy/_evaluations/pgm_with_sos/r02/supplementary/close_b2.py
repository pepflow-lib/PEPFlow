import hashlib
import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
nbpath = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(nbpath, as_version=4)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        assert not any(
            t in cell.source for t in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r")
        )
    assert all(o.output_type != "error" for o in cell.get("outputs", []))
checkpath = root / "supplementary/pgm_example_lyap_checklist.md"
text = checkpath.read_text().replace(
    "Last reviewed block: B1", "Last reviewed block: B2"
)
lines = text.splitlines()
lines = [
    ("SHA-256: " + hashlib.sha256(nbpath.read_bytes()).hexdigest())
    if line.startswith("SHA-256:")
    else line
    for line in lines
]
for i, line in enumerate(lines):
    if line.startswith("| 7."):
        lines[i] = line.replace(
            "| pending | Later-block requirement |",
            "| verified | 9,10: dense and sparse values, all-owner active weights, relaxation recipe, basis and dense rank; recorded solves |",
        )
    if line.startswith("| 8."):
        lines[i] = line.replace(
            "| pending | Later-block requirement |",
            "| verified | 11-16: explicit candidate definitions, labeled weights/S/residuals, full numerical checks and exact N=4 identity; analytic status explicitly unresolved |",
        )
checkpath.write_text("\n".join(lines))
b2 = json.loads((root / "state/pgm_b2.json").read_text())
record = dict(
    current_block="B2",
    completion_status="complete",
    next_block="B3",
    entry_exit_reason="Coherent sparse numerical certificate, initial formula search and notebook checks completed",
    operational_status="awaiting_same_session_continuation",
    numerical_certificate_verified=True,
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=False,
    certificate_id=b2["certificate_id"],
    state="state/pgm_b2.json",
    static_evidence="supplementary/b2-static-002.json",
    access_control="instruction_only",
    access_status="no_observed_prohibited_exposure",
    audit_limit="No exhaustive filesystem read tracing",
    supplied_assistance="Fixed own-input SOS verified numerically against selected certificate; normalization 1",
    new_approved_sources_consulted=[
        "plugins/pepflow-workflows/skills/pep-full-proof/references/workflow.md",
        "pepflow/expression_manager.py",
        "pepflow/parameter.py",
        "pepflow/lyapunov_utils.py",
        "pepflow/ipython_utils.py",
    ],
    other_sources="Previously recorded approved framework files and own generated B1/B2 scripts, notebook and state",
    commands=[
        "run_b2_dense.py",
        "run_b2_sparse.py",
        "check_b2_candidates.py",
        "finalize_b2.py (four invocations preserved)",
        "update_b2_notebook.py",
        "execute_notebook.py (two invocations)",
        "check_static.py check (two evidence files)",
    ],
    operational_repairs=[
        "Exact candidate check initially used numerical evaluation mode; sympy_mode=True established exact fixed-N identity",
        "Ruff named-function correction and ty numeric type corrections; original acquisition source archived with original hash; solve components unchanged",
    ],
    unresolved_work="All-horizon proof and Blocks 3-5",
    original_deadline_utc="2026-09-23T18:17:47.370960+00:00",
    usage_tokens=None,
)
(root / "supplementary/b2-handoff.json").write_text(json.dumps(record, indent=2))
print("B2 checklist and operational handoff saved")
