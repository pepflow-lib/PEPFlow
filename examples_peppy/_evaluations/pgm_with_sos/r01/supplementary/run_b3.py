import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import numpy as np
root=runtime.ATTEMPT
certificate_path=sys.argv[1] if len(sys.argv)>1 else 'state/pgm_b2.json'
certificate=json.loads((root/certificate_path).read_text())
certificate['reallocated_S_pieces']=json.loads((root/f"supplementary/b3-psd-allocation-N{certificate['N_verify']}.json").read_text())
for filename in ('b3_certificate_check.py','b3_decomposition.py','b3_grouping.py'):
    exec(compile((root/'supplementary'/filename).read_text(),filename,'exec'))
observation=dict(N=N,certificate_id=certificate['certificate_id'],recipe_id='star-successor-with-psd-slack-allocation-on-observed-four-vector-support',rank_profile=ranks,rank_convention=dict(tolerance=1e-4,scaling='absolute unscaled Gram coordinates at L=R=1',basis_order='setup iteration order'),rank_credible=all(not any(5e-5 < v < 2e-4 for v in sv) for sv in singular_values),certificate_checked=certificate_checked,grouping_checked=grouping_checked,singular_values=singular_values,coverage_residual=coverage_residual,increment_residuals=increment_residuals,boundary_exclusions=dict(left=rank_left,right=rank_right),certificate_path=certificate_path)
(root/f'supplementary/rank_N{N}.json').write_text(json.dumps(observation,indent=2))
print('Singular values:',singular_values)


