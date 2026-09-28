import hashlib
import json
import re
from pathlib import Path

root = Path.cwd()
path = root / "bppm_example_lyap.ipynb"
nb = json.loads(path.read_text())
for i, c in enumerate(nb["cells"]):
    text = "".join(c["source"])
    assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in text)
    if c["cell_type"] == "markdown":
        assert "\\(" not in text and "\\[" not in text
    else:
        assert c["execution_count"] is not None
        assert all(o["output_type"] != "error" for o in c["outputs"])
assert any(o["output_type"] == "display_data" for o in nb["cells"][13]["outputs"])
stream = "".join("".join(o.get("text", "")) for o in nb["cells"][13]["outputs"])
assert "Exact candidate identity at N=4" in stream
assert "Numerical certificate residuals" in stream
static = json.loads((root / "supplementary/b2-static-002.json").read_text())
assert all(
    row["returncode"] == 0
    for row in static["commands"]
    if row["label"] in ("source_ruff", "source_ty")
)
b2 = json.loads((root / "state/bppm_b2.json").read_text())
assert b2["numerical_certificate_verified"] and not b2["analytic_full_pep_verified"]
checkpath = root / "supplementary/bppm_example_lyap_checklist.md"
check = checkpath.read_text()
check = check.replace("Last reviewed block: B1", "Last reviewed block: B2")
check = re.sub(
    r"SHA-256: [a-f0-9]+",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    check,
)
lines = check.splitlines()
for i, line in enumerate(lines):
    if line.startswith("| 7."):
        parts = line.split("|")
        parts[2] = " verified "
        parts[3] = " 11, 12 "
        parts[4] = (
            " Dense and sparse solve outputs from complete saved certificates; both optimal CLARABEL defaults; preserved gap 3.157e-10; basis and all owner groups shown. "
        )
        lines[i] = "|".join(parts)
    if line.startswith("| 8."):
        parts = line.split("|")
        parts[2] = " verified "
        parts[3] = " 11, 13 "
        parts[4] = (
            " Full numerical identity, scalar signs, S eigenvalues/reconstruction, labeled residuals and candidate matrices executed. Candidate formulas and fixed-sample exact identity recorded; arbitrary-horizon analytic status remains false. "
        )
        lines[i] = "|".join(parts)
checkpath.write_text("\n".join(lines))
record = dict(
    current_block="B2",
    completion_status="complete",
    next_block="B3",
    entry_exit_reason="Dense and sparse coherent certificates, initial closed-form search, complete numerical checks, notebook and static checks passed.",
    run_status="awaiting_continuation",
    access_control="instruction_only",
    sources=[
        "state/bppm_b1.json",
        "approved/plugins/pepflow-workflows/skills/pep-full-proof/references/workflow.md",
        "approved/pepflow/pep_result.py",
        "approved/pepflow/expression_manager.py",
        "approved/pepflow/constraint.py",
        "approved/pepflow/vector.py",
        "approved/pepflow/ipython_utils.py",
        "approved/allowlist.json",
        "all allowlisted pepflow Python files read by source-hash capture; frozen adapter source manifests record staged imports",
        "own generated setup, helper, certificate and notebook files",
    ],
    commands=[
        "run_b2_dense.py",
        "run_b2_relaxed.py",
        "update_b2_notebook.py (two saved execution logs)",
        "save_b2.py (two saved validation logs)",
        "static adapter checks b2-static-001.json and b2-static-002.json (exact argv/evidence retained)",
        "finalize_b2.py",
    ],
    incidents=[
        dict(
            classification="source diagnostics",
            evidence="b2-static-001.json",
            repair="Explicit numeric dictionary annotations and checked non-None dual branch; b2-static-002 passed.",
        )
    ],
    prohibited_content_observed=False,
    observability_limit="Instruction-only boundary; no exhaustive OS tracing.",
    certificate_id=b2["certificate_id"],
    numerical_certificate_verified=True,
    analytic_full_pep_verified=False,
    lyapunov_proof_verified=False,
    unresolved_work="B3-B5 not started; arbitrary-horizon analytic proof remains open.",
    deadline_utc="2026-09-23T17:01:13.976153+00:00",
    usage=None,
)
(root / "supplementary/b2-access-handoff.json").write_text(json.dumps(record, indent=2))
print("B2 artifact inspection passed; certificate", b2["certificate_id"])
