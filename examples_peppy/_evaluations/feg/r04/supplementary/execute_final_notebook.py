import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
import json
import os
import subprocess

# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

root = runtime.ATTEMPT
assert (
    json.loads((root / "supplementary/b5-static-002.json").read_text())["status"]
    == "passed"
)
env = dict(os.environ)
env["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
env["JUPYTER_NO_CONFIG"] = "1"
env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
command = [
    sys.executable,
    "-I",
    "-B",
    "-m",
    "jupyter",
    "nbconvert",
    "--to",
    "notebook",
    "--execute",
    "feg_example_lyap.ipynb",
    "--output",
    "feg_example_lyap.ipynb",
    "--output-dir",
    str(root),
    "--ExecutePreprocessor.kernel_name=feg-private",
    "--ExecutePreprocessor.timeout=180",
]
result = subprocess.run(
    command,
    cwd=root,
    env=env,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    timeout=240,
)
(root / "supplementary/b5-final-execution.json").write_text(
    json.dumps(
        {
            "command": command,
            "cwd": str(root),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "kernel_python_argv": [
                sys.executable,
                "-I",
                "-B",
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
        },
        indent=2,
    )
)
print(result.stdout)
print(result.stderr)
raise SystemExit(result.returncode)
