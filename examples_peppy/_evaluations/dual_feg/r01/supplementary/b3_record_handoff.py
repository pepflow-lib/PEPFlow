import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "dual_feg_example_lyap.ipynb"
nb = json.loads(p.read_text())
for cell in nb["cells"]:
    if cell["cell_type"] == "markdown" and "".join(cell["source"]).startswith(
        "## Partial-sum Lyapunov"
    ):
        cell["source"] = [
            "## Partial-sum Lyapunov construction and rank profile\n",
            "B3 is in progress. The selected N=6 certificate was revalidated, and the first grouping trial passed full-coordinate coverage. Its interior rank is constant with one endpoint excluded on each side. The required second-horizon certificate is pending a B2 revisit; B3 is not yet complete. Executable trial source and singular-value evidence are retained in supplementary/.\n",
        ]
p.write_text(json.dumps(nb, indent=1))
record = {
    "current_block": "B3",
    "access_control": "instruction_only",
    "approved_direct_reads": [
        "plugins/pepflow-workflows/skills/lyap-define/references/workflow.md"
    ],
    "generated_files": [
        "supplementary/prepare_b3.py",
        "supplementary/b3_certificate_check.py",
        "supplementary/b3_decomposition.py",
        "supplementary/b3_grouping.py",
        "supplementary/run_b3_trial.py",
        "supplementary/b3-trial-n6.json",
        "supplementary/b3-trial-n6-output.txt",
        "supplementary/b3-handoff-001.json",
    ],
    "prohibited_content_observed": False,
    "incidents": [],
    "status": "incomplete_pending_B2_N8_acquisition",
}
(root / "supplementary/b3-access-record.json").write_text(json.dumps(record, indent=2))
