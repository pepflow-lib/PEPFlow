"""Required final nbconvert execution with private runtime and pinned kernel."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / "supplementary/.runtime"
settings = json.loads((ROOT / "supplementary/approved/settings.json").read_text())
for key in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:
    os.environ[key] = "1"
for key in ["TEMP", "TMP", "TMPDIR", "IPYTHONDIR", "MPLCONFIGDIR", "JUPYTER_RUNTIME_DIR", "JUPYTER_CONFIG_DIR", "XDG_CACHE_HOME"]:
    dest = runtime / key.lower()
    dest.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(dest)
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
os.environ["JUPYTER_NO_CONFIG"] = "1"
notebook = ROOT / "dual_feg_example_lyap.ipynb"
command = [settings["python"], "-I", "-B", "-m", "nbconvert", "--to", "notebook", "--execute", str(notebook),
           "--inplace", "--ExecutePreprocessor.kernel_name=attempt-kernel", "--ExecutePreprocessor.timeout=180"]
completed = subprocess.run(command, cwd=ROOT, env=os.environ.copy(), capture_output=True, text=True, timeout=240)
evidence = dict(command=command, returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
(ROOT / "supplementary/b5-nbconvert-execution.json").write_text(json.dumps(evidence, indent=2))
print(completed.stdout)
print(completed.stderr)
assert completed.returncode == 0
nb = nbformat.read(notebook, as_version=4)
streams = []
for i, cell in enumerate(nb.cells):
    if cell.cell_type == "markdown":
        assert not any(c in cell.source for c in ["\x0c", "\r", "\\(", "\\)", "\\[", "\\]"])
    for output in cell.get("outputs", []):
        assert output.output_type != "error"
        if output.output_type == "stream":
            streams.append(dict(cell=i, text=output.text))
plot_count = sum("image/png" in o.get("data", {}) for c in nb.cells for o in c.get("outputs", []))
assert plot_count > 0
evidence.update(status="passed", sha256=hashlib.sha256(notebook.read_bytes()).hexdigest(), streams=streams,
                plot_count=plot_count, rendered_review="omitted under evaluation-ancillary-v1")
(ROOT / "supplementary/b5-nbconvert-execution.json").write_text(json.dumps(evidence, indent=2))
print("Final nbconvert execution passed; notebook SHA-256", evidence["sha256"])
