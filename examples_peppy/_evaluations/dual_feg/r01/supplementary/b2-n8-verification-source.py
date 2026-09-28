import json
import hashlib
import numpy as np
import sympy as sp
import pepflow as pf
from fractions import Fraction
from certificate import reconstruct, residual
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis

b1 = json.loads((notebook_dir / 'state/dual_feg_b1.json').read_text())
dense = json.loads((notebook_dir / 'supplementary/b2-n8-dense.json').read_text())
selected = json.loads((notebook_dir / 'supplementary/b2-n8-sparse.json').read_text())
n = selected['N_verify']
ctx, pb, obj, entries, pm = reconstruct(selected)
S_array = np.asarray(selected['S_matrix'], dtype=float)
basis = ctx.basis_vectors()
S_named = pf.MatrixWithNames(S_array, selected['S_row_names'], selected['S_col_names'])
D, ell = ldl_decompose_with_reversed_basis(S_named, basis, print_output=False)
E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
S_numeric = sum((float(D[i,j])*ell[i]*ell[j] for i,j in np.ndindex(D.shape)),pf.Scalar.zero())
S_reconstructed = E.T @ D @ E
print('Dense bound:', dense['opt_value'], 'selected bound:', selected['opt_value'])
print('Basis:', selected['basis_vectors'])
print('Dropped constraints:',len(selected['relaxed_constraints']))
print('Dense active counts:', {g:sum(v is not None and abs(v)>1e-6 and dense['constraint_metadata'][name]['group']==g for name,v in dense['named_dual_values'].items()) for g in dense['lambda_groups']})
print('Selected S eigenvalues:',np.linalg.eigvalsh(S_array))
print('Reverse LDL diagonal:',np.diag(D))
pf.pprint_labeled_matrix(pf.MatrixWithNames(E, [f'ell_{i}' for i in range(len(E))], selected['basis_vectors']))


def lambda_candidate(name, N):
    if name == 'initial_condition':
        return sp.Rational(4,N**2)
    if name == f'A monotone:x_{N},x_star':
        return sp.Rational(4,N)
    for k in range(N-1):
        if name == f'A monotone:x_{N},y_{k}':
            return sp.Rational(4,(N-k)*(N-k-1))
        if name == f'A Lipschitz:x_{k},y_{k}':
            return sp.Rational(2,(N-k)**2)
    if name == f'A Lipschitz:x_{N-1},x_{N}':
        return sp.Integer(2)
    return sp.Integer(0)

lambda_errors=[]
for name,value in selected['named_dual_values'].items():
    if value is not None:
        error=abs(float(lambda_candidate(name,n))-value)
        lambda_errors.append(error)
        print(name,value,'fraction=',str(Fraction(value).limit_denominator(10000)),'candidate=',lambda_candidate(name,n),'error=',error)
S_guess=(sp.Rational(2,n)*(ctx['x_0']-ctx['x_star'])-ctx[f'g_{n}'])**2
sg=pm.eval_scalar(S_guess,sympy_mode=True)
S_guess_array=np.asarray(sg.inner_prod_coords,dtype=float)
candidate_S_error=float(np.max(np.abs(S_guess_array-S_array)))
print('Candidate S = ||2(x_0-x_star)/N - A(x_N)||^2 at L=1; error:',candidate_S_error)
pf.pprint_labeled_matrix(pf.MatrixWithNames(S_guess_array,selected['basis_vectors'],selected['basis_vectors']))
exact_weighted=sum((lambda_candidate(c.name,n)*(pf.Scalar.zero()+residual(c)) for c,*_ in entries),pf.Scalar.zero())
exact_identity=pm.eval_scalar(pb.performance_metric-sp.Rational(4,n*n)-exact_weighted+S_guess,sympy_mode=True)
exact_sample=all(sp.simplify(v)==0 for a in [exact_identity.inner_prod_coords,exact_identity.func_coords,np.atleast_1d(exact_identity.offset)] for v in np.asarray(a).flat)
print('Exact candidate identity at selected finite horizon:',exact_sample)
weighted=pf.Scalar.zero()
scalar_duals=[]
for c,*_ in entries:
    meta=selected['constraint_metadata'][c.name]
    v=selected['named_dual_values'][c.name]
    if meta['relaxed']:
        assert v is None
        continue
    assert meta['kind']=='scalar'
    weighted+=float(v)*(pf.Scalar.zero()+residual(c))
    scalar_duals.append(float(v))
checked=pm.eval_scalar(pb.performance_metric-selected['opt_value']-weighted+S_numeric)


def max_abs(a):
    return float(np.max(np.abs(np.asarray(a,dtype=float)),initial=0))

residuals={'identity_gram_max_abs':max_abs(checked.inner_prod_coords),'identity_func_max_abs':max_abs(checked.func_coords),'identity_offset_abs':max_abs(checked.offset),'S_reconstruction_max_abs':max_abs(S_reconstructed-S_array),'dense_relaxed_gap':abs(dense['opt_value']-selected['opt_value']),'minimum_scalar_inequality_dual':min(scalar_duals),'minimum_S_eigenvalue':float(np.linalg.eigvalsh(S_array).min()),'minimum_matrix_inequality_eigenvalue':0.0}
tolerances={'identity_atol':1e-5,'identity_rtol':0.0,'reconstruction_atol':1e-4,'reconstruction_rtol':1e-5,'dual_tol':1e-6,'psd_tol':1e-6,'dense_opt_atol':1e-5}
passed=(selected['certificate_provenance']['solver_status']=='optimal' and np.isfinite(S_array).all() and np.allclose(S_array,S_array.T,atol=1e-6,rtol=0) and all(residuals[k]<=1e-5 for k in ['identity_gram_max_abs','identity_func_max_abs','identity_offset_abs','dense_relaxed_gap']) and np.allclose(S_reconstructed,S_array,atol=1e-4,rtol=1e-5) and residuals['minimum_scalar_inequality_dual']>=-1e-6 and residuals['minimum_S_eigenvalue']>=-1e-6)
print('Numerical certificate checks:',residuals,'passed=',passed)
pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(checked.inner_prod_coords,dtype=float),selected['basis_vectors'],selected['basis_vectors']))
assert passed
assert max(lambda_errors)<=1e-4 and candidate_S_error<=1e-4
search={'completed':True,'references_reviewed':['Approved generic operator API and own B1/B2 results; no target reference authorized.'],'attempts':[{'method':'Rational reconstruction and dependence on remaining horizon N-k','maximum_lambda_error':max(lambda_errors),'outcome':'Candidate formulas match retained scalar duals within 1e-4.'},{'method':'Inspect rank-one S and initial/final coordinate coupling','S_candidate':'||2(x_0-x_star)/N - g_N||^2 (L=1)','maximum_S_error':candidate_S_error,'exact_fixed_N_identity':exact_sample,'outcome':'Finite-horizon candidate check; arbitrary-horizon derivation pending.'}],'unresolved_components':['arbitrary-horizon validity of lambda and S formulas']}
state={**b1,**selected,'normalization':{'tau_name':'initial_condition','initial_condition':b1['initial_condition'],'performance_metric':b1['performance_metric'],'bound_value':selected['opt_value'],'bound_formula':b1['conjectured_rate']},'numerical_checks':{'tolerances':tolerances,'residuals':residuals,'passed':bool(passed)},'numerical_decomposition':{'method':'reverse_ldl','D':D.tolist(),'ell_coords':E.tolist(),'basis_labels':selected['basis_vectors']},'S_decomp_type':'ldl','closed_form_search':search,'formula_status':{'lambda':'candidate','S':'candidate'},'lamb_code':None,'S_code':'S_guess = (sp.Rational(2,N)*(ctx["x_0"]-ctx["x_star"])-ctx[f"g_{N}"])**2','numerical_certificate_verified':bool(passed),'analytic_full_pep_verified':False,'lyapunov_proof_verified':False,'require_analytic_full_pep':False,'proof_valid':bool(passed)}
source=(notebook_dir/'supplementary/b2_certificate_cells.py').read_text(encoding='utf-8-sig')
state['lamb_code']='def lambda_candidate'+source.split('def lambda_candidate',1)[1].split('\nlambda_errors',1)[0]
for relative_path,expected in state['certificate_provenance']['source_hashes'].items():
    assert hashlib.sha256((notebook_dir/relative_path).read_bytes()).hexdigest()==expected
certificate_keys=('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')
state['certificate_id']=hashlib.sha256(json.dumps({k:state[k] for k in certificate_keys},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
for filename in ['dual_feg_relaxed.json','dual_feg_b2.json']:
    (notebook_dir/'supplementary'/('n8-'+filename)).write_text(json.dumps(state,indent=2,allow_nan=False))
