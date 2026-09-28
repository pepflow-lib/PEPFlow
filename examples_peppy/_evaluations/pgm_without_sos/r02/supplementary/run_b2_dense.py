import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
from certificate import capture
sample = capture(4)
(runtime.ROOT/'state/pgm_dense.json').write_text(json.dumps(sample,indent=2))
print('dense',sample['opt_value'],sample['certificate_provenance']['solver_status'])
for name, val in sample['named_dual_values'].items():
    if val is not None and abs(val)>1e-6:
        print(name, round(val,8))
print('S eigenvalues',np.linalg.eigvalsh(sample['S_matrix']))
print('basis',sample['basis_vectors'])
