import sys
from pathlib import Path
root=Path.cwd()
exec(compile((root/'supplementary/run_b3_selected.py').read_text(encoding='utf-8-sig'),'run_b3_selected.py','exec'))
exec(compile((root/'supplementary/b3_assess.py').read_text(),'b3_assess.py','exec'))
rank_samples=[json.loads((root/f'supplementary/b3-observation-N{n}.json').read_text()) for n in (4,6)]
rank_search=assess_rank_pattern(rank_samples,certificate['certificate_id'],left=1,right=1)
assert rank_search['status']=='confirmed'
rank_search['evidence_path']='supplementary/rank_search.json'
(root/'supplementary/rank_search.json').write_text(json.dumps({'summary':rank_search,'samples':rank_samples},indent=2))
evaluated=[pm.eval_scalar(v) for v in lyap]
state={**certificate,'grouping_residuals':coverage_residuals,'rank_profile':ranks,'rank_search':rank_search,'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in evaluated],'lyap_func_coords':[np.asarray(v.func_coords,dtype=float).tolist() for v in evaluated],'lyap_offsets':[float(v.offset) for v in evaluated],'certificate_check_code':(root/'supplementary/b3_certificate_check.py').read_text(encoding='utf-8-sig'),'decomposition_code':(root/'supplementary/b3_decomposition.py').read_text(encoding='utf-8-sig'),'grouping_code':(root/'supplementary/b3_grouping.py').read_text(encoding='utf-8-sig')+'\n'+(root/'supplementary/b3_coverage.py').read_text(encoding='utf-8-sig'),'extra_duals':extra_duals,'rank_tolerance':rank_tolerance,'reconstruction_tolerance':tol['reconstruction_atol'],'reconstruction_rtol':tol['reconstruction_rtol'],'grouping_coverage':dict(constraint_assignment=term_assignment,S_assignment=S_assignment,normalization_constraint=tau_name,boundary_constraints=boundary_names,boundary_S=boundary_S,omitted_constraints=[],checked=grouping_checked),'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
(root/'state/bppm_b3.json').write_text(json.dumps(state,indent=2,allow_nan=False))
print('Confirmed rank comparison:',rank_search)

