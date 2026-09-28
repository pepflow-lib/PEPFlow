import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "supplementary/helpers"))
import runtime
from certificates import acquire
import json
import numpy as np

state, ctx, pb, result, entries = acquire(4)
(root / "state/ogm_dense.json").write_text(json.dumps(state, indent=2))
print('Bound', state['opt_value'])
print('Basis', state['basis_vectors'])
print('Eigenvalues', np.linalg.eigvalsh(state['S_matrix']))
for name, v in state['named_dual_values'].items():
    print(name, v)
