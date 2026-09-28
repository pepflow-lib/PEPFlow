from pathlib import Path
root=Path(__file__).resolve().parents[1]
w=(root/'supplementary/approved/plugins/pepflow-workflows/skills/lyap-define/references/workflow.md').read_text()
part=w.split('def assess_rank_pattern')[1].split('```')[0]
(root/'supplementary/b3_assess.py').write_text('def assess_rank_pattern'+part)
s=(root/'supplementary/run_b3.py').read_text(encoding='utf-8-sig')
s+='''
source=(notebook_dir/'supplementary/b3_assess.py').read_text()
exec(compile(source,'b3_assess.py','exec'),globals())
rank_samples=[json.loads((notebook_dir/f'supplementary/b3_rank_N{n}.json').read_text()) for n in (4,6)]
rank_search=assess_rank_pattern(rank_samples,certificate['certificate_id'],left=1,right=1)
assert rank_search['status']=='confirmed'
rank_search['evidence_path']='supplementary/rank_search.json'
(notebook_dir/'supplementary/rank_search.json').write_text(json.dumps({'summary':rank_search,'samples':rank_samples},indent=2))
def read_source(name):
    return (notebook_dir/'supplementary'/name).read_text(encoding='utf-8-sig')
evaluated=[pm.eval_scalar(v) for v in lyap]
state={**certificate,'rank_profile':ranks,'rank_search':rank_search,
 'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in evaluated],
 'lyap_func_coords':[np.asarray(v.func_coords,dtype=float).tolist() for v in evaluated],
 'lyap_offsets':[float(v.offset) for v in evaluated],
 'certificate_check_code':read_source('b3_check.py'),
 'decomposition_code':read_source('b3_decomposition.py'),
 'grouping_code':read_source('b3_grouping.py')+'\\n'+read_source('b3_coverage.py'),
 'extra_duals':extra_duals,'rank_tolerance':rank_tolerance,
 'reconstruction_tolerance':tol['reconstruction_atol'],'reconstruction_rtol':tol['reconstruction_rtol'],
 'grouping_coverage':{'constraint_assignment':term_assignment,'S_assignment':S_assignment,
 'normalization_constraint':tau_name,'boundary_constraints':boundary_names,'boundary_S':boundary_S,
 'omitted_constraints':[],'checked':grouping_checked},
 'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
(notebook_dir/'state/bppm_b3.json').write_text(json.dumps(state,indent=2))
print('B3 state saved with cross-horizon confirmation:',rank_search)
'''
(root/'supplementary/finalize_b3.py').write_text(s)
