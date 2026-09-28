import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "runtime", Path(__file__).parent / "helpers/runtime.py"
)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
from partial_sums import (  # ty: ignore[unresolved-import]  # local helper resolved by the notebook runtime path  # noqa: E402 - imports follow runtime or notebook setup
    partial_sums,
)

b2 = json.loads((runtime.ROOT / "state/feg_b2.json").read_text())
dense = json.loads((runtime.ROOT / "state/feg_dense.json").read_text())
*_, observation = partial_sums(b2, dense["opt_value"])
(runtime.ROOT / "supplementary/rank_N6.json").write_text(
    json.dumps(observation, indent=2)
)
print("Rank credible:", observation["rank_credible"])
print("Coverage residual:", observation["maximum_coverage_residual"])
print("Singular values:", observation["singular_values"])
