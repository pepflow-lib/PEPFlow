import importlib.util
import os
import subprocess
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "runtime", Path(__file__).parent / "helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
command = [
    sys.executable,
    "-I",
    "-B",
    "-m",
    "nbconvert",
    "--to",
    "notebook",
    "--execute",
    "--inplace",
    "--ExecutePreprocessor.kernel_name=feg-private",
    "--ExecutePreprocessor.timeout=180",
    str(runtime.ROOT / "feg_example_lyap.ipynb"),
]
print("Executing:", command, flush=True)
completed = subprocess.run(command, cwd=runtime.ROOT, timeout=600, check=False)
raise SystemExit(completed.returncode)
