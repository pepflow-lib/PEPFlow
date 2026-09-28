"""Required final nbconvert execution with attempt-owned Jupyter runtime."""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / "supplementary" / ".runtime"
for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[name] = "1"
for name in (
    "TEMP",
    "TMP",
    "TMPDIR",
    "IPYTHONDIR",
    "MPLCONFIGDIR",
    "JUPYTER_CONFIG_DIR",
    "JUPYTER_RUNTIME_DIR",
):
    folder = runtime / name.lower()
    folder.mkdir(parents=True, exist_ok=True)
    os.environ[name] = str(folder)
os.environ["JUPYTER_PATH"] = str(runtime / "jupyter")
os.environ["JUPYTER_NO_CONFIG"] = "1"
path = ROOT / "pgm_example_lyap.ipynb"
static = json.loads((ROOT / "supplementary" / "b5-static-002.json").read_text())
assert static["status"] == "passed"
started = datetime.now(timezone.utc)
deadline = datetime.fromisoformat("2026-09-23T23:46:30.668388+00:00")
remaining = (deadline - started).total_seconds()
assert remaining > 0
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
    "--inplace",
    "--ExecutePreprocessor.kernel_name=attempt-pgm",
    "--ExecutePreprocessor.timeout=180",
]
source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
result = subprocess.run(
    command,
    cwd=ROOT,
    env=os.environ.copy(),
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    timeout=min(600, remaining),
)
evidence = dict(
    command=command,
    cwd=str(ROOT),
    started_utc=started.isoformat(),
    finished_utc=datetime.now(timezone.utc).isoformat(),
    returncode=result.returncode,
    stdout=result.stdout,
    stderr=result.stderr,
    source_notebook_sha256=source_hash,
    executed_notebook_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    kernel="attempt-pgm",
    isolation="instruction_only",
    presentation_policy="evaluation-ancillary-v1",
    rendering_performed=False,
)
(ROOT / "supplementary" / "b5-final-execution.json").write_text(
    json.dumps(evidence, indent=2)
)
print(result.stdout)
print(result.stderr)
raise SystemExit(result.returncode)
