# Rebuild and revalidate a complete saved primal certificate without solving.
import hashlib
import json
import numpy as np
import pepflow as pf
from pathlib import Path
from pepflow.constraint import ScalarConstraint
from pepflow.utils import Comparator

certificate_checked=False
certificate_keys=('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors','basis_scalars',
                  'opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization','certificate_provenance','numerical_checks','numerical_decomposition')
payload={key:certificate[key] for key in certificate_keys}
assert hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()==certificate['certificate_id']
assert certificate['certificate_provenance']['pep_type']=='primal'
assert certificate['certificate_provenance']['solver_status']=='optimal'
assert certificate['closed_form_search']['completed']
for source,expected in certificate['certificate_provenance']['source_hashes'].items():
    source_path=Path(source).resolve()
    assert source_path.is_relative_to(notebook_dir)
    assert hashlib.sha256(source_path.read_bytes()).hexdigest()==expected
assert Path(pf.__file__).resolve()==notebook_dir/'supplementary/approved/pepflow/__init__.py'
N_int=int(certificate['N_verify'])
N=N_int
params=json.loads(certificate['params_json'])
assert params=={'L':1,'R':1}
ctx,pb,obj=get_pep_setup(N,params)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
ctx.set_as_current()
assert pb.ctx is ctx
entries=[(c,'initial',None,None) for c in pb.init_conditions]
assert not ctx.oper_to_duplets
for owner in ctx.func_to_triplets:
    owner.get_interpolation_constraints(ctx)
    data=ctx.get_constraint_data(owner)
    entries.extend((c,'interpolation',str(owner),str(group)) for group,cs in data.sc_dict.items() for c in cs)
    assert not data.psd_dict
metadata=certificate['constraint_metadata']
saved_duals=certificate['named_dual_values']
assert len(entries)==len({c.name for c,*_ in entries})
assert set(metadata)==set(saved_duals)=={c.name for c,*_ in entries}
assert set(pb.relaxed_constraints).issubset(metadata)
basis=ctx.basis_vectors()
basis_labels=[str(v) for v in basis]
assert basis_labels==certificate['basis_vectors']==certificate['S_row_names']==certificate['S_col_names']
assert [str(v) for v in ctx.basis_scalars()]==certificate['basis_scalars']
pm=pf.ExpressionManager(ctx,resolve_parameters=params)
tol=certificate['numerical_checks']['tolerances']
assert tol['identity_atol']==1e-5 and tol['psd_tol']==1e-6 and tol['dual_tol']==1e-6
S_array=np.asarray(certificate['S_matrix'],dtype=float)
assert S_array.shape==(len(basis),len(basis)) and np.isfinite(S_array).all()
assert np.allclose(S_array,S_array.T,atol=1e-6,rtol=0)
assert np.linalg.eigvalsh((S_array+S_array.T)/2).min()>=-1e-6
S_scalar=sum((float(S_array[i,j])*basis[i]*basis[j] for i,j in np.ndindex(S_array.shape)),pf.Scalar.zero())
weighted_terms={}
interpolation_terms={}
interpolation_pairs={}
extra_terms={}
extra_duals={}
for c,origin,owner,group in entries:
    assert isinstance(c,ScalarConstraint)
    assert metadata[c.name]==dict(origin=origin,owner=owner,group=group,kind='scalar',comparator=c.cmp.value,shape=[],relaxed=c.name in pb.relaxed_constraints)
    value=saved_duals[c.name]
    if c.name in pb.relaxed_constraints:
        assert value is None
        continue
    assert value is not None and np.isfinite(value)
    assert c.cmp==Comparator.EQ or value>=-1e-6
    residual=c.lhs-c.rhs
    if c.cmp in (Comparator.GE,Comparator.SEQ):
        residual=-residual
    weighted_terms[c.name]=value*(pf.Scalar.zero()+residual)
    if origin=='interpolation':
        interpolation_terms[c.name]=weighted_terms[c.name]
        interpolation_pairs[c.name]=tuple(c.name.split(':')[1].split(','))
    elif c.name!=certificate['tau_name']:
        extra_terms[c.name]=weighted_terms[c.name]
        extra_duals[c.name]=value
tau_name=certificate['tau_name']
assert tau_name=='initial_condition' and metadata[tau_name]['origin']=='initial'
assert metadata[tau_name]['comparator']=='LE' and not metadata[tau_name]['relaxed']
assert saved_duals[tau_name]==certificate['tau_sol']
assert certificate['normalization']['tau_name']==tau_name
assert certificate['normalization']['bound_value']==certificate['opt_value']
assert certificate['normalization']['initial_condition']=='||x_0-x_star||^2 <= R^2'
assert certificate['normalization']['performance_metric']=='h(x_N) - h(x_star)'
assert abs(certificate['opt_value']-1/(4*N))<1e-5
certificate_diff=pb.performance_metric-certificate['opt_value']-sum(weighted_terms.values(),pf.Scalar.zero())+S_scalar
value=pm.eval_scalar(certificate_diff)
def max_abs(array):
    return float(np.max(np.abs(np.asarray(array,dtype=float)),initial=0))
certificate_residuals=[max_abs(value.inner_prod_coords),max_abs(value.func_coords),max_abs(value.offset)]
assert max(certificate_residuals)<1e-5
D_saved=np.asarray(certificate['numerical_decomposition']['D'],dtype=float)
E_saved=np.asarray(certificate['numerical_decomposition']['ell_coords'],dtype=float)
assert certificate['numerical_decomposition']['basis_labels']==basis_labels
assert E_saved.shape[1]==len(basis) and D_saved.shape==(len(E_saved),len(E_saved))
assert np.isfinite(D_saved).all() and np.isfinite(E_saved).all()
assert np.allclose(E_saved.T@D_saved@E_saved,S_array,atol=1e-4,rtol=1e-5)
certificate_checked=True
print('Certificate rechecked at N=',N,'Gram/function/offset residuals:',certificate_residuals)
