import numpy as np
import pepflow as pf
from pepflow.constraint import ScalarConstraint
from pepflow.utils import Comparator
from certificate_checks import verify_certificate, certificate_digest

assert certificate_digest(certificate) == certificate['certificate_id']
assert certificate['closed_form_search']['completed']
assert certificate['certificate_provenance']['pep_type'] == 'primal'
ctx, pb, pm, checked, _, _, _, fresh_checks = verify_certificate(certificate)
N_int = certificate['N_verify']
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
assert certificate['params_json'] == '{"L": 1, "R": 1}'
assert certificate['normalization']['initial_condition'] == '||x_0-x_star||^2 <= R^2'
assert certificate['normalization']['performance_metric'] == 'f(x_N) - f(x_star)'
assert certificate['normalization']['tau_name'] == 'initial_condition'
assert abs(certificate['normalization']['bound_value']-certificate['opt_value']) < 1e-5
assert abs(certificate['named_dual_values']['initial_condition']-certificate['tau_sol']) < 1e-6
basis = list(ctx.basis_vectors())
S_array = np.asarray(certificate['S_matrix'], dtype=float)
S_scalar = sum((float(S_array[i,j])*basis[i]*basis[j] for i,j in np.ndindex(S_array.shape)), pf.Scalar.zero())
records = [(c,'initial',None,None) for c in pb.init_conditions]
assert not ctx.oper_to_duplets
for owner in ctx.func_to_triplets:
    data = ctx.get_constraint_data(owner)
    assert not data.psd_dict
    records.extend((c,'interpolation',str(owner),str(group)) for group, family in data.sc_dict.items() for c in family)
weighted_terms, group_terms, interpolation_pairs = {}, {}, {}
for con, origin, owner_name, group in records:
    assert isinstance(con, ScalarConstraint)
    meta = dict(origin=origin,owner=owner_name,group=group,kind='scalar',comparator=con.cmp.value,shape=[],relaxed=con.name in pb.relaxed_constraints)
    assert meta == certificate['constraint_metadata'][con.name]
    val = certificate['named_dual_values'][con.name]
    if meta['relaxed']:
        assert val is None
        continue
    assert val is not None
    r = con.lhs - con.rhs
    if con.cmp in (Comparator.GE, Comparator.SEQ):
        r = -r
    weighted_terms[con.name] = float(val)*r
    if origin == 'interpolation':
        group_terms[con.name] = weighted_terms[con.name]
        interpolation_pairs[con.name] = tuple(con.name.split(':')[1].split(','))
assert set(weighted_terms) - set(group_terms) == {'initial_condition'}
raw_diff = pb.performance_metric-certificate['opt_value']-sum(weighted_terms.values(),pf.Scalar.zero())+S_scalar

def coords_max(expression):
    value = pm.eval_scalar(expression)
    return [float(np.max(np.abs(np.asarray(part,dtype=float)),initial=0)) for part in (value.inner_prod_coords,value.func_coords,value.offset)]

assert max(coords_max(raw_diff)) < 1e-5
certificate_checked = True
extra_duals = {}
