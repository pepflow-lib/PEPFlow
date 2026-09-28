import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "supplementary/b5_step.py"
s = p.read_text(encoding="utf-8")
s = s.replace(
    "row_labels=['g_N','z_k','x_k-x_0','x_N-x_0'])",
    "row_labels=['g_N','z_k','x_k-x_0','x_N-x_0'],precision=0)",
)
p.write_text(s, encoding="utf-8")
p = root / "dual_feg_example_lyap.ipynb"
nb = json.loads(p.read_text(encoding="utf-8"))
for c in nb["cells"]:
    if c["cell_type"] == "code" and "".join(c["source"]).startswith("t_s,n_s="):
        c["source"] = s.splitlines(keepends=True)
p.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
