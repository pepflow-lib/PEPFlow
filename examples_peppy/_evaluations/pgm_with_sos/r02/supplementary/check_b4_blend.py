import importlib.util
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runtime',root/'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.configure()
from partial_sums import construct
from basis_structure import extract_structure
b3=json.loads((root/'state/pgm_b3.json').read_text())
trial=construct(b3,variant=b3['rank_search']['recipe_id'])
coeffs,funcs,offsets,errors=extract_structure(trial,b3['N'])
print(json.dumps(dict(function_coefficients=funcs,errors=errors),indent=2))
