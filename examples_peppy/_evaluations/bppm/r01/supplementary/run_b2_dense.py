import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
from certificate import solve_capture
import json
import numpy as np
ctx,pb,result,entries,data=solve_capture(4)
(runtime.ROOT/'state/bppm_dense.json').write_text(json.dumps(data,indent=2))
print('Bound:',data['opt_value'])
print('Basis:',data['basis_vectors'])
print('S eigenvalues:',np.linalg.eigvalsh(data['S_matrix']))
for name,value in data['named_dual_values'].items():
    if value is not None and abs(value)>1e-6:
        print(name,value)
