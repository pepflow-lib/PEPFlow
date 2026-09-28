import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "helpers"))
# local helper resolved by the notebook runtime path
import runtime  # ty: ignore[unresolved-import]

root = runtime.ROOT
os.environ["JUPYTER_PATH"] = str(runtime.RUNTIME / "jupyter")
with (root / "supplementary/b5-nbconvert.log").open("w") as log:
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "pgm_example_lyap.ipynb",
            "--output",
            "pgm_example_lyap.ipynb",
            "--output-dir",
            str(root),
            "--ExecutePreprocessor.kernel_name=pgm-private",
            "--ExecutePreprocessor.timeout=240",
        ],
        cwd=root,
        stdout=log,
        stderr=subprocess.STDOUT,
        check=False,
    )
print("nbconvert exit:", result.returncode)
if result.returncode:
    print((root / "supplementary/b5-nbconvert.log").read_text()[-18000:])
raise SystemExit(result.returncode)
