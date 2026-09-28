"""Insert visible certificate construction/checks and execute the B2 notebook."""
from pathlib import Path
import hashlib
import json
import os

import nbformat as nbf
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'supplementary' / '.runtime'
for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
for variable in ('TEMP', 'TMP', 'IPYTHONDIR', 'MPLCONFIGDIR', 'JUPYTER_RUNTIME_DIR', 'JUPYTER_CONFIG_DIR'):
    folder = RUNTIME / variable.lower()
    folder.mkdir(parents=True, exist_ok=True)
    os.environ[variable] = str(folder)
os.environ['JUPYTER_PATH'] = str(RUNTIME / 'jupyter')
notebook = ROOT / 'pgm_example_lyap.ipynb'
nb = nbf.read(notebook, as_version=4)
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [md(r"""## Full-PEP certificate

At $N=4$, both interpolation families enter the primal PEP. The dense certificate is preserved in `state/pgm_dense.json`. We tested a sparse pattern retaining only $(x_\star,x_i)$ and $(x_i,x_{i+1})$ inequalities, retaining the initial constraint. Each selected multiplier and the PSD slack come from the same CLARABEL solve. The following checks reconstruct the context without solving again.
"""), code("""import hashlib
import sympy as sp

b1 = json.loads((notebook_dir / 'state' / 'pgm_b1.json').read_text())
dense = json.loads((notebook_dir / 'state' / 'pgm_dense.json').read_text())
selected = json.loads((notebook_dir / 'supplementary' / 'b2-sparse-candidate.json').read_text())
N_int = selected['N_verify']
N = sp.S(N_int)
ctx, pb, obj = get_pep_setup(N_int, {'L': 1, 'R': 1})
entries = [(c, 'initial', None, None) for c in pb.init_conditions]
for owner in ctx.func_to_triplets:
    owner.get_interpolation_constraints(ctx)
    groups = ctx.get_constraint_data(owner)
    entries.extend((c, 'interpolation', str(owner), str(group))
                   for group, constraints in groups.sc_dict.items() for c in constraints)
assert {c.name for c, *_ in entries} == set(selected['constraint_metadata'])
assert selected['basis_vectors'] == [str(v) for v in ctx.basis_vectors()]
assert selected['basis_scalars'] == [str(v) for v in ctx.basis_scalars()]
relaxed = []
for c, origin, *_ in entries:
    if origin == 'initial':
        continue
    left, right = c.name.split(':')[1].split(',')
    keep = left == 'x_star'
    if left != 'x_star' and right != 'x_star':
        keep = int(right.split('_')[1]) == int(left.split('_')[1]) + 1
    if not keep:
        relaxed.append(c.name)
assert relaxed == selected['relaxed_constraints']
pb.set_relaxed_constraints(relaxed)
pm = pf.ExpressionManager(ctx, resolve_parameters={'L': sp.S(1), 'R': sp.S(1)})
S_array = np.asarray(selected['S_matrix'], dtype=float)
basis = ctx.basis_vectors()
print('Dense optimum:', dense['opt_value'])
print('Sparse optimum:', selected['opt_value'])
print('Dense/sparse difference:', abs(dense['opt_value'] - selected['opt_value']))
print('Basis:', selected['basis_vectors'])
for sample_name, sample in [('dense', dense), ('sparse', selected)]:
    for owner_name in ('f', 'g'):
        active = [(name, value) for name, value in sample['named_dual_values'].items()
                  if name.startswith(owner_name + ':') and value is not None and value > 1e-6]
        print(sample_name, owner_name, 'active multipliers:', len(active))
    eig = np.linalg.eigvalsh(np.asarray(sample['S_matrix']))
    print(sample_name, 'S rank at 1e-4:', np.sum(np.abs(eig) > 1e-4), 'eigenvalues:', eig)
"""), md(r"""### Initial multiplier formula search

Rationalizing the sparse entries suggests consecutive multipliers
$$\lambda^f_{i,i+1}=\frac{i+1}{2N-i}\quad(0\leq i<N),\qquad
\lambda^g_{i,i+1}=\frac{i}{2N-i}\quad(1\leq i<N).$$
Conservation of function-value coefficients then gives the minimizer multipliers as consecutive differences, with a final coefficient closing the sum to one. We compare every active coefficient, including the initial multiplier $L/(4N)$. These are candidates, not an all-horizon proof.
"""), code("""def candidate_multiplier(name, horizon):
    horizon = sp.S(horizon)
    if name == 'initial_condition':
        return sp.S(1)/(4*horizon)
    owner, pair = name.split(':')
    left, right = pair.split(',')
    if left == 'x_star':
        j = int(right.split('_')[1])
        if j == horizon:
            return sp.S(1 if owner == 'f' else 2)/(horizon+1)
        return (2*horizon + (1 if owner == 'f' else 0))/((2*horizon-j)*(2*horizon+1-j))
    if right == 'x_star':
        return sp.S(0)
    i, j = int(left.split('_')[1]), int(right.split('_')[1])
    return (i + (1 if owner == 'f' else 0))/(2*horizon-i) if j == i+1 else sp.S(0)

lambda_errors = []
for name, value in selected['named_dual_values'].items():
    candidate = candidate_multiplier(name, N)
    if value is not None:
        error = abs(float(candidate)-value)
        lambda_errors.append(error)
        print(name, 'numerical=', round(value, 9), 'candidate=', candidate)
    else:
        assert candidate == 0
print('Maximum multiplier comparison error:', max(lambda_errors))
assert max(lambda_errors) < 1e-4
for owner_name, indices in [('f', ['star', *range(N_int+1)]), ('g', ['star', *range(1, N_int+1)])]:
    labels = [f'x_{i}' for i in indices]
    candidate_matrix = sp.Matrix([[0 if a == b else candidate_multiplier(f'{owner_name}:{a},{b}', N)
                                  for b in labels] for a in labels])
    pf.pprint_labeled_matrix(np.asarray(candidate_matrix, dtype=object), labels, labels)
"""), md(r"""### Supplied SOS candidate and normalization

The three square families below are the **supplied assistance**. They are tested against this attempt's selected certificate. Here $a_i=\nabla f(x_i)$ and $s_i=L(x_{i-1}-x_i)-a_{i-1}\in\partial g(x_i)$. The certificate is normalized as
$$h(x_N)-h(x_\star)-\mathrm{opt}-\sum_c d_c R_c+S=0,$$
where every $R_c\leq0$. The candidate uses normalization factor 1. All its coefficients are nonnegative for $L>0$, $N\geq1$, $1\leq i\leq N$: denominators are positive and numerators are sums of nonnegative terms. Numerical agreement here does not establish the complete identity for arbitrary $N$.
"""), code("""S_candidate = pf.Scalar.zero()
square_vectors, square_coefficients, pieces = [], [], []
for ii in range(1, N_int+1):
    i = sp.S(ii)
    a = f.grad(ctx[f'x_{ii}'])
    ap = f.grad(ctx[f'x_{ii-1}'])
    ast = f.grad(ctx['x_star'])
    s = g.grad(ctx[f'x_{ii}'])
    c1 = N / ((2*N+1-i)*(2*N-i)*L)
    u1 = i/(2*N)*a + (2*N-i)/(2*N)*ap - ast
    c2 = ((i-1)/(2*N-i)*(2*N+2)/(2*N+1) + 2*N/((2*N-i)**2*(2*N+1)))/(2*L)
    u2 = ap+s-L/(2*N+1-i)*(ctx[f'x_{ii-1}']-ctx['x_star'])
    c3 = i/(2*N+1-i)*(2*N)/(2*N+1)/(2*L)
    u3 = (2*N+1)/(2*N)*(a+s)-(ap+s)/(2*N)-L/(2*N-i)*(ctx[f'x_{ii}']-ctx['x_star'])
    piece = c1*u1**2 + c2*u2**2 + c3*u3**2
    S_candidate += piece
    pieces.append(piece)
    square_vectors.extend([u1, u2, u3])
    square_coefficients.extend([c1, c2, c3])
E = np.asarray([pm.eval_vector(v).coords for v in square_vectors], dtype=float)
D = np.diag([float(c.get_value({'L': sp.S(1)})) for c in square_coefficients])
candidate_eval = pm.eval_scalar(S_candidate)
S_reconstructed = E.T @ D @ E
def max_abs(values):
    return float(np.max(np.abs(np.asarray(values, dtype=float)), initial=0.0))
print('Supplied SOS reconstruction residual:', max_abs(S_reconstructed - S_array))
assert np.allclose(S_reconstructed, S_array, atol=1e-4, rtol=1e-5)
assert max_abs(candidate_eval.func_coords) == 0 and max_abs(candidate_eval.offset) == 0
pf.pprint_labeled_matrix(S_reconstructed, selected['basis_vectors'], selected['basis_vectors'])
"""), md("### Complete fixed-horizon certificate verification\nThe saved multipliers and slack are checked in all coordinates, with no active interpolation family omitted. The supplied SOS is also checked as a decomposition of this same slack within the frozen tolerances."), code("""weighted = pf.Scalar.zero()
exact_weighted = pf.Scalar.zero()
inequality_duals = []
for c, *_ in entries:
    value = selected['named_dual_values'][c.name]
    residual = c.lhs-c.rhs
    if c.cmp in (pf.Comparator.GE, pf.Comparator.SEQ):
        residual = -residual
    meta = selected['constraint_metadata'][c.name]
    assert meta['comparator'] == c.cmp.value and meta['kind'] == 'scalar'
    if meta['relaxed']:
        assert value is None
        continue
    assert value is not None
    weighted += value * residual
    exact_weighted += candidate_multiplier(c.name, N)*residual
    if c.cmp != pf.Comparator.EQ:
        inequality_duals.append(value)
S_saved = sum((float(S_array[i,j])*basis[i]*basis[j] for i,j in np.ndindex(S_array.shape)), pf.Scalar.zero())
assert pb.performance_metric is not None
checked = pm.eval_scalar(pb.performance_metric-selected['opt_value']-weighted+S_saved)
candidate_checked = pm.eval_scalar(pb.performance_metric-selected['opt_value']-weighted+S_candidate)
exact_checked = pm.eval_scalar(pb.performance_metric-sp.S(1)/(4*N)-exact_weighted+S_candidate, sympy_mode=True)
exact_fixed_horizon = all(sp.simplify(v) == 0 for values in
                         (exact_checked.inner_prod_coords, exact_checked.func_coords, [exact_checked.offset])
                         for v in np.asarray(values, dtype=object).flat)
residuals = dict(identity_gram_max_abs=max_abs(checked.inner_prod_coords),
    identity_func_max_abs=max_abs(checked.func_coords), identity_offset_abs=max_abs(checked.offset),
    S_reconstruction_max_abs=max_abs(S_reconstructed-S_array),
    candidate_identity_gram_max_abs=max_abs(candidate_checked.inner_prod_coords),
    dense_relaxed_gap=abs(dense['opt_value']-selected['opt_value']),
    conjecture_gap=abs(selected['opt_value']-1/(4*N_int)),
    minimum_scalar_inequality_dual=min(inequality_duals),
    minimum_S_eigenvalue=float(np.linalg.eigvalsh(S_array).min()),
    minimum_matrix_inequality_eigenvalue=0.0)
tolerances = json.loads((repo_root / 'settings.json').read_text())['tolerances']
assert selected['certificate_provenance']['solver_status'] == 'optimal'
assert np.all(np.isfinite(S_array)) and np.allclose(S_array, S_array.T, atol=1e-6, rtol=0)
assert all(residuals[k] <= 1e-5 for k in ('identity_gram_max_abs', 'identity_func_max_abs', 'identity_offset_abs', 'candidate_identity_gram_max_abs'))
assert np.allclose(S_reconstructed, S_array, atol=1e-4, rtol=1e-5)
assert residuals['dense_relaxed_gap'] < 1e-5 and residuals['conjecture_gap'] < 1e-5
assert residuals['minimum_scalar_inequality_dual'] >= -1e-6
assert residuals['minimum_S_eigenvalue'] >= -1e-6
assert exact_fixed_horizon
print('Numerical certificate verified:', True)
print('Residuals:', residuals)
print('Exact candidate identity at N=4:', exact_fixed_horizon)
print('Analytic full-PEP proof for arbitrary N:', False)
pf.pprint_labeled_matrix(np.asarray(checked.inner_prod_coords), selected['basis_vectors'], selected['basis_vectors'])
"""), md("### Block 2 conclusion\nThe complete selected numerical certificate and supplied direct SOS decomposition pass the frozen checks. Rationalized multipliers and the supplied SOS also satisfy the exact fixed-horizon identity. This does not yet prove their arbitrary-horizon validity. Global lambda and S formulas are candidates; numerical Lyapunov discovery may proceed. No local Lyapunov theorem is claimed yet."), code("""source_paths = [notebook_dir / 'pgm_setup.py', notebook_dir / 'supplementary' / 'helpers' / 'certificates.py']
approved_list = json.loads((repo_root / 'allowlist.json').read_text())['exact_read_files']
source_paths.extend(Path(p) for p in approved_list if Path(p).parent == repo_root / 'pepflow')
source_hashes = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths}
assert selected['certificate_provenance']['source_hashes'] == source_hashes
selected.update(b1)
selected.update(N=N_int, N_verify=N_int, numerical_certificate_verified=True,
                analytic_full_pep_verified=False, lyapunov_proof_verified=False, proof_valid=True,
                require_analytic_full_pep=False)
selected['normalization'] = dict(tau_name='initial_condition', initial_condition=b1['initial_condition'],
    performance_metric=b1['performance_metric'], bound_value=selected['opt_value'],
    bound_formula=b1['conjectured_rate'], supplied_sos_scale=1)
selected['numerical_checks'] = dict(tolerances=tolerances, residuals=residuals, passed=True,
                                   exact_candidate_fixed_horizon=bool(exact_fixed_horizon))
selected['numerical_decomposition'] = dict(method='direct', D=D.tolist(), ell_coords=E.tolist(),
    basis_labels=selected['basis_vectors'], supplied_assistance=True,
    pieces=[np.asarray(pm.eval_scalar(piece).inner_prod_coords, dtype=float).tolist() for piece in pieces])
selected['S_decomp_type'] = 'direct'
selected['formula_status'] = {'lambda': 'candidate', 'S': 'candidate'}
selected['closed_form_search'] = dict(completed=True, references_reviewed=['approved/input.md: supplied fixed SOS'],
    attempts=['Sparse consecutive/star pattern preserves dense bound',
              'Rationalized consecutive multipliers; star coefficients derived by function-value conservation',
              'Supplied SOS compared to same numerical slack with scale 1',
              'Exact candidate full-coordinate identity verified at N=4'],
    unresolved_components=['arbitrary-horizon analytic full-PEP identity'],
    multiplier_max_error=max(lambda_errors), S_max_error=residuals['S_reconstruction_max_abs'])
lambda_labels = ['x_star', *[f'x_{i}' for i in range(N_int+1)]]
selected['lambda_row_names'] = lambda_labels
selected['lambda_col_names'] = lambda_labels
selected['lambda_matrix'] = [[selected['named_dual_values'].get(f'f:{a},{b}') or 0.0
                              for b in lambda_labels] for a in lambda_labels]
print('Ready to serialize coherent B2 certificate.')
""")]
nb.cells = nb.cells[:9] + cells + nb.cells[-3:]
# Save exact executed source for replay without hidden proof logic.
lambda_source = next(c.source for c in cells if c.cell_type == 'code' and c.source.startswith('def candidate_multiplier'))
sos_source = next(c.source for c in cells if c.cell_type == 'code' and c.source.startswith('S_candidate ='))
check_source = next(c.source for c in cells if c.cell_type == 'code' and c.source.startswith('weighted ='))
serialize = code("""selected['lamb_code'] = LAMB_SOURCE
selected['S_code'] = SOS_SOURCE
selected['certificate_check_code'] = CHECK_SOURCE
certificate_keys = ('N_verify', 'params_json', 'relaxed_constraints', 'S_matrix', 'S_row_names',
    'S_col_names', 'basis_vectors', 'basis_scalars', 'opt_value', 'tau_sol', 'tau_name',
    'named_dual_values', 'constraint_metadata', 'normalization', 'certificate_provenance',
    'numerical_checks', 'numerical_decomposition')
selected['certificate_id'] = hashlib.sha256(json.dumps({key: selected[key] for key in certificate_keys},
    sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
for filename in ('pgm_relaxed.json', 'pgm_b2.json'):
    (notebook_dir / 'state' / filename).write_text(json.dumps(selected, indent=2, allow_nan=False))
print('Saved certificate ID:', selected['certificate_id'])
""".replace('LAMB_SOURCE', repr(lambda_source)).replace('SOS_SOURCE', repr(sos_source)).replace('CHECK_SOURCE', repr(check_source)))
nb.cells.insert(-3, serialize)
nbf.write(nb, notebook)
NotebookClient(nb, timeout=120, kernel_name='attempt-pgm', resources={'metadata': {'path': str(ROOT)}}).execute()
nbf.write(nb, notebook)
print('B2 notebook executed and state saved.')
for cell in nb.cells:
    if cell.cell_type == 'markdown':
        assert '\\(' not in cell.source and '\\[' not in cell.source
        assert not any(ord(c) < 32 and c not in '\n\t' for c in cell.source)
checklist = ROOT / 'supplementary' / 'pgm_example_lyap_checklist.md'
lines = checklist.read_text(encoding='utf-8').splitlines()
for index, line in enumerate(lines):
    if line.startswith('Last reviewed block:'):
        lines[index] = 'Last reviewed block: B2'
    elif line.startswith('SHA-256:'):
        lines[index] = 'SHA-256: ' + hashlib.sha256(notebook.read_bytes()).hexdigest()
    elif line.startswith('| 7 |'):
        lines[index] = line.replace('| pending |  | Pending owning block. |', '| verified | 9,10 | Dense and sparse saved solve evidence, complete group summaries and preserved optimum printed. |')
    elif line.startswith('| 8 |'):
        lines[index] = line.replace('| pending |  | Pending owning block. |', '| verified | 11-20 | Visible candidates, supplied SOS, full-coordinate numerical checks and exact N=4 candidate check executed; global analytic status remains false. |')
checklist.write_text('\n'.join(lines), encoding='utf-8')
