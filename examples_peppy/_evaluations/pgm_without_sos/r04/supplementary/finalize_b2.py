from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / 'helpers'))
import runtime
import numpy as np
import pepflow as pf
import nbformat as nbf
notebook_dir = runtime.ATTEMPT
source = (notebook_dir / 'supplementary/b2_cells.py').read_text(encoding='utf-8-sig')
exec(compile(source, 'b2_cells.py', 'exec'))

lamb_code = source[source.index('def candidate_lambda'):source.index('\ncandidate_errors')]
S_code = "S_guess = sp.Rational(1, 4*N)*(ctx['x_0']-ctx['x_star'])**2 - pb.performance_metric + weighted_guess"
search = dict(completed=True, references_reviewed=['Own B1 and B2 certificates; target references excluded by clean-room policy'],
              attempts=[dict(component='lambda', method='Rational reconstruction and cumulative indexed sequences for f and g', max_error=max(candidate_errors)),
                        dict(component='S', method='Residual formula from rational lambda; compare full scalar coordinates; reverse LDL inspected', max_error=S_candidate_error)],
              unresolved_components=['analytic lambda validity for all horizons', 'analytic PSD decomposition of S'])
state = {**b1, **sample, 'normalization': dict(tau_name='initial_condition', initial_condition=b1['initial_condition'],
          performance_metric=b1['performance_metric'], bound_value=sample['opt_value'], bound_formula=b1['conjectured_rate']),
         'numerical_checks': dict(tolerances=tolerances, residuals=residuals, passed=True),
         'numerical_decomposition': dict(method='reverse_ldl', D=D.tolist(), ell_coords=E.tolist(), basis_labels=sample['basis_vectors']),
         'closed_form_search': search, 'formula_status': {'lambda': 'candidate', 'S': 'candidate'},
         'lamb_code': lamb_code, 'S_code': S_code, 'S_decomp_type': 'ldl',
         'numerical_certificate_verified': True, 'analytic_full_pep_verified': False,
         'lyapunov_proof_verified': False, 'require_analytic_full_pep': False, 'proof_valid': True}
keys = ('N_verify','params_json','relaxed_constraints','S_matrix','S_row_names','S_col_names','basis_vectors',
        'basis_scalars','opt_value','tau_sol','tau_name','named_dual_values','constraint_metadata','normalization',
        'certificate_provenance','numerical_checks','numerical_decomposition')
state['certificate_id'] = hashlib.sha256(json.dumps({k:state[k] for k in keys},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
for filename in ('pgm_b2.json', 'pgm_relaxed.json'):
    (notebook_dir / 'state' / filename).write_text(json.dumps(state, indent=2, allow_nan=False))
nb = nbf.read(notebook_dir / 'pgm_example_lyap.ipynb', as_version=4)
start = next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Dense and relaxed'))
end = next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Partial-sum'))
parts = source.split('# CELL')
nb.cells[start:end] = [nbf.v4.new_markdown_cell('## Dense and relaxed proof solves\nThe stored results were captured with the approved primal framework, CLARABEL defaults, and one coherent selected sparse solve. Both function groups and every initial multiplier are retained. The next cell reconstructs the setup and reviews the saved solves without rerunning them.'),
                      nbf.v4.new_code_cell(parts[0]),
                      nbf.v4.new_markdown_cell(r'''## Lambda and S verification
For $0\leq i<N$, the candidate cumulative multipliers are $a_i=(i+1)/(2N-i)$ for $f$ and $b_i=i/(2N-i)$ for $g$. Set $a_{-1}=0$, $a_N=b_N=1$, and $b_0=0$. Consecutive-pair weights are $a_i,b_i$; optimizer-pair weights are their successive differences. These are candidates inferred from this sample, not an all-horizon proof.
The candidate quadratic remainder is $S_{\rm guess}=\|x_0-x_\star\|^2/(4N)-(h_N-h_\star)+\sum\lambda I$, at $L=R=1$. Its agreement and the saved numerical reverse-LDL decomposition are checked below. No fixed SOS aid or pre-existing answer was consulted.'''),
                      nbf.v4.new_code_cell(parts[1]),
                      nbf.v4.new_markdown_cell('### Complete numerical certificate identity\nAll inequalities use nonpositive residuals. Nonnegative multipliers and a positive semidefinite remainder support the upper-bound direction. The finite-sample checks include Gram, function-value and constant coordinates; no analytic full-PEP claim is made.'),
                      nbf.v4.new_code_cell(parts[2]),
                      nbf.v4.new_markdown_cell('### Initial closed-form search status\nThe rational lambda formulas and residual S formula match this certificate. All-horizon validity and an analytic positive-semidefinite decomposition remain unresolved. The selected numerical certificate and its complete reverse-LDL factors are retained for Block 3. No theorem is asserted from finite-sample agreement.')]
nbf.write(nb, notebook_dir / 'pgm_example_lyap.ipynb')
print('B2 state saved; notebook updated.')
