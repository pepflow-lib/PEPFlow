from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import hashlib
import textwrap
import nbformat
from nbclient import NotebookClient
import os

root=runtime.ROOT
certificate=json.loads((root/'state/pgm_b2.json').read_text())
checker=(root/'supplementary/b3_certificate_check.py').read_text(encoding='utf-8-sig')
checker=checker.replace('ScalarConstraint, PSDConstraint','ScalarConstraint').replace('from pepflow.pep_result import MatrixWithNames', '').replace('S_sol = MatrixWithNames(S_array, basis_labels, basis_labels)', '')
grouping=(root/'supplementary/b3_grouping.py').read_text(encoding='utf-8-sig')
coverage=(root/'supplementary/b3_coverage_check.py').read_text()
setup='''import json
N_int = certificate['N_verify']
params_sp = json.loads(certificate['params_json'])
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
REPO_ROOT = notebook_dir
'''
body=setup+checker+'\n'+grouping+'\n'+coverage+'''
evaluated = [pm.eval_scalar(value) for value in lyap]
observation = dict(N=N_int,certificate_id=certificate['certificate_id'],recipe_id='forward_star_consecutive_three_sos_refined_dual',rank_profile=ranks,rank_convention={'tolerance':1e-4,'scaling':'unscaled Gram coordinates','order':'setup basis order'},rank_credible=rank_credible,certificate_checked=certificate_checked,grouping_checked=grouping_checked,singular_values=singular_values)
return dict(observation=observation,lyap_inner_prod_coords=[np.array(v.inner_prod_coords,dtype=float).tolist() for v in evaluated],lyap_func_coords=[np.array(v.func_coords,dtype=float).tolist() for v in evaluated],lyap_offsets=[float(v.offset) for v in evaluated],grouping_coverage=dict(constraint_assignment=term_assignment,S_assignment=S_assignment,normalization_constraint=tau_name,boundary_constraints=boundary_names,boundary_S=boundary_S,omitted_constraints=[],checked=True),extra_duals=extra_duals)
'''
function='def reconstruct_partial_sums(certificate):\n'+textwrap.indent(body,'    ')
call='''certificate = json.loads((notebook_dir/'state/pgm_b2.json').read_text())
other_certificate = json.loads((notebook_dir/'supplementary/b2-N6-certificate.json').read_text())
print('Selected horizon:', certificate['N_verify'])
selected_partial_sums = reconstruct_partial_sums(certificate)
print('Confirmation horizon:', other_certificate['N_verify'])
other_partial_sums = reconstruct_partial_sums(other_certificate)
rank_samples = [selected_partial_sums['observation'],other_partial_sums['observation']]
assert len({sample['N'] for sample in rank_samples}) == 2
assert all(sample['rank_profile'][1:sample['N']] == [4]*(sample['N']-1) for sample in rank_samples)
assert all(sample['certificate_checked'] and sample['grouping_checked'] and sample['rank_credible'] for sample in rank_samples)
print('Cross-horizon confirmation: N=4,6; interior rank 4; exclusions (1,1); unscaled tolerance 1e-4.')
'''
(root/'supplementary/b3_notebook_code.py').write_text(function+'\n'+call)
namespace={'notebook_dir':root}
exec((root/'pgm_setup.py').read_text(),namespace)
exec('import json\nimport numpy as np\nimport sympy as sp\n'+certificate['S_code'],namespace)
exec(function+'\n'+call,namespace)
selected=namespace['selected_partial_sums']
samples=namespace['rank_samples']
rank_search=dict(status='confirmed',boundary_exclusions={'left':1,'right':1},rank=4,confirmed_horizons=[4,6],selected_certificate_id=certificate['certificate_id'],recipe_id=samples[0]['recipe_id'],rank_convention=samples[0]['rank_convention'],unresolved_samples=[],evidence_path='supplementary/rank_search.json')
(root/'supplementary/rank_search.json').write_text(json.dumps({'summary':rank_search,'samples':samples},indent=2))
state={**certificate,**{k:v for k,v in selected.items() if k!='observation'},'rank_profile':samples[0]['rank_profile'],'rank_search':rank_search,'certificate_check_code':checker,'decomposition_code':certificate['S_code']+'\npieces, coefficients, vectors = supplied_sos(ctx, N_int, 1)\nS_piece_terms = {f"S_{i+1}":piece for i,piece in enumerate(pieces)}\n','grouping_code':grouping+'\n'+coverage,'rank_tolerance':1e-4,'reconstruction_tolerance':1e-4,'reconstruction_rtol':1e-5}
(root/'state/pgm_b3.json').write_text(json.dumps(state,indent=2))
path=root/'pgm_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Partial-sum'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Identify the vectors'))
nb.cells[start:end]=[nbformat.v4.new_markdown_cell(r'''## Partial-sum Lyapunov construction and rank profile
Let $I^f_{u,v}\leq0$ and $I^g_{u,v}\leq0$ denote the normalized interpolation residuals, and $S_i\geq0$ the three-square piece supplied at iteration $i$. Set $V_0=0$, add the $f$ optimizer-to-zero term in the first increment, and thereafter accumulate
$$V_{k+1}-V_k=\sum_{c\text{ assigned to }k}\lambda_c I_c-S_{k+1}\leq0.$$
Each interpolation residual appears exactly once in the partial sums, and all square pieces are subtracted. The complete original grouping is restored after refining the coherent certificates. The numerical profile is rank four for every interior index at $N=4$ and $N=6$, with fixed exclusions of $V_0,V_N$. The terminal rank is one because the initial squared-distance normalization remains. Full-coordinate coverage is checked below. These finite-sample observations do not establish the analytic theorem.'''),nbformat.v4.new_code_cell(function),nbformat.v4.new_code_cell(call)]
nbformat.write(nb,path)
os.environ['JUPYTER_PATH']=str(runtime.RUNTIME/'jupyter')
NotebookClient(nb,timeout=180,kernel_name='attempt-python',resources={'metadata':{'path':str(root)}}).execute()
nbformat.write(nb,path)
print('B3 notebook executed; hash',hashlib.sha256(path.read_bytes()).hexdigest())




