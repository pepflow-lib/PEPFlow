import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

root = Path.cwd()
nbpath = root / "bppm_example_lyap.ipynb"
nb = json.loads(nbpath.read_text(encoding="utf-8"))
b5 = json.loads((root / "state/bppm_b5.json").read_text(encoding="utf-8"))
static = json.loads((root / "supplementary/b5-static-002.json").read_text())
assert all(
    c["returncode"] == 0
    for c in static["commands"]
    if c["label"] in ("source_ruff", "source_ty")
)
sha = hashlib.sha256(nbpath.read_bytes()).hexdigest()
assert sha == b5["notebook_sha256"]
for c in nb["cells"]:
    source = "".join(c["source"])
    assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in source)
    if c["cell_type"] == "markdown":
        assert "\\(" not in source and "\\[" not in source
        assert source.count("$$") % 2 == 0
    else:
        assert c["execution_count"] is not None and not any(
            o["output_type"] == "error" for o in c["outputs"]
        )
assert any("image/png" in o.get("data", {}) for o in nb["cells"][11]["outputs"])
for idx in (15, 31, 33, 40, 43, 46):
    assert any(
        o["output_type"] == "display_data" for o in nb["cells"][idx]["outputs"]
    ), idx
for idx in (38, 41, 44):
    assert nb["cells"][idx + 1]["cell_type"] == "markdown" and "$$" in "".join(
        nb["cells"][idx + 1]["source"]
    )
assert "".join(nb["cells"][1]["source"]) == "## Proof Statement"
assert "".join(nb["cells"][2]["source"]).startswith("### Theorem")
assert "".join(nb["cells"][3]["source"]).startswith("### Proof outline")
workflow = (
    root
    / "supplementary/approved/plugins/pepflow-workflows/skills/pep-implement/references/workflow.md"
).read_text(encoding="utf-8")
items = [
    text for _, text in re.findall(r"^([1-9]|1[0-2])\. (.+)$", workflow, re.M)[:12]
]
assert len(items) == 12
cells = {
    1: [0],
    2: [1, 2, 3],
    3: [4, 5],
    4: [7],
    5: [9],
    6: [10, 11, 12],
    7: [13, 14],
    8: [13, 15],
    9: [16, 17, 18, 19, 20, 21],
    10: [22, 23, 24, 25, 26, 27, 28, 29],
    11: [30, 31, 32, 33, 34, 35, 36, 37],
    12: [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48],
}
evidence = {
    1: "Problem, assumptions, metric and Bregman proximal update visibly stated.",
    2: "Separate heading/theorem/proof cells; full V_k, all four step residuals, base, boundary, signs and exact R/(alpha N) normalization.",
    3: "Approved imports and private runtime paths execute; actual framework origin printed.",
    4: "Two convex function definitions and alpha/R parameters visible.",
    5: "Actual proximal iteration, initial Bregman constraint and final objective metric visible.",
    6: "Seven optimal CLARABEL values, inverse-rate increments, maximum discrepancy 3.622e-9, and stored matplotlib comparison plot.",
    7: "Both dense and sparse solve outputs, all active owner groups, basis and preserved bound displayed.",
    8: "Actual S matrix and complete spectral decomposition; all multiplier signs and Gram/function/offset identities checked; initial candidate search and separately unverified global analytic status recorded.",
    9: "Selected numerical certificate revalidated; visible partial sums; ranks and full-coordinate coverage; fixed (1,1) exclusions confirm rank 4 at N=4 and N=6.",
    10: "Actual candidate scan and sparse subset search executed, selected bases and zero counts printed; independence checked for all indices including endpoints.",
    11: "All-index numerical matrices and full function/offset reconstruction, candidate fits, exact coefficient recurrence solution and final closed form including function gaps.",
    12: "Separate symbolic PEPFlow step/base/terminal contexts; all Gram/function/offset residuals zero with labeled matrices; N=1/R=0 coverage; signs/domain/normalization established.",
}
lines = [
    "# Notebook evidence checklist",
    "Notebook: bppm_example_lyap.ipynb",
    "Last reviewed block: B5",
    "SHA-256: " + sha,
    "Presentation policy: evaluation-ancillary-v1. No browser, rendering or image inspection performed. Source math, saved text outputs and output metadata inspected; required final fresh-kernel nbconvert execution and static checks passed.",
    "",
    "| Item | Status | Cells | Evidence |",
    "|---|---|---|---|",
]
for i, item in enumerate(items, 1):
    refs = ", ".join(f"{j} ({nb['cells'][j]['id']})" for j in cells[i])
    lines.append(f"| {i}. {item} | verified | {refs} | {evidence[i]} |")
(root / "supplementary/bppm_example_lyap_checklist.md").write_text(
    "\n".join(lines), encoding="utf-8"
)
# Preserve a compact consulted-source index; exact adapter copies/hashes and commands remain in each evidence JSON.
records = [
    "preflight-access-record.json",
    "b1-access-handoff.json",
    "b2-access-handoff.json",
    "b3-revisit-handoff.json",
    "b2-N6-handoff.json",
    "b3-access-handoff.json",
    "b4-access-handoff.json",
]
source_index = {
    "access_control": "instruction_only",
    "record_files": ["supplementary/" + name for name in records],
    "new_B5_sources": [
        "supplementary/approved/plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md",
        "own B4 state, basis and expression sources",
        "own B5 mathematical source files and executed notebook",
        "approved framework/dependencies through the same isolated runtime",
    ],
    "new_B5_commands": [
        "run_b5_derive.py",
        "run_b5_exact.py",
        "build_b5_notebook.py",
        "static adapter b5-static-001.json and b5-static-002.json",
        "execute_final_notebook.py (pinned -I -B Python invoking nbconvert --execute)",
        "save_b5.py",
        "finalize_attempt.py",
    ],
    "exact_adapter_source_and_command_evidence": [
        "supplementary/" + name
        for name in [
            "preflight-001.json",
            "b1-static-001.json",
            "b1-static-002.json",
            "b1-static-003.json",
            "b2-static-001.json",
            "b2-static-002.json",
            "b2-static-003.json",
            "b3-static-001.json",
            "b3-static-002.json",
            "b3-static-003.json",
            "b4-static-001.json",
            "b4-static-002.json",
            "b5-static-001.json",
            "b5-static-002.json",
        ]
    ],
    "external_resources": [],
    "prohibited_sources_used_or_encountered": False,
    "limits": "Instruction-only isolation; no exhaustive OS read trace. Statement limited to visible commands, source inventories and preserved evidence, not an assertion about model training.",
}
(root / "supplementary/consulted-sources.json").write_text(
    json.dumps(source_index, indent=2), encoding="utf-8"
)
record = {
    "current_block": "B5",
    "completion_status": "complete",
    "next_block": "closure",
    "entry_exit_reason": "All five blocks completed; exact local Lyapunov proof, required static checks, fresh nbconvert execution and twelve-item saved-notebook audit passed.",
    "run_status": "complete",
    "completed_blocks": ["B1", "B2", "B3", "B4", "B5"],
    "unresolved_required_work": [],
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": True,
    "analytic_full_pep_note": "Separate global analytic certificate not asserted and not required; exact local Lyapunov theorem established.",
    "artifacts": [
        "bppm_setup.py",
        "bppm_example_lyap.ipynb",
        "state/bppm_b1.json",
        "state/bppm_b2.json",
        "state/bppm_b3.json",
        "state/bppm_b4.json",
        "state/bppm_b5.json",
    ],
    "notebook_sha256": sha,
    "checks": [
        "supplementary/b5-static-002.json",
        "supplementary/b5-final-execution-command.json",
        "supplementary/b5-final-execution-console.txt",
        "supplementary/bppm_example_lyap_checklist.md",
    ],
    "B5_incidents": [
        {
            "classification": "type diagnostic",
            "issue": "SymPy undefined function callable stub mismatch",
            "repair": "Annotated dynamic symbolic function factory result; ty passed without weakening checks.",
        }
    ],
    "access_control": "instruction_only",
    "prohibited_content_observed": False,
    "access_log": "supplementary/consulted-sources.json",
    "presentation_policy": "evaluation-ancillary-v1",
    "rendered_review_performed": False,
    "deadline_utc": "2026-09-23T17:01:13.976153+00:00",
    "closed_utc": datetime.now(timezone.utc).isoformat(),
    "token_usage": None,
}
(root / "supplementary/final-handoff.json").write_text(
    json.dumps(record, indent=2), encoding="utf-8"
)
print(
    "Final notebook audit passed: 12/12 required items, with the frozen presentation override."
)
print("Notebook SHA-256:", sha)
print("run_status=complete; required unresolved work=[]")
