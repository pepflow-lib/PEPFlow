import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('runtime.py')))
import json
import sympy as sp
import pepflow as pf
from feg_setup import get_pep_setup
notebook_dir=Path(__file__).resolve().parents[1]
REPO_ROOT=notebook_dir/'supplementary/approved'
certificate=json.loads((notebook_dir/'supplementary/N8/feg_b2.json').read_text())
N_int=certificate['N_verify']
params_sp={'L':sp.Integer(1),'R':sp.Integer(1)}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
for filename in ('b3_certificate_check.py','b3_decomposition.py','b3_grouping.py'):
    exec((notebook_dir/'supplementary'/filename).read_text(encoding='utf-8-sig'))
observation=dict(N=N_int,certificate_id=certificate['certificate_id'],recipe_id='step-mon-lip-terminal-whole-S',rank_profile=ranks,singular_values=singular_values,rank_convention=dict(tolerance=rank_tolerance,scaling='none; normalized L=R=1; original Gram coordinates',coordinate_order='chronological setup basis'),rank_credible=all(not any(0.5e-4<s<2e-4 for s in vals) for vals in singular_values),certificate_checked=certificate_checked,grouping_checked=grouping_checked,boundary_exclusions=dict(left=rank_left,right=rank_right),coverage_residuals=coverage_residuals)
(notebook_dir/f'supplementary/b3-observation-N{N_int}.json').write_text(json.dumps(observation,indent=2))
print('Singular values:',singular_values)

