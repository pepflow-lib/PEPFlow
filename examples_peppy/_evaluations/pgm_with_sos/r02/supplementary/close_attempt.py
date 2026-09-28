import hashlib
import json
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
path = root / "pgm_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
sha = hashlib.sha256(path.read_bytes()).hexdigest()
checkpath = root / "supplementary/pgm_example_lyap_checklist.md"
old_lines = checkpath.read_text().splitlines()
items = []
for line in old_lines:
    if line.startswith("| ") and len(line.split("|")) >= 4:
        label = line.split("|")[1].strip()
        if label and label.split(".")[0].isdigit():
            items.append(label)
assert len(items) == 12
notes = {
    1: "Cell 0: full assumptions, proximal-gradient update and target metric.",
    2: "Cells 1-3: separate Proof Statement, Theorem and self-contained Proof outline; explicit potential, all residual/SOS definitions and decrement identity, signs and endpoints.",
    3: "Cell 4: executed imports; approved framework origin printed.",
    4: "Cell 6: smooth f, closed convex g, sum h, parameters L,R.",
    5: "Cells 6-7: context builder, proximal recurrence, sum stationarity, R**2 constraint and objective gap; executed.",
    6: "Cells 8-10: seven numerical values and statuses; comparison plot preserved as image/png; candidate discrepancy printed.",
    7: "Cells 11-12,19-20: actual dense and sparse solve records at N=4 and N=6, all-owner summaries, preserved bounds and recorded solver statuses.",
    8: "Cells 13-20: rational multiplier/SOS candidate definitions and labeled matrices, complete saved-certificate replay and Gram/function/offset checks; initial formula-search record. Cells 38-53 and proof outline establish final analytic global certificate by exact local telescoping.",
    9: "Cells 21-24: explicit partial-sum loop, full coverage/PSD-piece/increment checks and rank profile; fixed (1,1) exclusions; rank 4 at N=4,6; recovery and fixed blend disclosed.",
    10: "Cells 25-31: actual candidate construction/deduplication/column-space scan, sparse-basis search outputs, reproducible templates and every-index independence checks.",
    11: "Cells 32-38,2-3: labeled numerical and candidate coefficient matrices; full Gram/function/offset reconstruction for every k; explicit closed-form potential; coefficient recurrences and final exact proof resolve candidate status.",
    12: "Cells 39-53: separate symbolic step, base, terminal, exceptional N=1 and radius-normalization identities; actual PEPFlow contexts/recurrence/LHS/RHS/differences. Exact zero Gram matrices and function/offset outputs. Cells 3,52 establish signs/domain and nonincreasing telescope. Cells 54-56 give sharpness.",
}
lines = [
    "Notebook: pgm_example_lyap.ipynb",
    "Last reviewed block: B5",
    "SHA-256: " + sha,
    "Presentation policy: evaluation-ancillary-v1. No browser, image inspection or rendered review performed, as required. Markdown delimiter/control-character checks passed; this is source inspection, not rendered verification.",
    "Final validation: supplementary/b5-static-001.json (Ruff and ty passed); supplementary/b5-final-nbconvert-console.txt (fresh-kernel nbconvert execution passed).",
    "",
    "| Item | Status | Cells and evidence |",
    "|---|---|---|",
]
for i, label in enumerate(items, 1):
    lines.append(f"| {label} | verified | {notes[i]} |")
checkpath.write_text("\n".join(lines))
statepath = root / "state/pgm_b5.json"
state = json.loads(statepath.read_text())
state["discovery_analytic_obligations"] = state.get("analytic_obligations", [])
state["analytic_obligations"] = []
state["local_multiplier_code"] = "\n\n".join(
    nb.cells[i].source for i in (41, 44, 47, 50)
)
state["notebook_sha256"] = sha
state["completion_status"] = "complete"
state["completed_blocks"] = ["B1", "B2", "B3", "B4", "B5"]
statepath.write_text(json.dumps(state, indent=2))
# Record actual direct reads and tool-consumed source manifests without claiming exhaustive tracing.
records = [
    "preflight-access-001.json",
    "b1-handoff.json",
    "b2-handoff.json",
    "b3-revisit-b2-handoff.json",
    "b2-n6-handoff.json",
    "b3-handoff.json",
    "b4-revisit-b3-handoff.json",
    "b3-polar-handoff.json",
    "b4-polar-revisit-b3-handoff.json",
    "b3-blend-handoff.json",
    "b4-handoff.json",
]
source_manifests = []
for name in [
    "preflight-001.json",
    "b1-static-001.json",
    "b1-static-002.json",
    "b1-static-003.json",
    "b2-static-001.json",
    "b2-static-002.json",
    "b2-n6-static-001.json",
    "b3-static-001.json",
    "b3-polar-static-001.json",
    "b3-blend-static-001.json",
    "b4-static-001.json",
    "b4-static-002.json",
    "b5-static-001.json",
]:
    evidence = json.loads((root / "supplementary" / name).read_text())
    source_manifests.append(
        dict(
            evidence="supplementary/" + name,
            status=evidence["status"],
            sources=evidence.get("sources", []),
        )
    )
commands = [
    "run_b1.py",
    "build_b1_notebook.py",
    "run_b2_dense.py",
    "run_b2_sparse.py",
    "check_b2_candidates.py",
    "finalize_b2.py",
    "update_b2_notebook.py",
    "execute_notebook.py",
    "repair_b2_provenance.py",
    "close_b2.py",
    "run_b3.py",
    "acquire_b2_n6.py",
    "update_b2_n6_notebook.py",
    "close_b2_n6.py",
    "finalize_b3.py",
    "update_b3_notebook.py",
    "close_b3.py",
    "explore_b4.py",
    "recover_b3_remainder.py",
    "note_b3_recovery.py",
    "close_b3_polar.py",
    "explore_b4_polar.py",
    "recover_b3_blend.py",
    "note_b3_blend.py",
    "close_b3_blend.py",
    "check_b4_blend.py",
    "finalize_b4.py",
    "update_b4_notebook.py",
    "refresh_b4_source.py",
    "close_b4.py",
    "check_b5_exact.py",
    "update_b5_notebook.py",
    "final_execute_nbconvert.py",
    "finalize_b5.py",
    "close_attempt.py",
]
access = dict(
    access_control="instruction_only",
    mechanism="Allowlist and explicit approved/attempt-owned import roots; not OS read isolation",
    prior_records=["supplementary/" + r for r in records],
    new_direct_approved_reads=[
        "supplementary/approved/plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md",
        "supplementary/approved/pepflow/utils.py",
        "supplementary/approved/pepflow/scalar.py",
        "supplementary/approved/pepflow/vector.py",
        "supplementary/approved/pepflow/function.py",
        "supplementary/approved/pepflow/parameter.py",
        "supplementary/approved/pepflow/expression_manager.py",
    ],
    executed_own_scripts=["supplementary/" + c for c in commands],
    script_invocation="Pinned .venv Python with -I -B; repeat/retry outputs retained in corresponding console files",
    adapter_manifests=source_manifests,
    external_resources=[],
    supplied_assistance="Own approved/input.md fixed PGM SOS formulas; verified in final local and global certificate; no source notebook accessed",
    mathematical_recovery="Original SOS partial sums failed terminal span; polar-only failed two interior spans; fixed 7/10 original +3/10 aligned PSD-piece recipe passed selected all-index basis reconstruction and both-horizon rank/coverage. All failed trials retained. Exact proof uses original supplied SOS, not blend.",
    operational_incidents=[
        "Initial static staging path-length failure resolved by narrowed helper root",
        "Unused import, formatting and SymPy type diagnostics repaired in own sources",
        "Exact evaluation mode explicitly selected after roundoff in a fixed-N check",
        "Notebook-builder variable typo and final-state writer reserved-key typo repaired",
    ],
    prohibited_sources_used_or_encountered=False,
    observed_boundary_deviations=[],
    access_status="no_observed_prohibited_exposure",
    audit_limit="Available tool records and import/source manifests are not an exhaustive filesystem-read audit; no OS enforcement or absence of training knowledge is claimed.",
)
(root / "supplementary/access-record.json").write_text(json.dumps(access, indent=2))
closure = dict(
    current_block="B5",
    completion_status="complete",
    next_block=None,
    entry_exit_reason="All mathematical and required notebook/static/execution gates satisfied",
    operational_status="closed",
    run_status="completed",
    completed_blocks=["B1", "B2", "B3", "B4", "B5"],
    numerical_certificate_verified=True,
    analytic_full_pep_verified=True,
    lyapunov_proof_verified=True,
    unresolved_work=[],
    notebook="pgm_example_lyap.ipynb",
    state="state/pgm_b5.json",
    notebook_sha256=sha,
    static_evidence="supplementary/b5-static-001.json",
    execution_evidence="supplementary/b5-final-nbconvert-console.txt",
    access_record="supplementary/access-record.json",
    presentation_policy="evaluation-ancillary-v1",
    access_control="instruction_only",
    access_status="no_observed_prohibited_exposure",
    original_dispatch_utc="2026-09-23T16:17:47.370960+00:00",
    original_deadline_utc="2026-09-23T18:17:47.370960+00:00",
    usage_tokens=None,
    exports=False,
)
(root / "supplementary/final-handoff.json").write_text(json.dumps(closure, indent=2))
assert state["notebook_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
print("Attempt complete; final notebook hash:", sha)
