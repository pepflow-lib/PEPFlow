rank_samples=[json.loads((notebook_dir/'supplementary'/f'b3-n{n:02d}-observation.json').read_text()) for n in (4,6)]
assert rank_samples[0]['certificate_id']==certificate['certificate_id']
assert rank_samples[0]['rank_profile']==ranks
for sample in rank_samples:
    assert sample['certificate_checked'] and sample['grouping_checked']
    assert sample['recipe_id']=='reverse_ldl_pivot_delay_0'
    assert sample['boundary_exclusions']=={'left':1,'right':1}
    retained=sample['rank_profile'][1:-1]
    assert len(retained)>=3 and set(retained)=={5}
    for values in sample['singular_values'][1:-1]:
        assert values[4]>1e-3 and values[5]<1e-5
rank_search={'status':'confirmed','boundary_exclusions':{'left':1,'right':1},'rank':5,
    'confirmed_horizons':[4,6],'selected_certificate_id':certificate['certificate_id'],
    'recipe_id':'reverse_ldl_pivot_delay_0','rank_convention':rank_samples[0]['rank_convention'],
    'unresolved_samples':[],'evidence_path':'supplementary/rank_search.json'}
print('Cross-horizon rank:',rank_search['rank'],'at horizons',rank_search['confirmed_horizons'],
      'with fixed exclusions (1,1), absolute unscaled tolerance 1e-4.')
(notebook_dir/'supplementary/rank_search.json').write_text(json.dumps({'summary':rank_search,'samples':rank_samples},indent=2))
certificate_check_code=(notebook_dir/'supplementary/b3_certificate_check.py').read_text(encoding='utf-8-sig')
decomposition_code=(notebook_dir/'supplementary/b3_decomposition.py').read_text(encoding='utf-8-sig')
grouping_code=(notebook_dir/'supplementary/b3_grouping.py').read_text(encoding='utf-8-sig')
evaluated_lyap=[pm.eval_scalar(Vk) for Vk in lyap]
b3={**certificate,'rank_profile':ranks,'rank_search':rank_search,
    'lyap_inner_prod_coords':[np.asarray(v.inner_prod_coords,dtype=float).tolist() for v in evaluated_lyap],
    'lyap_func_coords':[np.asarray(v.func_coords,dtype=float).tolist() for v in evaluated_lyap],
    'lyap_offsets':[float(v.offset) for v in evaluated_lyap],
    'certificate_check_code':certificate_check_code,'decomposition_code':decomposition_code,
    'grouping_code':grouping_code,'extra_duals':extra_duals,'rank_tolerance':rank_tolerance,
    'reconstruction_tolerance':1e-4,'reconstruction_rtol':1e-5,
    'grouping_coverage':{'constraint_assignment':term_assignment,'S_assignment':S_assignment,
        'normalization_constraint':tau_name,'boundary_constraints':[],'boundary_S':[],
        'omitted_constraints':[],'checked':True},
    'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
assert certificate_checked and grouping_checked
(notebook_dir/'state/pgm_b3.json').write_text(json.dumps(b3,indent=2,allow_nan=False))
