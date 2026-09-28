"""Run the final notebook through nbconvert in a new private kernel."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "supplementary/h"))
    # local helper resolved by the notebook runtime path
    from runtime import configure  # ty: ignore[unresolved-import]

    configure()
    os.environ["JUPYTER_PATH"] = str(root / "supplementary/.runtime/jupyter")
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
        "--ExecutePreprocessor.kernel_name=pgm-own",
        "--ExecutePreprocessor.timeout=180",
        str(root / "pgm_example_lyap.ipynb"),
    ]
    subprocess.run(command, cwd=root, check=True)


if __name__ == "__main__":
    main()
