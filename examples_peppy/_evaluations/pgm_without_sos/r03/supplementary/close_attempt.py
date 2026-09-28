import json
from pathlib import Path

root = Path.cwd()
approved = root / "supplementary/approved"
explicit = [
    "preflight-only.md",
    "allowlist.json",
    "settings.json",
    "clean-room.md",
    "plugins/pepflow-workflows/optional/with-clean-room/references/tool-recovery.md",
    "plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py",
    "dispatch.md",
    "input.md",
    "worker-protocol.md",
    "plugins/pepflow-workflows/references/output-layout.md",
]
for skill in (
    "pep-implement",
    "pep-full-proof",
    "lyap-define",
    "lyap-vectors",
    "lyap-closed-form",
):
    explicit += [
        f"plugins/pepflow-workflows/skills/{skill}/SKILL.md",
        f"plugins/pepflow-workflows/skills/{skill}/references/workflow.md",
    ]
explicit += [
    "pepflow/" + name
    for name in (
        "__init__.py",
        "function.py",
        "pep_runner.py",
        "pep.py",
        "pep_result.py",
        "expression_manager.py",
        "ipython_utils.py",
        "lyapunov_utils.py",
    )
]
b5 = json.loads((root / "state/pgm_b5.json").read_text())
record = {
    "attempt_id": "pgm_without_sos_r03",
    "access_control": "instruction_only",
    "mechanism": "Worker followed exact allowlist and own-output restriction; no OS read-isolation claim",
    "explicitly_consulted_approved_files": [str(approved / p) for p in explicit],
    "imported_and_hashed_sources": b5["certificate_provenance"]["source_hashes"],
    "own_generated_resources": "Scripts, notebook, state, evidence JSON and logs under this attempt; primary executed scripts listed below",
    "primary_executed_scripts": [
        "run_b1.py",
        "build_b1_notebook.py",
        "certificate.py",
        "sparse_trial.py",
        "run_b2_checks.py",
        "save_b2.py",
        "execute_notebook.py",
        "explore_b3.py",
        "run_grouping.py",
        "acquire_N6.py",
        "save_b2_N6.py",
        "run_grouping_N6.py",
        "build_b3.py",
        "save_b3.py",
        "explore_b4.py",
        "explore_b4_second.py",
        "run_b4.py",
        "save_b4.py",
        "derive_b5_recurrence.py",
        "derive_b5_scaled.py",
        "probe_symbolic_b5.py",
        "run_b5_symbolic.py",
        "run_b5_all.py",
        "build_b5.py",
        "execute_final_nbconvert.py",
        "final_markdown_audit.py",
        "save_b5_final.py",
    ],
    "commands": "All Python invocations used the pinned .venv/Scripts/python.exe with -I -B from the own attempt directory. Exact adapter argv, versions, source hashes and diagnostics are preserved in each static/preflight evidence JSON. Available tool-call transcripts preserve read/edit commands; this compact record is not an exhaustive OS trace.",
    "external_resources": ["UTC clock tool only; no external mathematical sources"],
    "prohibited_material_observed": False,
    "integrity_exceptions": [],
    "operational_events": [
        "Initial static staging path length error; narrowed attempt helper root and reran preflight; no frozen source edit.",
        "N6/N7 initial sweep and additional dense N6 reported optimal_inaccurate, preserved explicitly; selected N4/N6 sparse certificates were optimal.",
        "A symbolic smooth-function helper could not sympify a Parameter; wrote the defining interpolation residual directly in own symbolic code without modifying framework.",
        "One mistyped working directory failed to start a process; no content was read.",
        "Routine lint/type/coordinate-dtype issues repaired in own generated code and checks repeated.",
        "Final Markdown row-break source correction followed executed mathematical verification; no executable cells changed.",
    ],
    "observability_limits": "Instruction-only isolation and available tool outputs do not certify exhaustive access history or exclude relevant model-training knowledge.",
    "presentation_policy": "evaluation-ancillary-v1; no browser, rendering or image inspection",
    "run_status": "completed",
    "unresolved_work": "No required block work remains. A separate analytic global full-PEP matrix formula proof was not required and is not claimed.",
}
(root / "supplementary/clean-room-record.json").write_text(json.dumps(record, indent=2))
handoff = {
    "current_block": "B5",
    "completion_status": "complete",
    "next_block": None,
    "entry_exit_reason": "Exact step/base/terminal/N1 identities, signs, domain and radius normalization established; final notebook static and clean-kernel checks passed",
    "run_status": "completed",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": True,
    "unresolved_work": "No required block work remains; separate global analytic full-PEP matrix proof not claimed.",
    "notebook": "pgm_example_lyap.ipynb",
    "state": "state/pgm_b5.json",
    "static_evidence": "supplementary/b5-static-001.json",
    "execution_evidence": "supplementary/b5-final-notebook-output.txt",
    "access_record": "supplementary/clean-room-record.json",
    "presentation_policy": "evaluation-ancillary-v1",
    "token_usage": None,
}
(root / "supplementary/b5-handoff.json").write_text(json.dumps(handoff, indent=2))
print("Final operational and access records saved.")
