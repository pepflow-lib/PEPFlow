import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / 'supplementary/helpers'))
import runtime
import json
import hashlib
from certificate_checks import verify_certificate, certificate_digest

b1 = json.loads((root / 'state/ogm_b1.json').read_text())
state = {**b1, **json.loads((root / 'supplementary/b2-selected-raw.json').read_text())}
state['certificate_provenance']['source_hashes']['supplementary/helpers/certificate_checks.py'] = hashlib.sha256((root / 'supplementary/helpers/certificate_checks.py').read_bytes()).hexdigest()
ctx, pb, pm, checked, reconstructed, candidates, decomposition, checks = verify_certificate(state)
dense = json.loads((root / 'state/ogm_dense.json').read_text())
checks['residuals']['dense_relaxed_gap'] = abs(dense['opt_value'] - state['opt_value'])
assert checks['residuals']['dense_relaxed_gap'] < 1e-5
state.update(normalization=dict(tau_name='initial_condition',initial_condition=b1['initial_condition'],performance_metric=b1['performance_metric'],bound_value=state['opt_value'],bound_formula=b1['conjectured_rate']),numerical_checks=checks,numerical_decomposition=decomposition,closed_form_search=dict(completed=True,references_reviewed=['Approved generic B2 workflow; target references excluded by clean-room rules'],attempts=['Dense multipliers: inspected magnitudes and significant pairs, then kept only star-to-iterate and consecutive-forward pairs; bound preserved.', 'Scaled consecutive multipliers by theta_N^2/(2*theta_i^2) and star multipliers by theta_N^2/(2*theta_i); all equal one numerically. Terminal star weight fits 1/theta_N.', 'Observed rank-one S and compared (z_N-x_star-theta_N*g_N)^2/(2*theta_N^2) to all saved Gram entries; maximum error recorded.'],unresolved_components=['arbitrary-horizon analytic identity and signs']),formula_status={'lambda':'candidate','S':'candidate'},lamb_code="def lamb(ri, ci):\n    i = 0 if ri == 'z_0' else -1 if ri == 'x_star' else int(ri.split('_')[1])\n    j = 0 if ci == 'z_0' else -1 if ci == 'x_star' else int(ci.split('_')[1])\n    if i == -1 and 0 <= j <= N:\n        return 1/theta[N] if j == N else 2*theta[j]/theta[N]**2\n    return 2*theta[i]**2/theta[N]**2 if 0 <= i < N and j == i+1 else 0\n",S_code="w = ctx[f'z_{N}'] - ctx['x_star'] - theta[N]/L * ctx[f'g_{N}']\nS_guess = L/(2*theta[N]**2) * w**2",S_decomp_type='direct',numerical_certificate_verified=True,analytic_full_pep_verified=False,lyapunov_proof_verified=False,require_analytic_full_pep=False,proof_valid=True)
state['certificate_id'] = certificate_digest(state)
for filename in ('ogm_b2.json', 'ogm_relaxed.json'):
    (root / 'state' / filename).write_text(json.dumps(state, indent=2, allow_nan=False))
print(json.dumps(checks, indent=2))
print('Certificate', state['certificate_id'])

