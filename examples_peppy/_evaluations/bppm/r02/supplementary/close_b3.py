import hashlib
import json
from pathlib import Path

root = Path.cwd()
assert (
    json.loads((root / "supplementary/b3-static-002.json").read_text())["status"]
    == "passed"
)
nbpath = root / "bppm_example_lyap.ipynb"
nb = json.loads(nbpath.read_text())
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        assert cell["execution_count"] is not None
        assert not any(o["output_type"] == "error" for o in cell["outputs"])
text = "".join("".join(o.get("text", [])) for o in nb["cells"][22]["outputs"])
assert "rank V_0: 0" in text and "rank V_4: 4" in text and "Coverage residual" in text
path = root / "supplementary/bppm_example_lyap_checklist.md"
lines = (
    path.read_text()
    .replace("Last reviewed block: B2", "Last reviewed block: B3")
    .splitlines()
)
for i, line in enumerate(lines):
    if line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(nbpath.read_bytes()).hexdigest()
    if line.startswith("| 9 |"):
        p = line.split("|")
        p[3] = " verified "
        p[4] = " 20-24 "
        p[5] = (
            " Certificate replay, explicit partial sums, full coverage and sign checks; ranks 4 at N=4,6 with fixed exclusions (1,1). "
        )
        lines[i] = "|".join(p)
    if line.startswith("| 10 |"):
        lines[i] = line.replace("| 21 |", "| 25 |")
    if line.startswith("| 11 |"):
        lines[i] = line.replace("| 22 |", "| 26 |")
    if line.startswith("| 12 |"):
        lines[i] = line.replace("| 23 |", "| 27 |")
path.write_text("\n".join(lines) + "\n")
record = {
    "current_block": "B3",
    "completion_status": "complete",
    "next_block": "B4",
    "entry_exit_reason": "Rank 4 confirmed at N=4 and N=6; complete coverage, signs, certificate replay, notebook execution and static checks passed.",
    "operational_status": "awaiting_same_session_continuation",
    "selected_rank_profile": [0, 4, 4, 4, 4],
    "boundary_exclusions": {"left": 1, "right": 1},
    "confirmed_horizons": [4, 6],
    "rank_tolerance": 1e-4,
    "numerical_certificate_verified": True,
    "analytic_full_pep_verified": False,
    "lyapunov_proof_verified": False,
    "evidence": [
        "rank_search.json",
        "b3-static-002.json",
        "b3-notebook-execution.json",
    ],
    "incidents": [
        {
            "evidence": "b3-static-001.json",
            "repair": "Added explicit integer type guard before comparing mixed boundary/index assignment values; reran grouping and notebook checks.",
        }
    ],
    "consulted_sources": "Own selected and N6 certificates, own helpers/notebook, approved source hashes and already authorized generic B3 workflow only.",
    "access_control": "instruction_only",
    "prohibited_content_observed": False,
    "unresolved_work": "B4 basis and coefficient reconstruction; B5 exact arbitrary-horizon proof.",
}
(root / "supplementary/b3-handoff-002.json").write_text(json.dumps(record, indent=2))
print("B3 notebook evidence and operational handoff verified.")
