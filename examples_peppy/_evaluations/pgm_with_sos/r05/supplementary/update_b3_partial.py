import hashlib
import json
import os
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / "supplementary" / ".runtime"
for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[name] = "1"
for name in (
    "TEMP",
    "TMP",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_CONFIG_DIR",
    "JUPYTER_RUNTIME_DIR",
):
    os.environ[name] = str(runtime / name.lower())
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
notebook = ROOT / "pgm_example_lyap.ipynb"
nb = nbf.read(notebook, as_version=4)
position = next(
    i
    for i, c in enumerate(nb.cells)
    if c.cell_type == "markdown" and c.source.startswith("## Lyapunov partial sums")
)
source = (ROOT / "supplementary" / "b3_construct.py").read_text()
cells = [
    nbf.v4.new_markdown_cell(r"""## Lyapunov partial sums

Let $I^f_{a,b}\leq0$ and $I^g_{a,b}\leq0$ denote normalized interpolation residuals, and let $S_i\geq0$ be the supplied three-square block. With $V_0=0$, assign each inequality to its destination index and define
$$V_{k+1}-V_k=\sum_{c:\,\mathrm{destination}(c)=k+1}d_c I_c-S_{k+1},$$
including $d_{\star,0}^fI^f_{\star,0}$ in the first increment. Thus the sequence is nonincreasing under the certificate's sign convention. The initial distance constraint is reserved for the boundary argument.

At the first horizon $N=4$, all three interior ranks are 4. All interpolation terms and all SOS pieces are assigned, with no boundary omissions. The full-coordinate coverage residual is within $10^{-5}$. A second independently acquired horizon certificate is still required before Block 3 can complete.
"""),
    nbf.v4.new_code_cell(
        "certificate = json.loads((notebook_dir/'state'/'pgm_b2.json').read_text())"
    ),
    nbf.v4.new_code_cell(source),
    nbf.v4.new_markdown_cell(
        "Cross-horizon rank confirmation is pending. Fixed exclusions: one index at each end; absolute rank tolerance $10^{-4}$ on unscaled Gram matrices in setup insertion order."
    ),
]
nb.cells[position : position + 1] = cells
nbf.write(nb, notebook)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="attempt-pgm",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nbf.write(nb, notebook)
for c in nb.cells:
    if c.cell_type == "markdown":
        assert "\\(" not in c.source and "\\[" not in c.source
        assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in c.source)
checklist = ROOT / "supplementary" / "pgm_example_lyap_checklist.md"
text = checklist.read_text(encoding="utf-8")
text = "\n".join(
    "SHA-256: " + hashlib.sha256(notebook.read_bytes()).hexdigest()
    if line.startswith("SHA-256:")
    else "Last reviewed block: B3 (partial, second horizon pending)"
    if line.startswith("Last reviewed block:")
    else line
    for line in text.splitlines()
)
checklist.write_text(text, encoding="utf-8")
print(
    json.dumps(
        {
            "notebook_executed": True,
            "B3_complete": False,
            "next_block": "B2",
            "requested_horizon": 6,
        }
    )
)
