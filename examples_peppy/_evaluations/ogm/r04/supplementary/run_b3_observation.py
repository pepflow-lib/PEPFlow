import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from runtime import configure
notebook_dir,REPO_ROOT = configure()
import json
import sympy as sp
import pepflow as pf
from ogm_setup import get_pep_setup
certificate_path = sys.argv[1] if len(sys.argv)>1 else 'state/ogm_b2.json'
certificate = json.loads((notebook_dir/certificate_path).read_text())
N_int = certificate['N_verify']
params_sp = {k:sp.S(v) for k,v in json.loads(certificate['params_json']).items()}
ctx,pb,obj = get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
for filename in ('b3_certificate_check.py','b3_decomposition.py','b3_grouping.py'):
    source = (notebook_dir/'supplementary'/filename).read_text(encoding='utf-8-sig')
    exec(compile(source,filename,'exec'))
record = dict(N=N_int,certificate_id=certificate['certificate_id'],recipe_id='forward_chain_star_cumulative_terminal_square_boundary',rank_profile=ranks,rank_convention=dict(tolerance=rank_tolerance,scaling='absolute; no rescaling',coordinate_order='setup context basis order'),singular_values=singular_values,rank_credible=all(not any(0.1*rank_tolerance < s < 10*rank_tolerance for s in sv) for sv in singular_values),certificate_checked=certificate_checked,grouping_checked=grouping_checked,coverage_residuals=coverage_residuals)
(notebook_dir/f'supplementary/b3-observation-N{N_int}.json').write_text(json.dumps(record,indent=2))

