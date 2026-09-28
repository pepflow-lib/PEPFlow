"""Execute the final notebook via the required nbconvert route in a private kernel."""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# optional notebook-generation dependency
import nbformat as nbf  # ty: ignore[unresolved-import]

root = Path(__file__).resolve().parents[1]
runtime = root / "supplementary/.runtime"
env = os.environ.copy()
for key in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    env[key] = "1"
for key in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
    "XDG_CACHE_HOME",
):
    path = runtime / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    env[key] = str(path)
kernel = runtime / "jupyter/kernels/bppm-owned"
kernel.mkdir(parents=True, exist_ok=True)
(kernel / "kernel.json").write_text(
    json.dumps(
        {
            "argv": [
                sys.executable,
                "-I",
                "-B",
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            "display_name": "BPPM owned kernel",
            "language": "python",
        }
    )
)
env["JUPYTER_PATH"] = str(runtime / "jupyter")
env["JUPYTER_NO_CONFIG"] = "1"
env["PYTHONDONTWRITEBYTECODE"] = "1"
env["PYTHONIOENCODING"] = "utf-8"
nbpath = root / "bppm_example_lyap.ipynb"
command = [
    sys.executable,
    "-I",
    "-B",
    "-m",
    "nbconvert",
    "--to",
    "notebook",
    "--execute",
    str(nbpath),
    "--output",
    "bppm_example_lyap.ipynb",
    "--output-dir",
    str(root),
    "--ExecutePreprocessor.kernel_name=bppm-owned",
    "--ExecutePreprocessor.timeout=120",
]
started = datetime.now(timezone.utc).isoformat()
result = subprocess.run(
    command,
    cwd=root,
    env=env,
    capture_output=True,
    text=True,
    encoding="utf-8",
    timeout=150,
)
record = {
    "command": command,
    "cwd": str(root),
    "started_utc": started,
    "finished_utc": datetime.now(timezone.utc).isoformat(),
    "returncode": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
}
(root / "supplementary/b5-nbconvert-execution.json").write_text(
    json.dumps(record, indent=2)
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
nb = nbf.read(nbpath, as_version=4)
for cell in nb.cells:
    if cell.cell_type == "code":
        assert cell.execution_count is not None
        assert not any(o.output_type == "error" for o in cell.outputs)
    else:
        assert not any(
            t in cell.source for t in ("\\(", "\\)", "\\[", "\\]", "\x0c", "\r")
        )
record.update(
    clean_kernel=True,
    notebook_sha256=hashlib.sha256(nbpath.read_bytes()).hexdigest(),
    code_cells=sum(c.cell_type == "code" for c in nb.cells),
    markdown_source_check="passed",
    rendered_review="omitted_by_evaluation_policy",
)
(root / "supplementary/b5-nbconvert-execution.json").write_text(
    json.dumps(record, indent=2)
)
print("Final notebook passed end-to-end nbconvert execution.")
