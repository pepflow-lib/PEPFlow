"""Build the initial notebook and execute in the private kernel."""

import json
import os
import sys
from pathlib import Path

# optional notebook-generation dependency
import nbformat  # ty: ignore[unresolved-import]

ROOT = Path(__file__).resolve().parents[1]
SUP = ROOT / "supplementary"
RT = SUP / ".runtime"
for key in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]:
    os.environ[key] = "1"
for key in [
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_RUNTIME_DIR",
    "JUPYTER_CONFIG_DIR",
]:
    path = RT / key.lower()
    path.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(path)
kernels = RT / "jupyter" / "kernels" / "attempt"
kernels.mkdir(parents=True, exist_ok=True)
(kernels / "kernel.json").write_text(
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
            "display_name": "Attempt Python",
            "language": "python",
        }
    )
)
os.environ["JUPYTER_PATH"] = str(RT / "jupyter")
import subprocess  # noqa: E402 - imports follow runtime or notebook setup
from datetime import (  # noqa: E402 - imports follow runtime or notebook setup
    datetime,
    timezone,
)

os.environ["JUPYTER_NO_CONFIG"] = "1"
path = ROOT / "dual_feg_example_lyap.ipynb"
nb = nbformat.read(path, as_version=4)
for cell in nb.cells:
    if cell.cell_type == "markdown":
        cell.source = cell.source.replace("optimal_{i}naccurate", "optimal_inaccurate")
nbformat.write(nb, path)
command = [
    sys.executable,
    "-I",
    "-B",
    "-m",
    "nbconvert",
    "--to",
    "notebook",
    "--execute",
    str(path),
    "--ExecutePreprocessor.kernel_name=attempt",
    "--ExecutePreprocessor.timeout=180",
    "--output",
    "dual_feg_example_lyap.ipynb",
    "--output-dir",
    str(ROOT),
]
start = datetime.now(timezone.utc).isoformat()
result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=600)
record = {
    "command": command,
    "cwd": str(ROOT),
    "started_utc": start,
    "finished_utc": datetime.now(timezone.utc).isoformat(),
    "returncode": result.returncode,
    "stdout": result.stdout,
    "stderr": result.stderr,
    "kernel_spec": json.loads((kernels / "kernel.json").read_text()),
}
(SUP / "b5-execution.json").write_text(json.dumps(record, indent=2))
print(json.dumps(record, indent=2))
if result.returncode:
    raise SystemExit(result.returncode)
nb = nbformat.read(path, as_version=4)
inspection = []
for i, cell in enumerate(nb.cells):
    assert not any(o.output_type == "error" for o in cell.get("outputs", []))
    if cell.cell_type == "markdown":
        assert "\\(" not in cell.source and "\\[" not in cell.source
        assert not any(ord(ch) < 32 and ch not in "\n\t" for ch in cell.source)
    inspection.append(
        {
            "index": i,
            "id": cell.id,
            "type": cell.cell_type,
            "source_start": cell.source[:100],
            "execution_count": cell.get("execution_count"),
            "output_types": [o.output_type for o in cell.get("outputs", [])],
            "stream_output": [
                o.get("text", "")
                for o in cell.get("outputs", [])
                if o.output_type == "stream"
            ],
            "display_mime_types": [
                list(o.get("data", {}))
                for o in cell.get("outputs", [])
                if o.output_type in ["display_data", "execute_result"]
            ],
        }
    )
(SUP / "b5-notebook-inspection.json").write_text(json.dumps(inspection, indent=2))
print("Final notebook execution and source/output inspection passed.")
