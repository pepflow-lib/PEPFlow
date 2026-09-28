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
import numpy as np  # noqa: E402 - imports follow runtime or notebook setup

s = json.loads((root / "state/dual_feg_relaxed.json").read_text())
M = np.array(s["S_matrix"])
print(s["basis_vectors"])
print("eigenvalues", np.linalg.eigvalsh(M))
print("D", np.diag(s["numerical_decomposition"]["D"]))
print("rounded S", np.round(M, 6))
