import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "bppm_example_lyap.ipynb"
nb = json.loads(path.read_text(encoding="utf-8"))
for cell in nb["cells"]:
    source = "".join(cell["source"])
    assert not any(ord(c) < 32 and c not in "\n\t" for c in source)
    if cell["cell_type"] == "markdown":
        assert all(x not in source for x in ("\\(", "\\)", "\\[", "\\]"))
    assert not any(o.get("output_type") == "error" for o in cell.get("outputs", []))
plot = nb["cells"][8]["outputs"]
assert any("image/png" in o.get("data", {}) for o in plot)
labels = [
    "title, problem description, and the algorithm update equations in LaTeX",
    "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
    "imports",
    "function/operator definitions",
    "make_ctx_bppm and get_pep_setup",
    "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
    "dense and relaxed proof solves",
    "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
    "partial-sum Lyapunov construction and rank profile",
    "special-vector identification",
    "coefficient extraction and closed-form V_k",
    "symbolic step, base, and boundary identities",
]
cells = ["0", "1", "2–4", "5", "6", "7–9", "10", "10", "11", "12", "12", "13"]
lines = [
    "Notebook: bppm_example_lyap.ipynb",
    "Last reviewed block: B1",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    "Presentation policy: evaluation-ancillary-v1; source/output inspection only, no rendering or image inspection.",
    "",
    "| Item | Status | Cell indices | Evidence |",
    "|---|---|---|---|",
]
for i, (label, indices) in enumerate(zip(labels, cells), 1):
    verified = i in (1, 3, 4, 5, 6)
    evidence = (
        "Inspected saved source; executed without error."
        if verified
        else "Pending owning later block."
    )
    if i == 6:
        evidence = "Executed printed N=1..7 results, maximum error 3.62193e-9; plot PNG output present; visual review omitted by policy."
    lines.append(
        f"| {i}. {label} | {'verified' if verified else 'pending'} | {indices} | {evidence} |"
    )
(root / "supplementary/bppm_example_lyap_checklist.md").write_text(
    "\n".join(lines), encoding="utf-8"
)
record = {
    "current_block": "B1",
    "consulted_sources": [
        "supplementary/approved/dispatch.md",
        "supplementary/approved/input.md",
        "supplementary/approved/worker-protocol.md",
        "supplementary/approved/plugins/pepflow-workflows/skills/pep-implement/SKILL.md",
        "supplementary/approved/plugins/pepflow-workflows/skills/pep-implement/references/workflow.md",
        "supplementary/approved/plugins/pepflow-workflows/references/output-layout.md",
        "supplementary/approved/pepflow/function.py",
        "supplementary/approved/pepflow/pep_runner.py",
        "supplementary/approved/pepflow/__init__.py",
        "supplementary/approved/pepflow/pep.py",
        "supplementary/approved/pepflow/solver.py",
        "supplementary/approved/plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py",
    ],
    "commands": "Actual tools recorded reads, scoped rg, setup creation, run_b1.py twice (setup mechanical correction), build_b1_notebook.py twice, adapter b1-static-001 through 003 and inspect_b1.py.",
    "access_control": "instruction_only",
    "prohibited_content_observed": False,
    "external_resources": [],
    "incidents": [
        {
            "kind": "operational",
            "evidence": "b1-static-001.json",
            "reason": "Windows long staging path copying broad supplementary helper root",
            "repair": "Narrowed helper root to supplementary/helpers and moved own runtime helper; check mode repeats generic preflight.",
        },
        {
            "kind": "static_diagnostic",
            "evidence": "b1-static-002.json",
            "reason": "numbers.Number annotation does not accept inferred literal integer default",
            "repair": "Removed unnecessary default, keeping alpha required; rebuilt and reran checks.",
        },
    ],
    "framework_note": "bregman_prox docstring has factor/argument typos; implemented relation grad_h = h.grad(x_0)-stepsize*grad_u matches packet. Frozen source unchanged.",
    "audit_limit": "Resolution evidence and tool logs are not exhaustive filesystem access tracing.",
}
(root / "supplementary/b1-access.json").write_text(json.dumps(record, indent=2))
print(
    "B1 notebook source/output checks passed; plot output preserved; checklist and access record saved."
)
