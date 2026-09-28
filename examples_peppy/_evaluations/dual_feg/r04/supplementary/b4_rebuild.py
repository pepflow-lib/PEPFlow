# Rebuild the selected B3 snapshot without solving; all replay source is visible in B3.
from pepflow.utils import NUMERICAL_TYPE

b3 = json.loads((notebook_dir / 'state/dual_feg_b3.json').read_text())
certificate = b3
N_int = int(b3['N_verify'])
params_sp: dict[str, NUMERICAL_TYPE] = {'L': sp.S.One, 'R': sp.S.One}
REPO_ROOT = repo_root
ctx, pb, obj = get_pep_setup(N_int, params_sp)
pb.set_relaxed_constraints(b3['relaxed_constraints'])
pm = pf.ExpressionManager(ctx, resolve_parameters=params_sp)
lyap: list[pf.Scalar] = []
ranks: list[int] = []
certificate_checked = False
grouping_checked = False
for field in ('certificate_check_code', 'decomposition_code', 'grouping_code'):
    exec(compile(b3[field], f'<B3 replay {field}>', 'exec'), globals())
assert certificate_checked and grouping_checked
assert ranks == b3['rank_profile']
rank_search = b3['rank_search']
assert rank_search['status'] == 'confirmed' and rank_search['selected_certificate_id'] == b3['certificate_id']
rank_evidence = json.loads((notebook_dir / rank_search['evidence_path']).read_text())
assert rank_evidence['summary'] == rank_search
assert len(set(rank_search['confirmed_horizons'])) >= 2
for k, vk in enumerate(lyap):
    ev = pm.eval_scalar(vk)
    for actual, saved in ((ev.inner_prod_coords, b3['lyap_inner_prod_coords'][k]),
                          (ev.func_coords, b3['lyap_func_coords'][k]), (ev.offset, b3['lyap_offsets'][k])):
        assert np.allclose(np.asarray(actual, dtype=float), saved, atol=1e-4, rtol=1e-5)
print('Selected partial sums replayed, all coordinates agree, fixed exclusions:', rank_search['boundary_exclusions'])
