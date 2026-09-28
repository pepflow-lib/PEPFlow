import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runtime", root / "supplementary/helpers/runtime.py")
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import dual_feg_setup as setup

results = []
for n in range(1, 8):
    ctx, pb, obj = setup.get_pep_setup(n, {"L": 1, "R": 1})
    result, operational = runtime.solve_setup(ctx, pb, obj, {"L": 1, "R": 1})
    row = {"N": n, "opt_value": float(result.opt_value), **operational}
    results.append(row)
    print(json.dumps(row), flush=True)
    (root / "supplementary/_sweep_tmp.json").write_text(json.dumps(results, indent=2))

