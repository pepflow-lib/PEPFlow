import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "pgm_example_lyap.ipynb"
nb = json.loads(path.read_text(encoding="utf-8"))
for c in nb["cells"]:
    if c["cell_type"] == "markdown":
        text = "".join(c["source"])
        assert not any(x in text for x in ("\\(", "\\)", "\\[", "\\]", "\r", "\f"))
        assert text.count("$") % 2 == 0
    if c["cell_type"] == "code":
        assert c["execution_count"] is not None
        assert not any(o["output_type"] == "error" for o in c["outputs"])
assert any("image/png" in o.get("data", {}) for o in nb["cells"][8]["outputs"])
items = [
    "title, problem description, and the algorithm update equations in LaTeX",
    "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
    "imports",
    "function/operator definitions",
    "make_ctx_pgm and get_pep_setup",
    "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
    "dense and relaxed proof solves",
    "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
    "partial-sum Lyapunov construction and rank profile",
    "special-vector identification",
    "coefficient extraction and closed-form V_k",
    "symbolic step, base, and boundary identities",
]
cells = {1: "0", 2: "1", 3: "2,3,4", 4: "5", 5: "6", 6: "7,8,9"}
lines = [
    "# Notebook evidence checklist",
    "",
    "Notebook: pgm_example_lyap.ipynb",
    "Last reviewed block: B1",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    "Presentation: evaluation-ancillary-v1; source/output inspection only; no rendered/image inspection.",
    "",
    "| Item | Requirement | Status | Zero-based cells | Evidence |",
    "|---|---|---|---|---|",
]
for i, name in enumerate(items, 1):
    status = "verified" if i in (1, 3, 4, 5, 6) else "pending"
    evidence = (
        "Executed and source-inspected; no errors. "
        if status == "verified"
        else "Later-block obligation. "
    )
    if i == 6:
        evidence += "Seven optimal solves; maximum discrepancy 4.289838206883445e-09; plot PNG output present."
    if i == 1:
        evidence += "Math delimiters and control characters checked; rendering omitted by policy."
    lines.append(f"| {i} | {name} | {status} | {cells.get(i, '-')} | {evidence} |")
(root / "supplementary/pgm_example_lyap_checklist.md").write_text(
    "\n".join(lines), encoding="utf-8"
)
record = {
    "current_block": "B1",
    "completion_status": "complete",
    "next_block": "B2",
    "entry_exit_reason": "Initial authorized dispatch; B1 sweep, notebook, source and execution gates passed",
    "operational_status": "awaiting_same_session_continuation",
    "access_control": "instruction_only",
    "prohibited_content_observed": False,
    "audit_limit": "No exhaustive filesystem tracing; source access declarations supplemented by adapter manifests",
    "assistance": "Fixed PGM SOS aid supplied in input.md; unused for B1 solve constraints; verification pending",
    "consulted_sources": [
        "approved/dispatch.md",
        "approved/input.md",
        "approved/worker-protocol.md",
        "approved/plugins/pepflow-workflows/skills/{pep-implement,pep-full-proof,lyap-define,lyap-vectors,lyap-closed-form}/SKILL.md",
        "approved/plugins/pepflow-workflows/skills/pep-implement/references/workflow.md",
        "approved/plugins/pepflow-workflows/references/output-layout.md",
        "approved/pepflow/function.py",
        "approved/pepflow/pep.py",
        "approved/pepflow/pep_runner.py",
        "approved/pepflow/pep_context.py",
        "approved/pepflow/solver.py",
        "approved/pepflow/pep_result.py",
        "approved/plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py",
        "Own generated setup, runtime, runner, notebook builder, notebook, state, sweep, adapter evidence",
    ],
    "commands": [
        "PowerShell Get-Content/rg on exact named approved sources; execution via pinned Python -I -B",
        "supplementary/run_b1.py once: B1 sweep",
        "supplementary/build_b1_notebook.py: attempts 001 through 004, console records preserved",
        "Approved check_static.py: b1-static-001.json, b1-static-002.json, b1-static-003.json",
        "PowerShell notebook content/output metadata inspection; supplementary/finish_b1.py checks and records",
    ],
    "incidents": [
        {
            "kind": "operational",
            "detail": "Notebook kernel not found; repaired by explicit KernelManager using attempt-owned kernel spec",
        },
        {
            "kind": "operational",
            "detail": "Broad supplementary helper staging exceeded Windows path length. Moved own runtime to supplementary/helpers and updated imports; approved adapter unchanged",
        },
        {
            "kind": "source_diagnostic",
            "detail": "Notebook E402 imports after path setup; split bootstrap/import cells; reran notebook and all source checks",
        },
        {
            "kind": "operational",
            "detail": "PowerShell inspection pipeline syntax error, corrected; no file writes or new source exposure",
        },
    ],
    "static_evidence": "supplementary/b1-static-003.json",
    "notebook_execution": "supplementary/b1-notebook-console-004.txt",
    "runtime_helper_root": "supplementary/helpers",
    "probe_helper_path": "supplementary/helpers/runtime.py",
    "unresolved_work": "B2-B5; SOS compatibility and analytic proof not yet checked",
}
(root / "supplementary/b1-handoff.json").write_text(json.dumps(record, indent=2))
print(
    "B1 notebook content, execution outputs, plot presence, and delimiters checked; handoff recorded."
)
