import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent / 'helpers'))
import runtime
import json
import numpy as np
import sympy as sp
import pepflow as pf
from certificate import PARAMS, digest, inventory
from feg_setup import get_pep_setup

root=runtime.ATTEMPT
data=json.loads((root/'supplementary/b2-sparse-002.json').read_text())
lamb_code='''def candidate_lambda(name, N, L=sp.S.One):
    N = sp.S(N)
    if name == "initial_condition":
        return 4 * L**2 / N**2
    family, pair = name.split(":")
    p, q = pair.split(",")
    points = {p, q}
    if family == "A monotone":
        if points == {f"x_{N}", "x_star"}:
            return 4 * L / N
        for k in range(1, int(N)):
            if points == {f"x_{k}", f"x_{k+1}"}:
                return 4 * L * k * (k+1) / N**2
    if family == "A Lipschitz":
        for j in range(1, int(N)+1):
            if points == {f"x_{j}", f"x_{2*j-1}/2"}:
                return 2 * sp.Integer(j)**2 / N**2
    return sp.S.Zero
'''
S_code='''def candidate_S(ctx, A, N, L=sp.S.One):
    return (A(ctx[f"x_{N}"]) - 2*L/sp.S(N)*(ctx["x_0"]-ctx["x_star"]))**2
'''
exec(lamb_code)
exec(S_code)
ctx,pb,A=get_pep_setup(6,PARAMS)
pm=pf.ExpressionManager(ctx,resolve_parameters=PARAMS)
entries=inventory(ctx,pb,A)
weighted=sum((candidate_lambda(c.name,6)*(c.lhs-c.rhs) for c,*_ in entries),pf.Scalar.zero())
S_guess=candidate_S(ctx,A,6)
exact=pm.eval_scalar(pb.performance_metric-sp.Rational(4,36)-weighted+S_guess,sympy_mode=True)
exact_checks={name:all(sp.simplify(v)==0 for v in np.asarray(getattr(exact,name),dtype=object).flat) for name in ('inner_prod_coords','func_coords','offset')}
assert all(exact_checks.values())
lambda_error=max(abs(float(candidate_lambda(name,6))-val) for name,val in data['named_dual_values'].items() if val is not None)
S_error=float(np.max(np.abs(np.asarray(pm.eval_scalar(S_guess).inner_prod_coords,dtype=float)-np.array(data['S_matrix']))))
data.update(lamb_code=lamb_code,S_code=S_code,formula_status={'lambda':'candidate','S':'candidate'},closed_form_search={'completed':True,'references_reviewed':[],'reference_scope_note':'No pre-existing case references authorized; candidates derived from this attempt dense and sparse data.','attempts':[{'method':'Inspect support, rational approximations and index-scaled multipliers','outcome':'Candidate monotone 4*L*k*(k+1)/N**2, final-star 4*L/N; Lipschitz 2*j**2/N**2; tau 4*L**2/N**2','matching_atol':1e-4,'max_error':lambda_error,'matching_passed':lambda_error<=1e-4},{'method':'Inspect rank-one S and complete the final residual square','outcome':'Candidate ||A(x_N)-2L/N*(x0-xstar)||**2','matching_atol':1e-4,'max_error':S_error,'matching_passed':S_error<=1e-4},{'method':'Exact symbolic full-coordinate identity at N=6, L=R=1','checks':exact_checks,'outcome':'Exact finite-horizon identity holds; not an arbitrary-horizon proof and not a replacement of saved numerical solve.'}],'unresolved_components':['arbitrary-horizon lambda/S identity','candidate agreement with chosen numerical sample at atol=1e-4']},S_decomp_type='ldl',analytic_full_pep_verified=False,lyapunov_proof_verified=False,proof_valid=data['numerical_certificate_verified'],require_analytic_full_pep=False,sparsity_recipe={'method':'drop dense interpolation multipliers below 1e-6','threshold':1e-6,'support':'monotone adjacent full iterates k=1..N-1 and (x_N,x_star); Lipschitz (x_j,x_{j-1/2}), j=1..N'},candidate_sample_checks={'N':6,'params':{'L':1,'R':1},'exact_coordinate_zero':exact_checks,'lambda_max_error':lambda_error,'S_gram_max_error':S_error})
assert data['certificate_id']==digest(data)
for filename in ('feg_b2.json','feg_relaxed.json'):
    (root/'state'/filename).write_text(json.dumps(data,indent=2,allow_nan=False))
print(json.dumps(data['closed_form_search'],indent=2))

