import hashlib
import json
from pathlib import Path

root = Path.cwd()
nb_path = root / "bppm_example_lyap.ipynb"
nb = json.loads(nb_path.read_text())
evidence = json.loads((root / "supplementary/b1-static-004.json").read_text())
assert evidence["status"] == "passed"
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        assert cell["execution_count"] is not None
        assert not any(o["output_type"] == "error" for o in cell["outputs"])
assert any("image/png" in o.get("data", {}) for o in nb["cells"][9]["outputs"])
items = [
    (
        "title, problem description, and the algorithm update equations in LaTeX",
        "verified",
        "0",
        "Assumptions, divergence, exact updates, initial condition and metric present; source delimiter checks passed.",
    ),
    (
        "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
        "pending",
        "1",
        "Conjecture is explicitly pending proof.",
    ),
    (
        "imports",
        "verified",
        "2, 3",
        "Fresh kernel executed approved-root bootstrap and imports.",
    ),
    (
        "function/operator definitions",
        "verified",
        "5",
        "Convex f and h; symbolic alpha and R are visible.",
    ),
    (
        "make_ctx_bppm and get_pep_setup",
        "verified",
        "7",
        "Exact bregman_prox recursion, iterate tags, divergence initialization and metric visible and executed.",
    ),
    (
        "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
        "verified",
        "8, 9, 10",
        "Seven optimal solves; max discrepancy 4.241e-9; PNG plot output retained. No image inspection under presentation override.",
    ),
    ("dense and relaxed proof solves", "pending", "11", "Block 2 pending."),
    (
        "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
        "pending",
        "12",
        "Block 2 pending.",
    ),
    (
        "partial-sum Lyapunov construction and rank profile",
        "pending",
        "13",
        "Block 3 pending.",
    ),
    ("special-vector identification", "pending", "14", "Block 4 pending."),
    (
        "coefficient extraction and closed-form V_k",
        "pending",
        "15",
        "Blocks 4 and 5 pending.",
    ),
    (
        "symbolic step, base, and boundary identities",
        "pending",
        "16",
        "Block 5 pending.",
    ),
]
header = f"Notebook: bppm_example_lyap.ipynb\nLast reviewed block: B1\nSHA-256: {hashlib.sha256(nb_path.read_bytes()).hexdigest()}\nPresentation policy: evaluation-ancillary-v1; no rendered/image inspection performed.\n\n| Item | Requirement | Status | Cell indices | Evidence |\n|---|---|---|---|---|\n"
(root / "supplementary/bppm_example_lyap_checklist.md").write_text(
    header
    + "\n".join(
        f"| {i} | {item} | {status} | {cells} | {detail} |"
        for i, (item, status, cells, detail) in enumerate(items, 1)
    )
)
record = {
    "current_block": "B1",
    "completion_status": "complete",
    "next_block": "B2",
    "entry_exit_reason": "Initial dispatch; B1 setup, sweep, notebook and checks completed.",
    "operational_status": "awaiting_same_session_continuation",
    "dispatch_utc": "2026-09-23T17:08:47.115070+00:00",
    "deadline_utc": "2026-09-23T19:08:47.115070+00:00",
    "access_control": "instruction_only",
    "prohibited_content_observed": False,
    "consulted_approved_files": [
        "dispatch.md",
        "input.md",
        "worker-protocol.md",
        "settings.json",
        "clean-room.md",
        "allowlist.json",
        "plugins/pepflow-workflows/optional/with-clean-room/references/tool-recovery.md",
        "plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py",
        "plugins/pepflow-workflows/references/output-layout.md",
        *[
            f"plugins/pepflow-workflows/skills/{s}/SKILL.md"
            for s in (
                "pep-implement",
                "pep-full-proof",
                "lyap-define",
                "lyap-vectors",
                "lyap-closed-form",
            )
        ],
        "plugins/pepflow-workflows/skills/pep-implement/references/workflow.md",
        *[
            f"pepflow/{s}"
            for s in (
                "__init__.py",
                "function.py",
                "pep_runner.py",
                "pep.py",
                "solver.py",
                "vector.py",
                "pep_context.py",
                "pep_result.py",
            )
        ],
    ],
    "tool_consumed_sources": "Approved package and dependencies; source manifests, command lines, origins and hashes retained in adapter JSON records. Own generated files read/executed as recorded in transcript and notebook evidence.",
    "incidents": [
        {
            "kind": "operational_path_length",
            "evidence": "b1-static-001.json",
            "repair": "Moved own runtime helper to supplementary/helpers; narrower helper root and matching probe path. Generic preflight passed in b1-preflight-002.json.",
        },
        {
            "kind": "source_diagnostics",
            "evidence": "b1-static-003.json",
            "repair": "Split notebook path bootstrap from imports; explicit typing.cast for framework Parameter/Number annotation mismatch. Repeated sweep after setup source change. No frozen source changes or suppressed diagnostics.",
        },
    ],
    "framework_observation": "bregman_prox prose has inconsistent half-factor/typo, but implementation grad_h = h.grad(x_0) - stepsize*grad_u matches the supplied exact update. No source modification.",
    "checks": {
        "static": "b1-static-004.json",
        "execution": "b1-notebook-execution.json",
        "sweep": "b1-sweep-002-output.txt",
    },
    "audit_limit": "Instruction-only controls and available tool records; not exhaustive OS read tracing.",
    "unresolved_work": "Blocks B2-B5; no analytic theorem yet.",
}
(root / "supplementary/b1-handoff.json").write_text(json.dumps(record, indent=2))
print(
    "B1 notebook content and outputs inspected; checklist and operational handoff saved."
)
