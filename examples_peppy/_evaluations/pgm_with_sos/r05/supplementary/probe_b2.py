import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
bootstrap = (ROOT / "supplementary" / "run_b1.py").read_text().split("results = []")[0]
exec(compile(bootstrap, str(ROOT / "supplementary" / "run_b1.py"), "exec"))
sys.path.insert(0, str(ROOT / "supplementary" / "helpers"))
cert = importlib.import_module("certificates")
setup = importlib.import_module("pgm_setup")
ctx, pb, obj, entries, dense = cert.solve_certificate(setup, 4)
(ROOT / "state" / "pgm_dense.json").write_text(json.dumps(dense, indent=2))
print("Dense", dense["opt_value"], dense["certificate_provenance"]["solver_status"])
for name, value in dense["named_dual_values"].items():
    if value is not None and value > 1e-6:
        print(name, round(value, 8))
