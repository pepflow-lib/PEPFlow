import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime", root / "supplementary/helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
from partial_sums import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    construct,
)

b2 = json.loads((root / "state/pgm_b2.json").read_text())
trial = construct(b2)
(root / "supplementary/b3-n4-canonical.json").write_text(
    json.dumps(trial["observation"], indent=2)
)
print(json.dumps(trial["observation"], indent=2))
