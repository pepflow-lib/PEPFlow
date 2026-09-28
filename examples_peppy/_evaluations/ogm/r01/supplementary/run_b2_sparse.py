import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "supplementary/helpers"))
import runtime
from certificates import acquire
from ogm_setup import theta_sequence
import json
import numpy as np

old = json.loads((root / "state/ogm_dense.json").read_text())
N = old['N']
def index(tag):
    if tag == 'z_0':
        return 0
    if tag == 'x_star':
        return -1
    return int(tag.split('_')[1])
dropped = []
for name, meta in old['constraint_metadata'].items():
    if meta['origin'] == 'interpolation':
        left, right = name.split(':')[1].split(',')
        i, j = index(left), index(right)
        if not (i == -1 or j == i + 1):
            dropped.append(name)
state, ctx, pb, result, entries = acquire(N, dropped)
(root / "supplementary/b2-selected-raw.json").write_text(json.dumps(state, indent=2))
theta = theta_sequence(N)
print('Bound', state['opt_value'], 'dense gap', state['opt_value']-old['opt_value'])
print('Eigenvalues', np.linalg.eigvalsh(state['S_matrix']))
for name, v in state['named_dual_values'].items():
    if v is not None:
        print(name, v)
vector = np.array([1,-1]+[-2*t for t in theta[:-1]]+[-theta[-1]])
guess = np.outer(vector, vector)/(2*theta[-1]**2)
print('Square candidate error', np.max(np.abs(guess-np.array(state['S_matrix']))))
