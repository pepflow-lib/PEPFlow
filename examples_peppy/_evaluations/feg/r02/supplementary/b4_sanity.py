b3 = json.loads((notebook_dir/'state/feg_b3.json').read_text())
assert certificate_checked and grouping_checked
assert certificate['certificate_id']==b3['certificate_id']
assert ranks==b3['rank_profile']
rank_search=b3['rank_search']
rank_evidence=json.loads((notebook_dir/rank_search['evidence_path']).read_text())
assert rank_evidence['summary']==rank_search
assert rank_search['status']=='confirmed' and rank_search['confirmed_horizons']==[6,8]
assert rank_search['boundary_exclusions']=={'left':1,'right':1}
for k,Vk in enumerate(lyap):
    value=pm.eval_scalar(Vk)
    for actual,saved in ((value.inner_prod_coords,b3['lyap_inner_prod_coords'][k]),(value.func_coords,b3['lyap_func_coords'][k]),(value.offset,b3['lyap_offsets'][k])):
        assert np.allclose(np.asarray(actual,dtype=float),np.asarray(saved,dtype=float),atol=1e-4,rtol=1e-5)
print('Selected partial sums and cross-horizon evidence replayed; all indices 0 through',N_int,'retained for reconstruction.')
