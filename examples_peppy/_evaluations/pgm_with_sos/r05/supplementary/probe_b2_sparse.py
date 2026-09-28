from pathlib import Path
import importlib
import json
import sys
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]
exec(compile((ROOT / 'supplementary' / 'run_b1.py').read_text().split('results = []')[0], 'bootstrap', 'exec'))
sys.path.insert(0, str(ROOT / 'supplementary' / 'helpers'))
cert = importlib.import_module('certificates')
setup = importlib.import_module('pgm_setup')
np = importlib.import_module('numpy')
sp = importlib.import_module('sympy')
pf = importlib.import_module('pepflow')
dense = json.loads((ROOT / 'state' / 'pgm_dense.json').read_text())
dropped = []
for name in dense['named_dual_values']:
    if name == 'initial_condition':
        continue
    left, right = name.split(':')[1].split(',')
    keep = left == 'x_star'
    if left != 'x_star' and right != 'x_star':
        keep = int(right.split('_')[1]) == int(left.split('_')[1]) + 1
    if not keep:
        dropped.append(name)
ctx, pb, obj, entries, state = cert.solve_certificate(setup, 4, dropped)
(ROOT / 'supplementary' / 'b2-sparse-candidate.json').write_text(json.dumps(state, indent=2))
print('Sparse', state['opt_value'], state['certificate_provenance']['solver_status'])
for name, value in state['named_dual_values'].items():
    if value is not None:
        print(name, value, Fraction(value).limit_denominator(10000))
pm = pf.ExpressionManager(ctx, resolve_parameters={'L': 1, 'R': 1})
N = sp.S(4)
S = pf.Scalar.zero()
for ii in range(1, 5):
    i = sp.S(ii)
    a = setup.f.grad(ctx[f'x_{ii}'])
    ap = setup.f.grad(ctx[f'x_{ii-1}'])
    ast = setup.f.grad(ctx['x_star'])
    s = setup.g.grad(ctx[f'x_{ii}'])
    c1 = N / ((2*N+1-i)*(2*N-i)*setup.L)
    u1 = i/(2*N)*a + (2*N-i)/(2*N)*ap - ast
    c2 = ((i-1)/(2*N-i)*(2*N+2)/(2*N+1) + 2*N/((2*N-i)**2*(2*N+1)))/(2*setup.L)
    u2 = ap+s-setup.L/(2*N+1-i)*(ctx[f'x_{ii-1}']-ctx['x_star'])
    c3 = i/(2*N+1-i)*(2*N)/(2*N+1)/(2*setup.L)
    u3 = (2*N+1)/(2*N)*(a+s)-(ap+s)/(2*N)-setup.L/(2*N-i)*(ctx[f'x_{ii}']-ctx['x_star'])
    S += c1*u1**2+c2*u2**2+c3*u3**2
candidate = np.asarray(pm.eval_scalar(S).inner_prod_coords, dtype=float)
actual = np.asarray(state['S_matrix'])
scale = np.sum(candidate*actual)/np.sum(candidate*candidate)
print('SOS fit scale', scale, 'residual', np.max(np.abs(scale*candidate-actual)))
