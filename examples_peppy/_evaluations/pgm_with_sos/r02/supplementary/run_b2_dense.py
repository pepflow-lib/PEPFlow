import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "runtime", root / "supplementary/helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
import json  # noqa: E402 - imports follow runtime or notebook setup

from certificate import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    acquire,
    summarize,
    verify,
)

data, ctx, pb, result = acquire(4)
(root / "state/pgm_dense.json").write_text(json.dumps(data, indent=2))
summarize(data)
print("check", verify(data, data["opt_value"])[0])
