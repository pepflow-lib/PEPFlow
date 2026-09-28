import hashlib
import json
from pathlib import Path

root = Path.cwd()
execution = json.loads((root / "supplementary/b5-final-execution.json").read_text())
assert execution["returncode"] != 0
assert "Python313" in execution["stderr"]
settings = json.loads((root / "supplementary/approved/settings.json").read_text())
assert settings["source_equivalence_exceptions"] == []
exact = json.loads((root / "supplementary/b5-exact-results.json").read_text())
b4 = json.loads((root / "state/feg_b4.json").read_text())
incident = dict(
    kind="confirmed_unapproved_generic_dependency_execution",
    access_control="instruction_only",
    access_status="unresolved",
    eligible=False,
    source="C:/Users/Jack/AppData/Local/Programs/Python/Python313/Scripts/jupyter-nbconvert.EXE and its Python313/Lib/site-packages dependencies",
    evidence="supplementary/b5-final-execution.json",
    exposure="Generic nbconvert/jupyter dependency stack and launcher code consumed outside the approved pinned dependency environment; no prohibited target mathematics observed",
    frozen_equivalence_exceptions=[],
    classification="error; not confirmed mathematical contamination",
    reason="Pinned python -I -B -m jupyter dispatched an external PATH-resolved nbconvert executable. Frozen allowlist permits pinned .venv dependencies; no predeclared equivalence rule covers Python313.",
    recovery="Mathematical work suspended immediately on observed traceback; bounded triage of own execution log and approved settings confirms no authorized equivalence route. Stop without repair or further execution.",
)
(root / "supplementary/b5-access-incident.json").write_text(
    json.dumps(incident, indent=2)
)
state = {
    **b4,
    "current_block": "B5",
    "completion_status": "incomplete",
    "run_status": "error",
    "access_status": "unresolved",
    "eligible": False,
    "lyapunov_proof_verified": False,
    "analytic_full_pep_verified": False,
    "proof_checks": exact["proof_checks"],
    "proof_check_scope": "Standalone pinned-interpreter exact checks completed before the access deviation; final notebook execution failed, so B5 delivery and eligibility gates are incomplete.",
    "lyapunov_formula": "V_0=0; V_k=2*k**2/N**2*||A(x_k)||**2+4*k*L/N**2*<A(x_k),x_k-x_0> for 1<=k<=N",
    "remaining_unknowns": [],
    "unresolved_work": [
        "Repair final notebook symbolic coefficient display: MatrixWithNames display coerces symbolic entries to float.",
        "Complete authorized final notebook execution and all-item audit; blocked by confirmed unapproved generic dependency execution without a frozen equivalence exception.",
    ],
    "incident_evidence": "supplementary/b5-access-incident.json",
    "notebook_execution_evidence": "supplementary/b5-final-execution.json",
    "static_check_evidence": "supplementary/b5-static-003.json",
    "notebook_delivery_complete": False,
    "presentation_policy": "evaluation-ancillary-v1",
}
(root / "state/feg_b5.json").write_text(json.dumps(state, indent=2, allow_nan=False))
check = root / "supplementary/feg_example_lyap_checklist.md"
lines = check.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = (
            "Last reviewed block: B5 stopped incomplete; final notebook execution failed"
        )
    if line.startswith("SHA-256:"):
        lines[i] = (
            "SHA-256: "
            + hashlib.sha256((root / "feg_example_lyap.ipynb").read_bytes()).hexdigest()
        )
    if (
        line.startswith("|")
        and not line.startswith("| Item")
        and not line.startswith("|---")
    ):
        parts = line.split("|")
        if len(parts) > 5:
            parts[3] = " pending "
            parts[5] = (
                " Final edited notebook not fully executed/audited; prior block evidence preserved; see B5 incident and execution log. "
            )
            lines[i] = "|".join(parts)
lines.append(
    "\nFinal execution failed during symbolic coefficient display. Unapproved external nbconvert launcher was observed; no frozen equivalence exception permits continuation. No rendered inspection was attempted under evaluation-ancillary-v1."
)
check.write_text("\n".join(lines) + "\n")
closure = dict(
    attempt_id="feg_r03",
    current_block="B5",
    completion_status="incomplete",
    next_block=None,
    entry_exit_reason="unapproved_generic_dependency_execution_without_frozen_equivalence_exception",
    operational_status="stopped",
    run_status="error",
    access_status="unresolved",
    eligible=False,
    completed_blocks=["B1", "B2", "B3", "B4"],
    unresolved_work=state["unresolved_work"],
    mathematical_contamination_confirmed=False,
    incident_evidence=state["incident_evidence"],
    deadline_extended=False,
)
(root / "supplementary/closure.json").write_text(json.dumps(closure, indent=2))
print(json.dumps(closure, indent=2))
