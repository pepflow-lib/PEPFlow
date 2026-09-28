# Initial closed-form guesses derived from the selected nonzero pattern.
from fractions import Fraction
candidate = {'initial_condition': 4/N**2}
for k in range(1,N):
    candidate[f'A monotone:x_{k},x_{k+1}'] = 4*k*(k+1)/N**2
candidate[f'A monotone:x_{N},x_star'] = 4/N
candidate['A Lipschitz:x_1,x_1/2'] = 2/N**2
for k in range(1,N):
    candidate[f'A Lipschitz:x_{k}+1/2,x_{k+1}'] = 2*(k+1)**2/N**2
lambda_error = max(abs(selected['named_dual_values'][name]-v) for name,v in candidate.items())
S_guess = (2/N*(ctx['x_0']-ctx['x_star'])-op(ctx[f'x_{N}']))**2
S_guess_eval = pm.eval_scalar(S_guess)
S_guess_error = max_abs(S_guess_eval.inner_prod_coords-S_array)
for name,v in selected['named_dual_values'].items():
    if v is not None:
        print(name, v, 'rational inspection:', Fraction(v).limit_denominator(1000))
print('Candidate comparison errors:',lambda_error,S_guess_error)
print('Atol=1e-4 matches:',lambda_error<=1e-4,S_guess_error<=1e-4)
print('Analytic full-PEP proof: unresolved. Numerical certificate: verified.')
pf.pprint_labeled_matrix(pf.MatrixWithNames(np.asarray(S_guess_eval.inner_prod_coords),selected['basis_vectors'],selected['basis_vectors']))
