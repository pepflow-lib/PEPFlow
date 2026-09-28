import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
root=runtime.ATTEMPT
scope={}
for filename in ('b3_certificate_check.py','b3_decomposition.py','b3_grouping.py'):
    exec(compile((root/'supplementary'/filename).read_text(encoding='utf-8-sig'),filename,'exec'),scope)
sample={key:scope[key] for key in ('N_int','ranks','singular_values','rank_credible','certificate_checked','grouping_checked','coverage_residuals','term_assignment','S_assignment')}
sample.update(N=scope['N_int'],rank_profile=scope['ranks'],certificate_id=scope['certificate']['certificate_id'],recipe_id='consecutive-mon-plus-own-half-lipschitz-whole-S-boundary',rank_convention={'tolerance':1e-4,'scaling':'absolute singular values, no rescaling','coordinates':'setup basis order'},boundary_exclusions={'left':1,'right':1})
(root/'supplementary/b3-rank-N6.json').write_text(json.dumps(sample,indent=2))
print('Retained smallest nonzero / largest discarded singular values:',[(min([s for s in sv if s>1e-4],default=0),max([s for s in sv if s<=1e-4],default=0)) for sv in sample['singular_values']])
