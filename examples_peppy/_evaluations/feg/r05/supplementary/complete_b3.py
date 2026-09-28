import importlib.util
import json
import textwrap
from pathlib import Path
spec = importlib.util.spec_from_file_location('runtime', Path(__file__).parent / 'helpers/runtime.py')
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
from partial_sums import partial_sums

root = runtime.ROOT
b2 = json.loads((root/'state/feg_b2.json').read_text())
sample8 = json.loads((root/'supplementary/feg_certificate_N8.json').read_text())
dense6 = json.loads((root/'state/feg_dense.json').read_text())
dense8 = json.loads((root/'supplementary/feg_dense_N8.json').read_text())
*_, observation6 = partial_sums(b2, dense6['opt_value'])
*_, observation8 = partial_sums(sample8, dense8['opt_value'])
observations = [observation6,observation8]
for obs in observations:
    assert obs['rank_credible'] and obs['certificate_checked'] and obs['grouping_checked']
    retained = obs['rank_profile'][1:-1]
    assert len(retained)>=3 and set(retained)=={2}
assert observation6['recipe_id'] == observation8['recipe_id']
assert observation6['rank_convention'] == observation8['rank_convention']
summary = dict(status='confirmed',boundary_exclusions={'left':1,'right':1},rank=2,confirmed_horizons=[6,8],
               selected_certificate_id=b2['certificate_id'],recipe_id=observation6['recipe_id'],
               rank_convention=observation6['rank_convention'],unresolved_samples=[],evidence_path='supplementary/rank_search.json')
(root/'supplementary/rank_N8.json').write_text(json.dumps(observation8,indent=2))
(root/'supplementary/rank_search.json').write_text(json.dumps({'summary':summary,'samples':observations},indent=2))
source = (root/'supplementary/helpers/partial_sums.py').read_text(encoding='utf-8-sig')
verify = (root/'supplementary/helpers/verify_certificate.py').read_text(encoding='utf-8-sig')
dec_start = source.index('    D = np.asarray')
dec_end = source.index('    assignment = {}')
decomposition_code = 'basis = ctx.basis_vectors()\n' + textwrap.dedent(source[dec_start:dec_end])
grouping_code = source + '\nctx, pb, obj, pm, lyap, observation = partial_sums(certificate, dense_value)\ngrouping_checked = observation["grouping_checked"]\n'
check_code = verify + '\nctx, pb, obj, pm, checked, numerical_checks = verify_saved(certificate, dense_value)\ncertificate_checked = numerical_checks["passed"]\n'
b3 = dict(b2,rank_profile=observation6['rank_profile'],rank_search=summary,
          lyap_inner_prod_coords=observation6['lyap_inner_prod_coords'],lyap_func_coords=observation6['lyap_func_coords'],lyap_offsets=observation6['lyap_offsets'],
          certificate_check_code=check_code,decomposition_code=decomposition_code,grouping_code=grouping_code,
          extra_duals={},rank_tolerance=1e-4,reconstruction_tolerance=1e-4,reconstruction_rtol=1e-5,
          grouping_coverage=dict(constraint_assignment=observation6['constraint_assignment'],S_assignment=observation6['S_assignment'],normalization_constraint='initial_condition',boundary_constraints=observation6['boundary_constraints'],boundary_S=observation6['boundary_S'],omitted_constraints=[],checked=True),
          numerical_certificate_verified=True,analytic_full_pep_verified=False,lyapunov_proof_verified=False)
(root/'state/feg_b3.json').write_text(json.dumps(b3,indent=2))
print('Confirmed rank 2 at N=6,8 with fixed exclusions (1,1).')
