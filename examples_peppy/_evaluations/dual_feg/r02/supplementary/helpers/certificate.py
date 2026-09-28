"""Capture the complete selected primal certificate without replacing framework APIs."""
import hashlib
import uuid
import numpy as np
import pepflow as pf
from pepflow.lyapunov_utils import ldl_decompose_with_reversed_basis
from runtime import NOTEBOOK_DIR, REPO_ROOT, solve_setup


def capture(ctx, pb, obj, params):
    files = [NOTEBOOK_DIR / 'dual_feg_setup.py', NOTEBOOK_DIR / 'supplementary/helpers/runtime.py',
             NOTEBOOK_DIR / 'supplementary/helpers/certificate.py']
    import json
    allowed = json.loads((REPO_ROOT / 'allowlist.json').read_text())['exact_read_files']
    files += [__import__('pathlib').Path(p) for p in allowed if '/pepflow/' in p.replace('\\', '/') and p.endswith('.py')]
    hashes = {str(p.relative_to(NOTEBOOK_DIR)).replace('\\','/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    result, operational = solve_setup(ctx, pb, obj, params)
    S = result.get_gram_dual_matrix()
    groups = ctx.get_constraint_data(obj)
    entries = [(c, 'initial', None, None) for c in pb.init_conditions]
    entries += [(c, 'interpolation', str(obj), str(group)) for group, constraints in groups.sc_dict.items() for c in constraints]
    assert not groups.psd_dict
    meta, duals = {}, {}
    for c, origin, owner, group in entries:
        dropped = c.name in pb.relaxed_constraints
        v = result.get_dual_value(c.name)
        assert dropped or v is not None
        assert dropped or np.isfinite(float(v))
        meta[c.name] = dict(origin=origin, owner=owner, group=group, kind='scalar', comparator=c.cmp.value, shape=[], relaxed=dropped)
        duals[c.name] = None if dropped else float(v)
    basis = ctx.basis_vectors()
    pm = pf.ExpressionManager(ctx, resolve_parameters=params)
    D, ell = ldl_decompose_with_reversed_basis(S, basis, print_output=False)
    E = np.asarray([pm.eval_vector(v).coords for v in ell], dtype=float)
    lambdas = result.get_scalar_constraint_dual_value_in_numpy(obj)
    assert isinstance(lambdas, dict)
    data = dict(N=int(len([v for v in ctx.vectors if 'x_0' in v.tags])) , opt_value=float(result.opt_value),
        tau_sol=float(result.get_dual_value('initial_condition')), tau_name='initial_condition',
        S_matrix=np.asarray(S.matrix,dtype=float).tolist(), S_row_names=S.row_names, S_col_names=S.col_names,
        basis_vectors=[str(v) for v in basis], basis_scalars=[str(v) for v in ctx.basis_scalars()],
        named_dual_values=duals, constraint_metadata=meta, relaxed_constraints=list(pb.relaxed_constraints),
        numerical_decomposition=dict(method='reverse_ldl', D=np.asarray(D).tolist(), ell_coords=E.tolist(), basis_labels=[str(v) for v in basis]),
        lambda_groups={name:dict(matrix=np.asarray(m.matrix).tolist(),row_names=m.row_names,col_names=m.col_names) for name,m in lambdas.items()},
        certificate_provenance=dict(solve_id=str(uuid.uuid4()), pep_type='primal', solver_status=result.solver_status,
                                    source_hashes=hashes, solver=operational))
    for p in files:
        assert hashes[str(p.relative_to(NOTEBOOK_DIR)).replace('\\','/')] == hashlib.sha256(p.read_bytes()).hexdigest()
    return data
