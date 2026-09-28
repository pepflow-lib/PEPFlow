import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'helpers'))
import runtime
import json
import bppm_setup as setup
from certificate import capture
params = {'alpha':1,'R':1}
ctx, pb, obj = setup.get_pep_setup(4, params)
data = capture(ctx, pb, obj, params)
(runtime.ROOT / 'state/bppm_dense.json').write_text(json.dumps(data, indent=2))
print('objective',data['opt_value'])
print('S max',max(abs(x) for row in data['S_matrix'] for x in row))
for name, value in data['named_dual_values'].items():
    if value is not None and abs(value)>1e-6:
        print(name,round(value,8))
print(data['basis_vectors'])
