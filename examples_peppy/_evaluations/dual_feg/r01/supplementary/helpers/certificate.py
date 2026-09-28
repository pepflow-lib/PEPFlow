"""Attempt-local complete primal certificate acquisition and revalidation."""
import hashlib
import json
import uuid
from importlib.metadata import version
from pathlib import Path

import numpy as np
import sympy as sp
import pepflow as pf
from pepflow.utils import Comparator
from dual_feg_setup import get_pep_setup


def inventory(ctx, pb):
    entries = [(c, 'initial', None, None) for c in pb.init_conditions]
    for owner in [*ctx.func_to_triplets, *ctx.oper_to_duplets]:
        groups = ctx.get_constraint_data(owner)
        entries.extend((c, 'interpolation', str(owner), str(group)) for group, cs in groups.sc_dict.items() for c in cs)
        entries.extend((c, 'interpolation', str(owner), str(group)) for group, c in groups.psd_dict.items())
    return entries


def acquire(n, relaxed, root):
    allowlist = json.loads((root/'supplementary/approved/allowlist.json').read_text())
    paths = [root/'dual_feg_setup.py', Path(__file__), *[Path(p) for p in allowlist['exact_read_files'] if Path(p).parent.name == 'pepflow']]
    hashes = {str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

    ctx, pb, obj = get_pep_setup(n, {'L': 1, 'R': 1})
    if relaxed:
        pb.set_relaxed_constraints(relaxed)
    entries = inventory(ctx, pb)
    constraints = [c for c, *_ in entries if c.name not in relaxed]
    solver = pf.CVXPrimalSolver(perf_metric=pb.performance_metric, constraints=constraints, context=ctx)
    problem = solver.build_problem(resolve_parameters={'L': sp.Integer(1), 'R': sp.Integer(1)})
    options = {'solver': 'CLARABEL'}
    try:
        value = problem.solve(**options)
    except Exception as error:
        print('CLARABEL failure:', repr(error), flush=True)
        options = {'solver': 'SCS', 'eps': 1e-7, 'max_iters': 200000}
        value = problem.solve(**options)
    result = pf.PEPResult(opt_value=value, dual_var_manager=solver.dual_var_manager, pep_type=pf.PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    meta, duals = {}, {}
    for c, origin, owner, group in entries:
        scalar = isinstance(c, pf.ScalarConstraint)
        dropped = c.name in relaxed
        v = result.get_dual_value(c.name)
        if not dropped:
            assert v is not None
        meta[c.name] = {'origin': origin, 'owner': owner, 'group': group, 'kind': 'scalar' if scalar else 'psd', 'comparator': c.cmp.value, 'shape': [] if scalar else list(np.asarray(c.lhs-c.rhs).shape), 'relaxed': dropped}
        duals[c.name] = None if dropped else float(v) if scalar and v is not None else np.asarray(v).tolist()
    sm = result.get_gram_dual_matrix()
    groups = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert isinstance(groups, dict)
    displays = {str(k): {'matrix':np.asarray(v.matrix, dtype=float).tolist(), 'row_names':list(v.row_names), 'col_names':list(v.col_names)} for k,v in groups.items()}
    tau = result.get_dual_value('initial_condition')
    assert tau is not None
    return {'N':n,'N_verify':n,'params_json':'{"L": 1, "R": 1}', 'opt_value':float(value), 'tau_sol':float(tau), 'tau_name':'initial_condition','relaxed_constraints':list(relaxed), 'S_matrix':np.asarray(sm.matrix,dtype=float).tolist(), 'S_row_names':list(sm.row_names),'S_col_names':list(sm.col_names),'basis_vectors':[str(v) for v in ctx.basis_vectors()],'basis_scalars':[str(v) for v in ctx.basis_scalars()],'lambda_groups':displays,'constraint_metadata':meta,'named_dual_values':duals,'certificate_provenance':{'solve_id':str(uuid.uuid4()),'pep_type':'primal','solver_status':str(problem.status),'source_hashes':hashes,'solver':{'api':'CVXPrimalSolver.build_problem; cvxpy.Problem.solve','effective_name':problem.solver_stats.solver_name,'settings':options,'cvxpy_version':version('cvxpy')}}}


def residual(c):
    r = c.lhs-c.rhs
    return -r if c.cmp in (Comparator.GE, Comparator.SEQ) else r


def reconstruct(data):
    ctx, pb, obj = get_pep_setup(data['N_verify'], json.loads(data['params_json']))
    ctx.set_as_current()
    entries = inventory(ctx, pb)
    assert set(data['constraint_metadata']) == {c.name for c, *_ in entries}
    assert data['basis_vectors'] == [str(v) for v in ctx.basis_vectors()]
    pm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(data['params_json']))
    return ctx, pb, obj, entries, pm


def verify(data, dense_value):
    ctx, pb, obj, entries, pm = reconstruct(data)
    weighted = pf.Scalar.zero()
    scalar_duals, matrix_eigs = [], []
    for c, *_ in entries:
        meta = data['constraint_metadata'][c.name]
        v = data['named_dual_values'][c.name]
        if meta['relaxed']:
            assert v is None
            continue
        if meta['kind'] == 'scalar':
            weighted += float(v) * (pf.Scalar.zero()+residual(c))
            if c.cmp != Comparator.EQ:
                scalar_duals.append(float(v))
        else:
            a = np.asarray(v,dtype=float)
            rr = residual(c)
            weighted += sum((a[i,j]*rr[j,i] for i,j in np.ndindex(a.shape)), pf.Scalar.zero())
            matrix_eigs.extend(np.linalg.eigvalsh(a))
    basis = ctx.basis_vectors()
    s = np.asarray(data['S_matrix'])
    S_numeric = sum((s[i,j]*basis[i]*basis[j] for i,j in np.ndindex(s.shape)),pf.Scalar.zero())
    checked = pm.eval_scalar(pb.performance_metric-data['opt_value']-weighted+S_numeric)
    def maximum(a):
        return float(np.max(np.abs(np.asarray(a,dtype=float)),initial=0))
    checks = {'identity_gram_max_abs':maximum(checked.inner_prod_coords),'identity_func_max_abs':maximum(checked.func_coords),'identity_offset_abs':maximum(checked.offset),'dense_relaxed_gap':abs(data['opt_value']-dense_value),'minimum_scalar_inequality_dual':min(scalar_duals,default=0), 'minimum_S_eigenvalue':float(np.linalg.eigvalsh(s).min()), 'minimum_matrix_inequality_eigenvalue':min(matrix_eigs,default=0)}
    passed = data['certificate_provenance']['solver_status']=='optimal' and all(checks[k]<=1e-5 for k in ['identity_gram_max_abs','identity_func_max_abs','identity_offset_abs','dense_relaxed_gap']) and min(checks[k] for k in ['minimum_scalar_inequality_dual','minimum_S_eigenvalue','minimum_matrix_inequality_eigenvalue']) >= -1e-6
    return checks, passed


