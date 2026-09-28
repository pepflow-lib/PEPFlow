import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "dual_feg_example_lyap.ipynb"
nb = json.loads(p.read_text())
for i, c in enumerate(nb["cells"]):
    src = "".join(c["source"])
    if c["cell_type"] == "markdown":
        assert "\\(" not in src and "\\[" not in src
        assert not any(ord(ch) < 32 and ch not in "\n\t\r" for ch in src)
    for o in c.get("outputs", []):
        assert o["output_type"] != "error"
        if i >= 19 and "text" in o:
            for line in "".join(o["text"]).splitlines():
                if any(
                    key in line
                    for key in [
                        "sparse basis",
                        "reconstruction residual",
                        "Full-component",
                        "Same-certificate",
                    ]
                ):
                    print(i, line)
check = root / "supplementary/dual_feg_example_lyap_checklist.md"
lines = check.read_text().splitlines()
lines[1] = "Last reviewed block: B4"
lines[2] = "SHA-256: " + hashlib.sha256(p.read_bytes()).hexdigest()
for i, line in enumerate(lines):
    if line.startswith("| 10."):
        lines[i] = (
            "| 10. special-vector identification | verified | 19-29 | Actual candidate construction/filtering/sparse search executed; uniform adopted basis and both endpoint bases independently checked. |"
        )
    if line.startswith("| 11."):
        lines[i] = (
            "| 11. coefficient extraction and closed-form V_k | pending | 28-31 | Numerical coefficient matrices and all-index full-component reconstruction verified (max Gram error <1e-9); closed forms remain B5 obligation with named unknown functions. |"
        )
    if line.startswith("| 12."):
        lines[i] = (
            "| 12. symbolic step, base, and boundary identities | pending | 32 | B5 obligation. |"
        )
check.write_text("\n".join(lines))
record = {
    "current_block": "B4",
    "access_control": "instruction_only",
    "approved_direct_reads": [
        "plugins/pepflow-workflows/skills/lyap-vectors/references/workflow.md",
        "pepflow/lyapunov_utils.py",
    ],
    "generated_scripts": [
        "b4_scan_cells.py",
        "run_b4_scan.py",
        "b4_basis.py",
        "b4_coefficients.py",
        "b4_structure.py",
        "finalize_b4.py",
        "update_b4_notebook.py",
        "review_b4.py",
    ],
    "prohibited_content_observed": False,
    "incidents": [],
    "status": "complete_numerical_structure",
}
(root / "supplementary/b4-access-record.json").write_text(json.dumps(record, indent=2))
