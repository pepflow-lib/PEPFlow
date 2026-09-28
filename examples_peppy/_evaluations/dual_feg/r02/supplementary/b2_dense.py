import importlib.util
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('runtime', root / 'supplementary/helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import dual_feg_setup as setup
from certificate import capture
ctx, pb, obj = setup.get_pep_setup(6, {'L':1,'R':1})
data = capture(ctx,pb,obj,{'L':1,'R':1})
data['N'] = 6
(root / 'state/dual_feg_dense.json').write_text(json.dumps(data,indent=2))
print('Objective', data['opt_value'])
for name, val in data['named_dual_values'].items():
    if val is not None and val > 1e-6:
        print(name, round(val,8))
