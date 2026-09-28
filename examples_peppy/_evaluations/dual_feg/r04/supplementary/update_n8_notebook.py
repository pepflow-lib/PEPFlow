"""Document and replay the separate N=8 certificate without solving."""

import hashlib
import os
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

# optional notebook-generation dependency
from nbclient import NotebookClient  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / "supplementary/.runtime"
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[key] = "1"
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "MPLCONFIGDIR",
    "IPYTHONDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    p = runtime / key.lower()
    p.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(p)
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
path = ROOT / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
for cell in nb.cells:
    if (
        cell.id == "b3-01"
        and "from pepflow.utils import NUMERICAL_TYPE" not in cell.source
    ):
        cell.source = (
            "from pepflow.utils import NUMERICAL_TYPE\n"
            + cell.source.replace(
                "params_sp =", "params_sp: dict[str, NUMERICAL_TYPE] ="
            )
        )
cells = [
    nbformat.v4.new_markdown_cell(
        "### Additional coherent certificate at $N=8$\nThe same structural relaxation is acquired independently at $N=8$, with CLARABEL defaults. Its dense and sparse optima agree within $1.5\\times10^{-9}$. The following code replays its complete numerical certificate and decomposition checks. It remains a supplementary sample; the selected main certificate is still $N=6$. Cross-horizon grouping is pending B3."
    ),
    nbformat.v4.new_code_cell((ROOT / "supplementary/n8/verification.py").read_text()),
]
for i, cell in enumerate(cells):
    cell.id = f"b2n8-{i:02d}"
nb.cells = [c for c in nb.cells if not c.id.startswith("b2n8-")]
index = next(i for i, c in enumerate(nb.cells) if c.id == "b3-00")
nb.cells[index:index] = cells
nbformat.write(nb, path)
NotebookClient(
    nb,
    timeout=120,
    kernel_name="dual-feg-owned",
    resources={"metadata": {"path": str(ROOT)}},
).execute()
nbformat.write(nb, path)
checkpath = ROOT / "supplementary/dual_feg_example_lyap_checklist.md"
lines = checkpath.read_text().splitlines()
for i, line in enumerate(lines):
    if line.startswith("Last reviewed block:"):
        lines[i] = "Last reviewed block: B2 revisit for N=8 certificate"
    elif line.startswith("SHA-256:"):
        lines[i] = "SHA-256: " + hashlib.sha256(path.read_bytes()).hexdigest()
    elif line.startswith("| 8."):
        lines[i] = (
            "| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | b2-02,b2-03,b2n8-00,b2n8-01 | Complete N=6 and N=8 numerical certificates replayed; analytic status remains candidate. |"
        )
checkpath.write_text("\n".join(lines), encoding="utf-8")
print("N=8 certificate notebook replay passed; selected main certificate remains N=6.")
