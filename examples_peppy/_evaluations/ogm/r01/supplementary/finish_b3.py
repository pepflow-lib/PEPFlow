import sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'supplementary/helpers'))
import runtime
import json

sources={name:(root/'supplementary'/name).read_text(encoding='utf-8-sig') for name in ('b3_certificate_check.py','b3_decomposition.py','b3_grouping.py')}
samples=[]
selected_state=None
for cert_path in ('supplementary/ogm_b2_N6.json','state/ogm_b2.json'):
    certificate=json.loads((root/cert_path).read_text())
    for name,source in sources.items():
        exec(compile(source,name,'exec'))
    sample=dict(N=N_int,certificate_id=certificate['certificate_id'],certificate_path=cert_path,recipe_id='star-through-k-consecutive-through-k-terminal-square-boundary',rank_profile=ranks,rank_convention=dict(tolerance=rank_tolerance,scaling='unscaled Gram coordinates',coordinate_order='x0,xstar,g0,...,gN'),rank_credible=rank_credible,certificate_checked=certificate_checked,grouping_checked=grouping_checked,singular_values=singular_values,coverage_residual=coverage_residual)
    assert certificate_checked and grouping_checked and rank_credible
    assert len(retained_ranks)>=3 and set(retained_ranks)=={3}
    samples.append(sample)
    (root/f'supplementary/b3-rank-N{N_int}.json').write_text(json.dumps(sample,indent=2))
    if N_int==4:
        values=[pm.eval_scalar(v) for v in lyap]
        selected_state={**certificate,'rank_profile':ranks,'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in values],'lyap_func_coords':[np.asarray(v.func_coords,dtype=float).tolist() for v in values],'lyap_offsets':[float(v.offset) for v in values],'certificate_check_code':sources['b3_certificate_check.py'],'decomposition_code':sources['b3_decomposition.py'],'grouping_code':sources['b3_grouping.py'],'extra_duals':extra_duals,'rank_tolerance':rank_tolerance,'reconstruction_tolerance':1e-4,'reconstruction_rtol':1e-5,'grouping_coverage':dict(constraint_assignment=term_assignment,S_assignment=S_assignment,normalization_constraint='initial_condition',boundary_constraints=boundary_names,boundary_S=boundary_S,omitted_constraints=[],checked=True),'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
assert selected_state is not None
assert len({s['N'] for s in samples})==2
assert samples[0]['rank_convention']==samples[1]['rank_convention']
summary=dict(status='confirmed',boundary_exclusions=dict(left=1,right=1),rank=3,confirmed_horizons=[4,6],selected_certificate_id=selected_state['certificate_id'],recipe_id=samples[0]['recipe_id'],rank_convention=samples[0]['rank_convention'],unresolved_samples=[],evidence_path='supplementary/rank_search.json')
selected_state['rank_search']=summary
(root/'supplementary/rank_search.json').write_text(json.dumps(dict(summary=summary,samples=samples),indent=2))
(root/'state/ogm_b3.json').write_text(json.dumps(selected_state,indent=2,allow_nan=False))
print(json.dumps(summary,indent=2))
