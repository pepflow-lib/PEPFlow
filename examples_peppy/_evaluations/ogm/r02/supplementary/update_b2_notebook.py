"""Update B2 cells and execute the evolving notebook in an owned kernel."""
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "supplementary/.runtime"
sys.path.insert(0, str(ROOT / "supplementary"))
from b2_notebook_cells import CANDIDATES, LOAD, VERIFY  # noqa: E402
for key in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:
    os.environ[key] = "1"
for key in ["TEMP", "TMP", "IPYTHONDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "MPLCONFIGDIR", "XDG_CACHE_HOME"]:
    location = RUNTIME / key.lower()
    location.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(location)
os.environ["JUPYTER_PATH"] = str(RUNTIME / "jupyter")
import nbformat as nbf  # noqa: E402
from nbclient import NotebookClient  # noqa: E402

path = ROOT / "ogm_example_lyap.ipynb"
notebook = nbf.read(path, as_version=4)
new_cells = [
    nbf.v4.new_markdown_cell("## Full PEP proof certificate\nAt N=6, a direct primal PEP solve supplies every multiplier and the Gram dual S together. The dense and selected solve records below are cached; these cells rebuild the context and recheck the complete saved certificate without solving again.", id="b2-heading"),
    nbf.v4.new_code_cell(LOAD, id="b2-load-summary"),
    nbf.v4.new_markdown_cell(r"### Initial closed-form search\nScaling the selected multipliers by $\theta_N^2$ suggests $\lambda_{\star,j}=2\theta_j/\theta_N^2$ for $j<N$, $\lambda_{\star,N}=1/\theta_N$, and $\lambda_{i,i+1}=2\theta_i^2/\theta_N^2$. The rank-one numerical remainder suggests $S=\frac{L}{2\theta_N^2}\|z_N-x_\star-\theta_N g_N/L\|^2$. These are tested candidates. No target reference was consulted; the search used the own numerical certificate.", id="b2-search-description"),
    nbf.v4.new_code_cell(CANDIDATES, id="b2-candidates"),
    nbf.v4.new_markdown_cell(r"### Complete numerical identity\nNormalize each interpolation and initial constraint to $R_c\le0$. The checked identity is $\mathrm{metric}-\mathrm{bound}-\sum_c d_cR_c+S=0$. Thus nonnegative multipliers and $S\succeq0$ have the required upper-bound sign. The numerical reverse-LDL decomposition retains every factor, including tiny factors; it does not replace the selected S by the analytic candidate. All Gram, function, and constant coordinates are checked at the frozen tolerances.", id="b2-identity-description"),
    nbf.v4.new_code_cell(VERIFY, id="b2-certificate-check")]
start = next(i for i,c in enumerate(notebook.cells) if c.id in ("b2-placeholder", "b2-heading"))
for cell in new_cells:
    if cell.cell_type == "markdown":
        cell.source = cell.source.replace(r"\n", "\n")
end = next(i for i,c in enumerate(notebook.cells) if c.id == "b3-placeholder")
notebook.cells[start:end] = new_cells
nbf.write(notebook, path)
NotebookClient(notebook, timeout=120, kernel_name="ogm-owned", resources={"metadata": {"path": str(ROOT)}}).execute()
nbf.write(notebook, path)
for cell in notebook.cells:
    if cell.cell_type == "markdown":
        assert not any(char in cell.source for char in ["\x0c", "\r", "\\(", "\\)", "\\[", "\\]"])
print(json.dumps({"clean_kernel_execution": "passed", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}))
for cell in notebook.cells:
    if cell.id.startswith("b2-"):
        for output in cell.get("outputs", []):
            if output.get("output_type") == "stream":
                print(output["text"])
