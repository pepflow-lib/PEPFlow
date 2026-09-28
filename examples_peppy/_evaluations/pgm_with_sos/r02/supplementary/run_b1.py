import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runtime", root / "supplementary/helpers/runtime.py")
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
import pgm_setup as setup

results = []
for n in range(1, 8):
    ctx, pb, _ = setup.get_pep_setup(n, {"L": 1, "R": 1})
    result, log = runtime.solve_selected(ctx, pb, {"L": 1, "R": 1})
    record = {"N": n, "opt_value": float(result.opt_value), "solver_log": log}
    results.append(record)
    print(json.dumps(record), flush=True)
    (root / "supplementary/_sweep_tmp.json").write_text(json.dumps(results, indent=2))

