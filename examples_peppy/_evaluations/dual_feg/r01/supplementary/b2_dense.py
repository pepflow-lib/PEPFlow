import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
from certificate import acquire, verify
root = runtime.ATTEMPT
state = acquire(6, [], root)
(root/'state/dual_feg_dense.json').write_text(json.dumps(state,indent=2))
print('Dense bound',state['opt_value'],state['certificate_provenance']['solver_status'])
print('Basis:',state['basis_vectors'])
print('S eigs:',np.linalg.eigvalsh(state['S_matrix']))
for name, v in state['named_dual_values'].items():
    if v is not None and abs(v)>1e-6:
        print(name,v)
print('Checks:',verify(state,state['opt_value']))
