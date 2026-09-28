import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
from certificate import solve, ROOT
n=6
_,_,_,_,dense=solve(n)
(ROOT/f'supplementary/pgm_dense_N{n}.json').write_text(json.dumps(dense,indent=2))
dropped=[]
for name in dense['constraint_metadata']:
    if ':' not in name:
        continue
    left,right=name.split(':')[1].split(',')
    keep=left=='x_star' or (left!='x_star' and right!='x_star' and int(right[2:])==int(left[2:])+1)
    if not keep:
        dropped.append(name)
_,_,_,_,selected=solve(n,dropped)
(ROOT/f'supplementary/sparse-trial-N{n}.json').write_text(json.dumps(selected,indent=2))
print('Dense:',dense['opt_value'],dense['solver_status'])
print('Sparse:',selected['opt_value'],selected['solver_status'])
