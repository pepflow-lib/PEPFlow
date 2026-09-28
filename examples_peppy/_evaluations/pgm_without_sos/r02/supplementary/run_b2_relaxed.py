import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
from fractions import Fraction
import numpy as np
from certificate import capture
sample = json.loads((runtime.ROOT/'state/pgm_dense.json').read_text())
relaxed=[]
for name, meta in sample['constraint_metadata'].items():
    if meta['origin']=='initial':
        continue
    first, second=name.split(':')[1].split(',')
    if first=='x_star':
        keep=True
    elif second=='x_star':
        keep=False
    else:
        i,j=int(first[2:]),int(second[2:])
        keep=(j==i+1)
    if not keep:
        relaxed.append(name)
selected=capture(4,relaxed)
(runtime.ROOT/'supplementary/b2-relaxation-001.json').write_text(json.dumps(selected,indent=2))
print('relaxed',selected['opt_value'],selected['certificate_provenance']['solver_status'])
for name,val in selected['named_dual_values'].items():
    if val is not None:
        print(name,val,str(Fraction(val).limit_denominator(1000)))
print('S eig',np.linalg.eigvalsh(selected['S_matrix']))
