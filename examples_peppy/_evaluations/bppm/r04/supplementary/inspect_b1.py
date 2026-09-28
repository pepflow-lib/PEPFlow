import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
nbpath = root / "bppm_example_lyap.ipynb"
nb = json.loads(nbpath.read_text())
for i, cell in enumerate(nb["cells"]):
    source = "".join(cell["source"])
    assert not any(c in source for c in ("\x0c", "\x08", "\r"))
    if cell["cell_type"] == "markdown":
        assert "\\(" not in source and "\\[" not in source
    else:
        assert cell["execution_count"] is not None
        assert all(o["output_type"] != "error" for o in cell["outputs"])
    print(
        i,
        cell["cell_type"],
        source.splitlines()[0],
        [o.get("output_type") for o in cell.get("outputs", [])],
    )
assert any(
    "image/png" in o.get("data", {}) for c in nb["cells"] for o in c.get("outputs", [])
)
items = [
    (
        "title, problem description, and the algorithm update equations in LaTeX",
        "verified",
        "0",
        "Assumptions, divergence, recurrence, metric and normalization inspected.",
    ),
    (
        "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
        "pending",
        "1",
        "Explicit placeholder; Block 5 owns theorem.",
    ),
    (
        "imports",
        "verified",
        "2,3",
        "Fresh-kernel execution passed with approved roots.",
    ),
    (
        "function/operator definitions",
        "verified",
        "5",
        "Two convex functions and alpha,R parameters visible.",
    ),
    (
        "make_ctx_bppm and get_pep_setup",
        "verified",
        "6",
        "Executable recurrence, initialization and metric visible.",
    ),
    (
        "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
        "verified",
        "8",
        "Seven optimal solves; printed values and embedded PNG plot present, maximum error 4.242e-9.",
    ),
    ("dense and relaxed proof solves", "pending", "11", "Block 2 not entered."),
    (
        "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
        "pending",
        "11",
        "Block 2 not entered.",
    ),
    (
        "partial-sum Lyapunov construction and rank profile",
        "pending",
        "12",
        "Block 3 not entered.",
    ),
    ("special-vector identification", "pending", "13", "Block 4 not entered."),
    (
        "coefficient extraction and closed-form V_k",
        "pending",
        "13,14",
        "Blocks 4 and 5 not entered.",
    ),
    (
        "symbolic step, base, and boundary identities",
        "pending",
        "14",
        "Block 5 not entered.",
    ),
]
lines = [
    "Notebook: bppm_example_lyap.ipynb",
    "Last reviewed block: B1",
    "SHA-256: " + hashlib.sha256(nbpath.read_bytes()).hexdigest(),
    "Presentation policy: evaluation-ancillary-v1; source/output inspection only; no rendering or image inspection performed.",
    "",
    "|Item|Requirement|Status|Cell indices|Evidence|",
    "|---|---|---|---|---|",
]
lines += [f"|{i}|{a}|{b}|{c}|{d}|" for i, (a, b, c, d) in enumerate(items, 1)]
(root / "supplementary/bppm_example_lyap_checklist.md").write_text("\n".join(lines))
record = {
    "phase": "B1",
    "access_control": "instruction_only",
    "additional_approved_sources": [
        "dispatch.md",
        "input.md",
        "worker-protocol.md",
        "plugins/pepflow-workflows/skills/pep-implement/SKILL.md",
        "plugins/pepflow-workflows/skills/pep-implement/references/workflow.md",
        "plugins/pepflow-workflows/skills/pep-full-proof/SKILL.md",
        "plugins/pepflow-workflows/skills/lyap-define/SKILL.md",
        "plugins/pepflow-workflows/skills/lyap-vectors/SKILL.md",
        "plugins/pepflow-workflows/skills/lyap-closed-form/SKILL.md",
        "plugins/pepflow-workflows/references/output-layout.md",
        "pepflow/function.py",
        "pepflow/pep.py",
        "pepflow/pep_runner.py",
        "pepflow/__init__.py",
        "plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py",
    ],
    "commands": "PowerShell tool transcript; sweep/notebook console logs and static/preflight evidence preserve executable commands and results. All Python invocations used pinned interpreter -I -B.",
    "incident": {
        "classification": "operational_error",
        "evidence": "b1-static-001.json",
        "reason": "Windows path length during recursive staging of supplementary helper root",
        "repair": "Narrowed attempt-local helper directory to supplementary/helpers; regenerated notebook and repeated preflight/static checks. Frozen adapter unchanged.",
    },
    "prohibited_content_observed": False,
    "audit_limit": "No exhaustive OS tracing; consulted-source declaration limited to observed tool content.",
}
(root / "supplementary/b1-consulted-sources.json").write_text(
    json.dumps(record, indent=2)
)
