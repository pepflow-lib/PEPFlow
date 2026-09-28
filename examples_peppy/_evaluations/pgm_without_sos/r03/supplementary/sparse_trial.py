import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
from fractions import Fraction
import numpy as np
from certificate import solve, ROOT

dense=json.loads((ROOT/'state/pgm_dense.json').read_text())
dropped=[]
for name in dense['constraint_metadata']:
    if ':' not in name:
        continue
    left,right=name.split(':')[1].split(',')
    keep=left=='x_star' or (left!='x_star' and right!='x_star' and int(right[2:])==int(left[2:])+1)
    if not keep:
        dropped.append(name)
ctx,pb,result,entries,data=solve(4,dropped)
(ROOT/'supplementary/sparse-trial.json').write_text(json.dumps(data,indent=2))
print(data['opt_value'],data['solver_status'])
for name,value in data['named_dual_values'].items():
    if value is not None:
        print(name,value,str(Fraction(value).limit_denominator(1000)))
print('eig',np.linalg.eigvalsh(data['S_matrix']))
