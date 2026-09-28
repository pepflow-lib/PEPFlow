import json
from pathlib import Path

root = Path.cwd()
p = root / "supplementary/b2_cells.py"
s = (
    p.read_text(encoding="utf-8-sig")
    .replace(
        "resolve_parameters={'L': 1, 'R': 1}",
        "resolve_parameters={'L': sp.Integer(1), 'R': sp.Integer(1)}",
    )
    .replace(
        "max_abs = lambda a: float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0))",
        "def max_abs(a):\n    return float(np.max(np.abs(np.asarray(a, dtype=float)), initial=0))",
    )
)
p.write_text(s)
path = root / "pgm_example_lyap.ipynb"
b = json.loads(path.read_text())
b["cells"][9]["source"] = s.splitlines(keepends=True)
path.write_text(json.dumps(b, indent=1))
for filename in ("pgm_b2.json", "pgm_relaxed.json"):
    p = root / "state" / filename
    state = json.loads(p.read_text())
    tags = ["x_star"] + [f"x_{i}" for i in range(state["N"] + 1)]
    state["lambda_row_names"] = tags
    state["lambda_col_names"] = tags
    state["lambda_matrix"] = [
        [state["named_dual_values"].get("f:" + a + "," + b) or 0.0 for b in tags]
        for a in tags
    ]
    p.write_text(json.dumps(state, indent=2))
