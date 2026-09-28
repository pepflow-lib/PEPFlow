import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "supplementary/helpers"))
import json  # noqa: E402 - imports follow runtime or notebook setup
import os  # noqa: E402 - imports follow runtime or notebook setup
import subprocess  # noqa: E402 - imports follow runtime or notebook setup

import runtime  # noqa: E402 - imports follow runtime or notebook setup

os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
os.environ["JUPYTER_NO_CONFIG"] = "1"
command = [
    sys.executable,
    "-I",
    "-B",
    "-m",
    "nbconvert",
    "--to",
    "notebook",
    "--execute",
    str(root / "ogm_example_lyap.ipynb"),
    "--inplace",
    "--ExecutePreprocessor.kernel_name=ogm-attempt",
    "--ExecutePreprocessor.timeout=120",
]
record = {
    "command": command,
    "cwd": str(root),
    "python": sys.executable,
    "runtime": str(runtime.RUNTIME),
}
print(json.dumps(record), flush=True)
result = subprocess.run(command, cwd=root, env=os.environ.copy(), check=False)
record["returncode"] = result.returncode
(root / "supplementary/b5-nbconvert-evidence.json").write_text(
    json.dumps(record, indent=2)
)
raise SystemExit(result.returncode)
