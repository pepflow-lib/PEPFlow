import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import numpy as np
from fractions import Fraction
from certificate_solver import solve_capture, ROOT

dense = json.loads((ROOT/'state/feg_dense.json').read_text())
relaxed = [name for name,v in dense['named_dual_values'].items() if name != 'initial_condition' and v is not None and abs(v)<1e-6]
import hashlib
allowlist = json.loads((ROOT/'supplementary/approved/allowlist.json').read_text())
paths = [Path(p) for p in allowlist['exact_read_files'] if Path(p).parent == ROOT/'supplementary/approved/pepflow']
paths += [ROOT/'feg_setup.py', ROOT/'supplementary/certificate_solver.py']
hashes = {str(p.relative_to(ROOT)).replace('\\','/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
ctx,pb,op,result,data = solve_capture(6,relaxed)
assert hashes == {str(p.relative_to(ROOT)).replace('\\','/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
data['source_hashes_before_and_after_solve'] = hashes
(ROOT/'supplementary/b2-selected-raw.json').write_text(json.dumps(data,indent=2))
print('Selected',data['opt_value'],data['solver_status'],'removed',len(relaxed),'gap',data['opt_value']-dense['opt_value'])
for name,v in data['named_dual_values'].items():
    if v is not None:
        print(name,v,str(Fraction(v).limit_denominator(1000)))
print('S rank',np.linalg.matrix_rank(data['S_matrix'],tol=1e-4))

