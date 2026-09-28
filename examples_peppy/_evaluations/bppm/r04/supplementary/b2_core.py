"""Complete primal capture for the B2 mathematical workflow."""
import hashlib
import json
import uuid
from pathlib import Path

import cvxpy as cp
import numpy as np
import pepflow as pf
from bppm_setup import get_pep_setup


def max_abs(values):
    return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0.0))


def entries_of(ctx, pb):
    entries = [(c, 'initial', None, None) for c in pb.init_conditions]
    for owner in ctx.func_to_triplets:
        groups = ctx.get_constraint_data(owner)
        entries.extend((c, 'interpolation', str(owner), str(group))
                       for group, constraints in groups.sc_dict.items() for c in constraints)
        assert not groups.psd_dict
    assert not ctx.oper_to_duplets
    assert len({c.name for c, *_ in entries}) == len(entries)
    return entries


def solve_capture(N, params, relaxed, root):
    source_paths = [root / 'bppm_setup.py', root / 'supplementary/b2_core.py']
    allowed = json.loads((root / 'supplementary/approved/allowlist.json').read_text())
    source_paths += [Path(p) for p in allowed['exact_read_files'] if Path(p).parent == root / 'supplementary/approved/pepflow']
    hashes = {str(p.relative_to(root)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    ctx, pb, obj = get_pep_setup(N, params)
    pb.set_relaxed_constraints(relaxed)
    entries = entries_of(ctx, pb)
    constraints = [c for c, *_ in entries if c.name not in relaxed]
    solver = pf.CVXPrimalSolver(perf_metric=pb.performance_metric,
                               constraints=constraints, context=ctx)
    problem = solver.build_problem(resolve_parameters=params)
    options = {'solver': 'CLARABEL'}
    try:
        value = problem.solve(**options)
    except cp.error.SolverError:
        options = {'solver': 'SCS', 'eps': 1e-7, 'max_iters': 200000}
        value = problem.solve(**options)
    result = pf.PEPResult(opt_value=float(value), dual_var_manager=solver.dual_var_manager,
                          pep_type=pf.PEPType.PRIMAL, solver_status=problem.status, context=ctx)
    assert problem.status == 'optimal'
    S = result.get_gram_dual_matrix()
    meta, duals = {}, {}
    for c, origin, owner, group in entries:
        assert isinstance(c, pf.ScalarConstraint)
        dropped = c.name in relaxed
        d = result.get_dual_value(c.name)
        assert dropped or d is not None
        if d is not None:
            assert np.isfinite(d)
        meta[c.name] = dict(origin=origin, owner=owner, group=group, kind='scalar',
                            comparator=c.cmp.value, shape=[], relaxed=dropped)
        if dropped:
            duals[c.name] = None
        else:
            assert d is not None
            duals[c.name] = float(d)
    data = dict(N=N, N_verify=N, params_json=json.dumps(params), opt_value=float(value),
                tau_sol=duals['initial_condition'], tau_name='initial_condition',
                relaxed_constraints=relaxed, S_matrix=np.asarray(S.matrix, dtype=float).tolist(),
                S_row_names=list(S.row_names), S_col_names=list(S.col_names),
                basis_vectors=[str(v) for v in ctx.basis_vectors()],
                basis_scalars=[str(v) for v in ctx.basis_scalars()],
                named_dual_values=duals, constraint_metadata=meta,
                certificate_provenance=dict(solve_id=str(uuid.uuid4()), pep_type='primal',
                    solver_status=problem.status, source_hashes=hashes,
                    solver=dict(api='CVXPrimalSolver.build_problem + cvxpy.Problem.solve',
                                cvxpy_version=cp.__version__, effective_name=problem.solver_stats.solver_name, settings=options)),
                normalization=dict(tau_name='initial_condition', initial_condition='D_h(x_star,x_0)<=R',
                    performance_metric='f(x_N)-f(x_star)', bound_value=float(value), bound_formula='R/(alpha*N)'))
    print('N, bound, solver:', N, value, problem.solver_stats.solver_name)
    for owner in ('f', 'h'):
        print(owner, [(name, round(d, 7)) for name, d in duals.items() if name.startswith(owner + ':') and d is not None and abs(d) > 1e-6])
    print('S max, eigenvalues:', max_abs(S.matrix), np.linalg.eigvalsh(S.matrix))
    return ctx, pb, result, data


def candidate_weights(N, a):
    weights = {'initial_condition': 1/(a*N), f'h:x_star,x_{N}': 1/(a*N)}
    for k in range(1, N+1):
        weights[f'f:x_star,x_{k}'] = 1/N
        weights[f'h:x_{k},x_{k-1}'] = k/(a*N)
        if k >= 2:
            weights[f'f:x_{k-1},x_{k}'] = (k-1)/N
            weights[f'h:x_{k-1},x_{k}'] = (k-1)/(a*N)
    return weights


def verify_certificate(ctx, pb, data, dense_value):
    from pepflow.utils import Comparator
    pm = pf.ExpressionManager(ctx, resolve_parameters=json.loads(data['params_json']))
    basis = ctx.basis_vectors()
    S = np.asarray(data['S_matrix'], dtype=float)
    eig, Q = np.linalg.eigh(S)
    D, E = np.diag(eig), Q.T
    ell = [sum((float(v)*b for v, b in zip(row, basis)), pf.Vector.zero()) for row in E]
    S_numeric = sum((float(eig[i])*ell[i]*ell[i] for i in range(len(eig))), pf.Scalar.zero())
    weighted = pf.Scalar.zero()
    min_dual = 0.0
    entries = entries_of(ctx, pb)
    assert {c.name for c, *_ in entries} == set(data['named_dual_values']) == set(data['constraint_metadata'])
    for c, *_ in entries:
        meta = data['constraint_metadata'][c.name]
        value = data['named_dual_values'][c.name]
        if meta['relaxed']:
            assert value is None
            continue
        assert value is not None
        residual = c.lhs-c.rhs
        if c.cmp in (Comparator.GE, Comparator.SEQ):
            residual = -residual
        weighted += float(value)*residual
        if c.cmp != Comparator.EQ:
            min_dual = min(min_dual, value)
    checked = pm.eval_scalar(pb.performance_metric-data['opt_value']-weighted+S_numeric)
    residuals = dict(identity_gram_max_abs=max_abs(checked.inner_prod_coords),
        identity_func_max_abs=max_abs(checked.func_coords), identity_offset_abs=max_abs(checked.offset),
        S_reconstruction_max_abs=max_abs(E.T@D@E-S), dense_relaxed_gap=abs(dense_value-data['opt_value']),
        minimum_scalar_inequality_dual=min_dual, minimum_S_eigenvalue=float(eig.min()),
        minimum_matrix_inequality_eigenvalue=0.0)
    tolerances = dict(identity_atol=1e-5,identity_rtol=0.0,reconstruction_atol=1e-4,
        reconstruction_rtol=1e-5,dual_tol=1e-6,psd_tol=1e-6,dense_opt_atol=1e-5)
    assert all(residuals[k] <= 1e-5 for k in ('identity_gram_max_abs','identity_func_max_abs','identity_offset_abs'))
    assert np.allclose(E.T@D@E,S,atol=1e-4,rtol=1e-5)
    assert np.allclose(S,S.T,atol=1e-6,rtol=0)
    assert np.all(np.isfinite(S))
    assert min_dual >= -1e-6 and eig.min() >= -1e-6
    assert residuals['dense_relaxed_gap'] < 1e-5
    assert data['certificate_provenance']['solver_status'] == 'optimal'
    data['numerical_decomposition'] = dict(method='direct',factorization='eigendecomposition',D=D.tolist(),ell_coords=E.tolist(),basis_labels=[str(b) for b in basis])
    data['numerical_checks'] = dict(tolerances=tolerances,residuals=residuals,passed=True)
    data['numerical_certificate_verified'] = True
    print('Full coordinate certificate checks:', residuals)
    return checked
