"""Update the existing notebook with visible B2 constructions and checks."""
from pathlib import Path
import nbformat as nbf

root=Path(__file__).resolve().parents[1]
dest=root/'bppm_example_lyap.ipynb'
nb=nbf.read(dest,as_version=4)
md=nbf.v4.new_markdown_cell
code=nbf.v4.new_code_cell
helper=(root/'supplementary/helpers/certificate_tools.py').read_text()
verify_source=helper[helper.index('def verify_certificate'):helper.index('CERTIFICATE_KEYS')].strip()
cells=[
md(r"""## Full-PEP certificate

We retain one coherent primal-dual certificate from the sparse solve at $N=4$, $\alpha=R=1$. The dense solve and sparse solve are stored separately; all sparse multipliers, the Gram remainder, and the bound originate in the same sparse solve. The frozen numerical tolerances are unchanged.

The dense solution has optimizer comparisons for $f$, forward comparisons among iterates for $f$, and adjacent/forward comparisons for $h$. Its Gram remainder has eigenvalues below $4\cdot10^{-10}$. We test a nearest-neighbor relaxation preserving the optimizer comparisons. CLARABEL defaults are used for both solves.
"""),
code("import hashlib\nimport sympy as sp\nfrom certificate_tools import inventory, scalar_from_gram, certificate_id\n\ndense = json.loads((notebook_dir / 'state/bppm_dense.json').read_text())\nb2 = json.loads((notebook_dir / 'state/bppm_b2.json').read_text())\nassert certificate_id(b2) == b2['certificate_id']\nfor path, expected in b2['certificate_provenance']['source_hashes'].items():\n    assert hashlib.sha256((notebook_dir / path).read_bytes()).hexdigest() == expected\nN = b2['N_verify']\nparams = {key: sp.S(value) for key, value in json.loads(b2['params_json']).items()}\nprint('Dense bound:', dense['opt_value'])\nprint('Dense basis:', dense['basis_vectors'])\nprint('Dense S eigenvalues:', np.linalg.eigvalsh(np.array(dense['S_matrix'])))\nfor owner in ('f', 'h'):\n    active = {name: value for name, value in dense['named_dual_values'].items() if name.startswith(owner + ':') and value is not None and abs(value) > 1e-6}\n    print('Dense active', owner, active)"),
code("keep = {'initial_condition', f'h:x_star,x_{N}'}\nkeep.update(f'f:x_star,x_{i}' for i in range(1, N+1))\nkeep.update(f'f:x_{i},x_{i+1}' for i in range(1, N))\nkeep.update(f'h:x_{i},x_{i-1}' for i in range(1, N+1))\nkeep.update(f'h:x_{i},x_{i+1}' for i in range(1, N))\nrelaxed = [c.name for c, *_ in inventory(ctx, pb) if c.name not in keep]\nassert relaxed == b2['relaxed_constraints']\npb.set_relaxed_constraints(relaxed)\nprint('Dropped constraints:', len(relaxed))\nprint('Sparse bound:', b2['opt_value'])\nprint('Dense/sparse discrepancy:', abs(dense['opt_value'] - b2['opt_value']))\nassert abs(dense['opt_value'] - b2['opt_value']) < 1e-5\nfor name, value in b2['named_dual_values'].items():\n    if value is not None:\n        print(name, value)"),
md(r"""### Initial formula search

Inspecting the sparse values suggests the following candidate multipliers (all omitted terms are zero):
$$\tau=\frac1{\alpha N},\quad
\lambda^f_{\star,i}=\frac1N\ (1\leq i\leq N),\quad
\lambda^f_{i,i+1}=\frac{i}{N}\ (1\leq i<N),$$
$$\lambda^h_{i,i-1}=\frac{i}{\alpha N}\ (1\leq i\leq N),\quad
\lambda^h_{i,i+1}=\frac{i}{\alpha N}\ (1\leq i<N),\quad
\lambda^h_{\star,N}=\frac1{\alpha N},\qquad S_{\rm guess}=0.$$
Here $\lambda^f_{i,j}$ multiplies $f(x_j)-f(x_i)+\langle\nabla f(x_j),x_i-x_j\rangle\leq0$, and similarly for $h$.
These are numerical candidates, not yet an arbitrary-horizon full-PEP proof. No target-specific reference was consulted. The checks below compare all active multipliers, not just the returned $f$ group.
"""),
code("def candidate_multipliers(N, alpha):\n    values = {'initial_condition': 1/(alpha*N), f'h:x_star,x_{N}': 1/(alpha*N)}\n    values.update({f'f:x_star,x_{i}': 1/N for i in range(1, N+1)})\n    values.update({f'f:x_{i},x_{i+1}': i/N for i in range(1, N)})\n    values.update({f'h:x_{i},x_{i-1}': i/(alpha*N) for i in range(1, N+1)})\n    values.update({f'h:x_{i},x_{i+1}': i/(alpha*N) for i in range(1, N)})\n    return values\n\ncandidate = candidate_multipliers(sp.Integer(N), params['alpha'])\nerrors = [abs(float(candidate.get(name, 0)) - value) for name, value in b2['named_dual_values'].items() if value is not None]\nprint('Maximum candidate multiplier error:', max(errors))\nassert max(errors) < 1e-4\nfor owner, groups in b2['all_lambda_groups'].items():\n    for group_name, display in groups.items():\n        labels = display['row_names']\n        columns = display['col_names']\n        matrix = np.array([[candidate.get(f'{owner}:{r},{c}', sp.S.Zero) for c in columns] for r in labels], dtype=object)\n        print('Candidate multipliers:', owner, group_name)\n        pf.pprint_labeled_matrix(pf.MatrixWithNames(matrix, labels, columns))"),
md(r"""### Selected Gram remainder and decomposition

The spectral decomposition below retains every eigenvalue of the selected $S$; no numerical term is discarded. With factor-coordinate rows $E$, $S=E^TDE$ and $S_{\rm numeric}=\sum_{ij}D_{ij}\ell_i\ell_j$. All eigenvalues are nonnegative within the frozen PSD tolerance. The separate zero candidate matches $S$ within $10^{-4}$; it does not replace the saved numerical remainder.
"""),
code("S_array = np.asarray(b2['S_matrix'], dtype=float)\nD = np.asarray(b2['numerical_decomposition']['D'], dtype=float)\nE = np.asarray(b2['numerical_decomposition']['ell_coords'], dtype=float)\nprint('Selected S eigenvalues / diagonal D:', np.diag(D))\nprint('S factor reconstruction error:', np.max(np.abs(E.T @ D @ E - S_array)))\nassert np.allclose(E.T @ D @ E, S_array, atol=1e-4, rtol=1e-5)\nprint('S=0 candidate error:', np.max(np.abs(S_array)))\nassert np.max(np.abs(S_array)) < 1e-4\npf.pprint_labeled_matrix(pf.MatrixWithNames(np.zeros_like(S_array), b2['S_row_names'], b2['S_col_names']))"),
md(r"""### Complete numerical certificate verification

Every inequality residual is oriented as $r_c\leq0$. The checked identity includes the initial-condition constant:
$$[f(x_N)-f(x_\star)]-\mathrm{bound}-\sum_c d_c r_c+S_{\rm numeric}=0.$$
The next cell checks Gram coordinates, function coordinates, offset, dual signs, PSD, decomposition reconstruction, and dense/sparse agreement. All scalar and matrix families must be inventoried; this setup has only scalar interpolation constraints and the Gram PSD constraint.
"""),
code(verify_source),
code("checks, residual = verify_certificate(ctx, pb, params, b2, dense['opt_value'])\nprint('Numerical checks:', checks)\nassert checks['passed']\npf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(residual.inner_prod_coords, dtype=float), b2['basis_vectors'], b2['basis_vectors']))\npf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(residual.func_coords, dtype=float).reshape(1, -1), ['function residual'], b2['basis_scalars']))\nprint('Offset residual:', residual.offset)\nexact_weighted = pf.Scalar.zero()\nfor constraint, *_ in inventory(ctx, pb):\n    coefficient = candidate.get(constraint.name, sp.S.Zero)\n    exact_weighted += coefficient * (pf.Scalar.zero() + constraint.lhs - constraint.rhs)\nexact_diff = pb.performance_metric - params['R']/(params['alpha']*N) - exact_weighted\nexact_coords = pf.ExpressionManager(ctx, resolve_parameters=params).eval_scalar(exact_diff)\nassert all(sp.simplify(v) == 0 for v in np.asarray(exact_coords.inner_prod_coords).flat)\nassert all(sp.simplify(v) == 0 for v in np.asarray(exact_coords.func_coords).flat)\nassert sp.simplify(exact_coords.offset) == 0\nprint('Candidate exact identity at N=4: all coordinates zero. This is a fixed-horizon check.')"),
md("### Block 2 conclusion\n\nThe selected numerical certificate is verified. Candidate formulas match all active groups, and the zero Gram candidate passes an exact fixed-horizon identity check. The initial closed-form search is complete; the arbitrary-horizon identity remains unresolved. Status: `numerical_certificate_verified=True`, `analytic_full_pep_verified=False`, `lyapunov_proof_verified=False`. Blocks 3–5 remain to be done.")]
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Full-PEP certificate'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Lyapunov partial sums'))
nb.cells[start:end]=cells
nbf.write(nb,dest)
print('B2 cells written:',start,'through',start+len(cells)-1)
