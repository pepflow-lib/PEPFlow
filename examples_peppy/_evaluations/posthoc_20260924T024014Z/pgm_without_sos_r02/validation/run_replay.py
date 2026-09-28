import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
with (root / "selected-replay-final.log").open("w", encoding="utf-8") as log:
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(root / "replay_selected.py")],
        cwd=root,
        stdout=log,
        stderr=subprocess.STDOUT,
    )
(root / "execution-status.json").write_text(
    json.dumps(
        {
            "command": [sys.executable, "-I", "-B", "replay_selected.py"],
            "returncode": result.returncode,
            "log": "selected-replay-final.log",
        },
        indent=2,
    )
)
print("Replay return code:", result.returncode)
