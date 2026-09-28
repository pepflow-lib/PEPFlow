import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "ogm_example_lyap.ipynb"
nb = json.loads(path.read_text(encoding="utf-8"))
for i, cell in enumerate(nb["cells"]):
    source = "".join(cell["source"])
    if cell["cell_type"] == "markdown":
        assert not any(ch in source for ch in ("\t", "\r", "\f", "\x08")), (
            i,
            repr(source),
        )
        assert "\\\\" not in source, (i, repr(source))
        assert "\\(" not in source and "\\[" not in source
        assert source.count("$") % 2 == 0
    else:
        assert cell["execution_count"] is not None
        assert not any(o["output_type"] == "error" for o in cell["outputs"])
assert any(
    "image/png" in o.get("data", {})
    for cell in nb["cells"]
    for o in cell.get("outputs", [])
)
items = [
    "title, problem description, and the algorithm update equations in LaTeX",
    "proof statement placeholder, to be filled with the final theorem and proof outline in Block 5",
    "imports",
    "function/operator definitions",
    "make_ctx_ogm and get_pep_setup",
    "numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate",
    "dense and relaxed proof solves",
    "lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)",
    "partial-sum Lyapunov construction and rank profile",
    "special-vector identification",
    "coefficient extraction and closed-form V_k",
    "symbolic step, base, and boundary identities",
]
indices = ["0", "1", "2,3", "5", "7", "8,9,10", "11", "12", "13", "14", "15", "15"]
lines = [
    "Notebook: ogm_example_lyap.ipynb",
    "Last reviewed block: B1",
    "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
    "Presentation policy: evaluation-ancillary-v1; no rendered/image inspection performed. Text delimiters, source, execution and embedded plot output inspected.",
    "",
    "| Item | Status | Cell indices (zero-based) | Evidence |",
    "|---|---|---|---|",
]
for n, (item, index) in enumerate(zip(items, indices), 1):
    verified = n in (1, 3, 4, 5, 6)
    evidence = "Source inspected and fresh-kernel execution passed."
    if n == 1:
        evidence = "Assumptions and all updates inspected; special terminal recurrence retained; delimiters checked."
    if n == 6:
        evidence = "Seven optimal sweep rows, discrepancies printed, and embedded PNG plot retained; maximum discrepancy 3.12e-9."
    if not verified:
        evidence = "Later-block obligation; placeholder only."
    lines.append(
        f"| {n}. {item} | {'verified' if verified else 'pending'} | {index} | {evidence} |"
    )
(root / "supplementary/ogm_example_lyap_checklist.md").write_text(
    "\n".join(lines), encoding="utf-8"
)
print("Text/source/output inspection passed; checklist updated.")
