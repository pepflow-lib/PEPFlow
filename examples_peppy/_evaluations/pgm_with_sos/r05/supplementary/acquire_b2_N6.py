"""Additional coherent B2 certificate, leaving selected N4 state untouched."""
from pathlib import Path
import importlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
exec(compile((ROOT/'supplementary'/'run_b1.py').read_text().split('results = []')[0], 'bootstrap', 'exec'))
sys.path.insert(0, str(ROOT/'supplementary'/'helpers'))
cert = importlib.import_module('certificates')
setup = importlib.import_module('pgm_setup')
np = importlib.import_module('numpy')
nbf = importlib.import_module('nbformat')
output = ROOT/'supplementary'/'N6'
output.mkdir(exist_ok=True)
ctx, pb, obj, entries, dense = cert.solve_certificate(setup, 6)
(output/'dense.json').write_text(json.dumps(dense,indent=2))
print('Dense N6:',dense['opt_value'],dense['certificate_provenance']['solver_status'])
dropped = []
for name in dense['named_dual_values']:
    if name == 'initial_condition':
        continue
    left,right = name.split(':')[1].split(',')
    keep = left == 'x_star'
    if left != 'x_star' and right != 'x_star':
        keep = int(right.split('_')[1]) == int(left.split('_')[1])+1
    if not keep:
        dropped.append(name)
ctx, pb, obj, entries, selected = cert.solve_certificate(setup,6,dropped)
(output/'sparse-candidate.json').write_text(json.dumps(selected,indent=2))
print('Sparse N6:',selected['opt_value'],selected['certificate_provenance']['solver_status'])
notebook_dir = ROOT
repo_root = ROOT/'supplementary'/'approved'
pf = importlib.import_module('pepflow')
L,R,f,g,h = setup.L,setup.R,setup.f,setup.g,setup.h
get_pep_setup = setup.get_pep_setup
nb = nbf.read(ROOT/'pgm_example_lyap.ipynb',as_version=4)
executed = []
for cell_index in (10,12,14,16,18,19):
    source = nb.cells[cell_index].source
    source = source.replace("notebook_dir / 'state' / 'pgm_dense.json'", "notebook_dir / 'supplementary' / 'N6' / 'dense.json'")
    source = source.replace("notebook_dir / 'supplementary' / 'b2-sparse-candidate.json'", "notebook_dir / 'supplementary' / 'N6' / 'sparse-candidate.json'")
    source = source.replace("notebook_dir / 'state' / filename", "notebook_dir / 'supplementary' / 'N6' / filename")
    source = source.replace('at N=4', 'at N=6')
    executed.append(source)
    exec(compile(source,f'B2-replay-cell-{cell_index}','exec'))
(output/'executed-b2-check-source.py').write_text('\n\n'.join(executed),encoding='utf-8')
selected['closed_form_search']['reused_initial_search_from'] = json.loads((ROOT/'state'/'pgm_b2.json').read_text())['certificate_id']
selected['closed_form_search']['additional_horizon_verification'] = 6
(output/'pgm_b2.json').write_text(json.dumps(selected,indent=2))
print('Additional N6 certificate saved; N4 remains selected.')
