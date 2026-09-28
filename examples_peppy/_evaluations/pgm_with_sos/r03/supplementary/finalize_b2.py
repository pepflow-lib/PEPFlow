import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/"helpers"))
from runtime import configure, NOTEBOOK_DIR
configure()
import inspect
import json
import hashlib
import numpy as np
import sympy as sp
import pepflow as pf
from pgm_setup import get_pep_setup
from certificates import (inventory, residual, verify, aid_terms, lambda_candidate,
                          fingerprint, maxabs, save)

b1=json.loads((NOTEBOOK_DIR/"state/pgm_b1.json").read_text())
data=json.loads((NOTEBOOK_DIR/"supplementary/b2-sparse-candidate.json").read_text())
dense=json.loads((NOTEBOOK_DIR/"state/pgm_dense.json").read_text())
n=data["N"]
ctx,pb,_=get_pep_setup(n,{"L":sp.S.One,"R":sp.S.One})
pb.set_relaxed_constraints(data["relaxed_constraints"])
assert [str(v) for v in ctx.basis_vectors()] == data["basis_vectors"]
checks,_=verify(ctx,pb,data,dense["opt_value"])
pm=pf.ExpressionManager(ctx,resolve_parameters={"L":sp.S.One,"R":sp.S.One})
terms=aid_terms(ctx,n)
ell=[u for _,_,_,u in terms]
D=np.diag([float(pm.eval_scalar(c)) for _,_,c,_ in terms])
E=np.array([pm.eval_vector(u).coords for u in ell],dtype=float)
aid=sum((c*u**2 for _,_,c,u in terms),pf.Scalar.zero())
aq=pm.eval_scalar(aid)
checks["S_reconstruction_max_abs"]=maxabs(E.T@D@E-np.array(data["S_matrix"]))
assert np.allclose(E.T@D@E,data["S_matrix"],atol=1e-4,rtol=1e-5)
assert maxabs(aq.func_coords)==0 and maxabs(aq.offset)==0
entries=inventory(ctx,pb)
weighted=pf.Scalar.zero()
exact_weighted=pf.Scalar.zero()
fit=[]
for c,*_ in entries:
    v=data["named_dual_values"][c.name]
    candidate=lambda_candidate(c.name,n)
    if v is not None:
        weighted += v*residual(c)
        fit.append(abs(float(candidate)-v))
    else:
        assert candidate==0
    exact_weighted += candidate*residual(c)
sample_diff=pm.eval_scalar(pb.performance_metric-data["opt_value"]-weighted+aid)
checks["aid_identity_gram_max_abs"]=maxabs(sample_diff.inner_prod_coords)
checks["aid_identity_func_max_abs"]=maxabs(sample_diff.func_coords)
checks["aid_identity_offset_abs"]=maxabs(sample_diff.offset)
assert max(checks["aid_identity_"+k] for k in ["gram_max_abs","func_max_abs","offset_abs"])<=1e-5
assert max(fit)<=1e-4
exact=pm.eval_scalar(pb.performance_metric-sp.Rational(1,4*n)-exact_weighted+aid,sympy_mode=True)
exact_zero=all(sp.simplify(v)==0 for v in [*exact.inner_prod_coords.flat,*exact.func_coords.flat,exact.offset])
assert exact_zero
print("All candidate multiplier comparison max:",max(fit))
print("Direct SOS comparison and identity:",checks)
print("Exact fixed N identity:",exact_zero)
tolerances=dict(identity_atol=1e-5,identity_rtol=0.,reconstruction_atol=1e-4,
reconstruction_rtol=1e-5,dual_tol=1e-6,psd_tol=1e-6,dense_opt_atol=1e-5)
state={**b1,**data,
"normalization":{"tau_name":"initial_condition","initial_condition":b1["initial_condition"],
"performance_metric":b1["performance_metric"],"bound_value":data["opt_value"],
"bound_formula":b1["conjectured_rate"],"SOS_scale":1},
"numerical_checks":{"tolerances":tolerances,"residuals":checks,"passed":True},
"numerical_decomposition":{"method":"direct","D":D.tolist(),"ell_coords":E.tolist(),
"basis_labels":data["basis_vectors"],"piece_labels":[[i,j] for i,j,_,_ in terms]},
"closed_form_search":{"completed":True,"references_reviewed":["approved/input.md: fixed PGM SOS aid"],
"attempts":[{"method":"Sparse consecutive pairs plus minimizer outgoing pairs",
"outcome":"Optimum preserved; rational inspection suggests telescoping weights"},
{"method":"Candidate lambda formulas inferred from rational approximations and flow differences",
"max_comparison_error":max(fit),"passed":True},
{"method":"Supplied exact SOS candidate; normalization scale 1","max_error":checks["S_reconstruction_max_abs"],
"fixed_N_exact_identity":exact_zero}],
"unresolved_components":["Arbitrary-horizon identity and analytic Lyapunov proof"]},
"formula_status":{"lambda":"candidate","S":"candidate"},
"lamb_code":inspect.getsource(lambda_candidate),"S_code":inspect.getsource(aid_terms),
"S_decomp_type":"direct","numerical_certificate_verified":True,"analytic_full_pep_verified":False,
"lyapunov_proof_verified":False,"require_analytic_full_pep":False,"proof_valid":True,
"sparsity_recipe":"Keep a=x_star or consecutive forward pairs for both f and g",
"fixed_N_exact_candidate_verified":True}
state["certificate_provenance"]["source_hashes"]=fingerprint()
certificate_keys=("N_verify","params_json","relaxed_constraints","S_matrix","S_row_names","S_col_names",
"basis_vectors","basis_scalars","opt_value","tau_sol","tau_name","named_dual_values","constraint_metadata",
"normalization","certificate_provenance","numerical_checks","numerical_decomposition")
state["certificate_id"]=hashlib.sha256(json.dumps({key:state[key] for key in certificate_keys},
sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
save(NOTEBOOK_DIR/"state/pgm_b2.json",state)
save(NOTEBOOK_DIR/"state/pgm_relaxed.json",state)

