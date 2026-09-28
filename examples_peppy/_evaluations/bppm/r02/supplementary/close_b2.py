import hashlib
import json
from pathlib import Path

root = Path.cwd()
nbpath = root / "bppm_example_lyap.ipynb"
nb = json.loads(nbpath.read_text())
assert (
    json.loads((root / "supplementary/b2-static-002.json").read_text())["status"]
    == "passed"
)
for c in nb["cells"]:
    if c["cell_type"] == "code":
        assert c["execution_count"] is not None
        assert not any(o["output_type"] == "error" for o in c["outputs"])
for i in (14, 16, 18):
    assert any(o["output_type"] == "display_data" for o in nb["cells"][i]["outputs"])
p = root / "supplementary/bppm_example_lyap_checklist.md"
t = p.read_text().replace("Last reviewed block: B1", "Last reviewed block: B2")
lines = t.splitlines()
for i, line in enumerate(lines):
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(nbpath.read_bytes()).hexdigest()
    if line.startswith("| 7 |"):
        bits = line.split("|")
        bits[3] = " verified "
        bits[4] = " 11, 12 "
        bits[5] = (
            " Both owner groups, basis labels, dense/relaxed values and active support visible; gap 4.658e-10. "
        )
        lines[i] = "|".join(bits)
    if line.startswith("| 8 |"):
        bits = line.split("|")
        bits[3] = " verified "
        bits[4] = " 13-19 "
        bits[5] = (
            " All duals and S replayed; labeled candidate and residual matrices; max identity residual 8.856e-10; all-horizon analytic status explicitly false. "
        )
        lines[i] = "|".join(bits)
    if line.startswith("| 9 |"):
        lines[i] = line.replace("| 13 |", "| 20 |")
    if line.startswith("| 10 |"):
        lines[i] = line.replace("| 14 |", "| 21 |")
    if line.startswith("| 11 |"):
        lines[i] = line.replace("| 15 |", "| 22 |")
    if line.startswith("| 12 |"):
        lines[i] = line.replace("| 16 |", "| 23 |")
p.write_text("\n".join(lines) + "\n")
b2 = json.loads((root / "state/bppm_b2.json").read_text())
record = {
    "current_block": "B2",
    "completion_status": "complete",
    "next_block": "B3",
    "entry_exit_reason": "Verified complete sparse numerical certificate and completed initial formula search; notebook/source/clean-kernel checks passed.",
    "operational_status": "awaiting_same_session_continuation",
    "certificate_id": b2["certificate_id"],
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "consulted_sources_additional": [
        "approved/plugins/pepflow-workflows/skills/pep-full-proof/references/workflow.md",
        "approved/pepflow/constraint.py",
        "approved/pepflow/expression_manager.py",
        "approved/pepflow/pep_context.py",
        "approved/allowlist.json",
        "approved package files read for provenance hashes (exact allowlist)",
    ],
    "generated_sources_consulted": "Own B1/B2 setup, state, notebook, helpers and evidence only.",
    "incidents": [
        {
            "kind": "typing_diagnostic",
            "evidence": "b2-static-001.json",
            "repair": "Explicit numeric-dictionary cast and SymPy integer arguments; b2-static-002.json passed.",
        }
    ],
    "provenance_note": "Selected solve refreshed after helper typing repair and expansion of source fingerprints; original solve summary remains in b2-selected-output.txt. Numerical values were identical. Earlier full selected JSON was overwritten during this same-N repair; preserve full samples before future replacements.",
    "checks": {
        "static": "b2-static-002.json",
        "execution": "b2-notebook-execution.json",
        "certificate": "../state/bppm_b2.json",
    },
    "access_control": "instruction_only",
    "prohibited_content_observed": False,
    "audit_limit": "No exhaustive OS access tracing; approved staging manifests and worker tool records retained.",
    "unresolved_work": "B3-B5, including multi-horizon rank evidence and exact arbitrary-horizon Lyapunov proof.",
}
(root / "supplementary/b2-handoff.json").write_text(json.dumps(record, indent=2))
print("B2 content/output checks and handoff recorded.")
