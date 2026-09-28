import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
from owned_runtime import configure, ROOT
configure()
import json
import numpy as np
import sympy as sp
import pepflow as pf
from pgm_setup import get_pep_setup

REPO_ROOT=ROOT
certificate=json.loads((ROOT/'supplementary/b2-n06-certificate.json').read_text())
N_int=certificate['N_verify']
params_sp={'L':sp.Integer(1),'R':sp.Integer(1)}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints'])
exec((ROOT/'supplementary/b3_certificate_check.py').read_text(),globals())
D=np.array(certificate['numerical_decomposition']['D'])
E=np.array(certificate['numerical_decomposition']['ell_coords'])
assert np.max(np.abs(D-np.diag(np.diag(D))))<1e-12
piece_matrices=[D[i,i]*np.outer(E[i],E[i]) for i in range(len(D))]
term_matrices={name:np.array(pm.eval_scalar(term).inner_prod_coords,dtype=float) for name,term in interpolation_terms.items()}
assign={name:int(name.split(',')[1][2:])-1 for name in term_matrices}
trials=[]
for delay in (-1,0,1):
    assignment=[]
    for i in range(len(D)):
        pivot=len(D)-1-i
        k=(pivot-3)//2 if pivot>=3 else 0
        assignment.append(max(-1,min(N_int-1,k-1+delay)))
    matrices=[np.zeros_like(S_array)]
    running=np.zeros_like(S_array)
    for k in range(N_int):
        steps={-1,0} if k==0 else {k}
        running=running+sum((M for name,M in term_matrices.items() if assign[name] in steps),np.zeros_like(S_array))
        running=running-sum((M for i,M in enumerate(piece_matrices) if assignment[i] in steps),np.zeros_like(S_array))
        matrices.append(running.copy())
    singular=[np.linalg.svd(M,compute_uv=False).tolist() for M in matrices]
    ranks=[int(np.linalg.matrix_rank(M,tol=1e-4)) for M in matrices]
    trial={'recipe':'reverse_ldl_by_pivot','delay':delay,'rank_profile':ranks,'singular_values':singular,'S_assignment':assignment,'term_assignment':assign}
    trials.append(trial)
    print('delay',delay,'ranks',ranks)
(ROOT/'supplementary/b3-n06-trials.json').write_text(json.dumps(trials,indent=2))
# Verify the complete selected trial's coverage and numerical signs.
selected=trials[1]
S_assignment=selected['S_assignment']
lyap=[pf.Scalar.zero()]
running=pf.Scalar.zero()
for k in range(N_int):
    steps={-1,0} if k==0 else {k}
    increment=sum((term for name,term in interpolation_terms.items() if assign[name] in steps),pf.Scalar.zero())
    for i, matrix in enumerate(piece_matrices):
        if S_assignment[i] in steps:
            increment-=sum((float(matrix[a,b])*basis[a]*basis[b] for a,b in np.ndindex(matrix.shape)),pf.Scalar.zero())
    running+=increment
    lyap.append(running)
coverage=pm.eval_scalar(lyap[-1]-(sum(interpolation_terms.values(),pf.Scalar.zero())-S_scalar))
coverage_residuals={name:float(np.max(np.abs(np.array(values,dtype=float)),initial=0)) for name,values in [('gram',coverage.inner_prod_coords),('function',coverage.func_coords),('offset',coverage.offset)]}
assert max(coverage_residuals.values())<=1e-5
minimum_piece_eigenvalue=min(float(np.linalg.eigvalsh(M).min()) for M in piece_matrices)
assert minimum_piece_eigenvalue>=-1e-6
assert not extra_terms
assert all(v is None or v>=-1e-6 for v in saved_duals.values())
assert len(assign)==len(interpolation_terms)
assert len(S_assignment)==len(piece_matrices)
selected.update(N=N_int,certificate_id=certificate['certificate_id'],recipe_id='reverse_ldl_pivot_delay_0',
    rank_convention={'tolerance':1e-4,'scaling':'absolute, unscaled original Gram coordinates','coordinate_order':'setup chronological basis'},
    rank_credible=True,certificate_checked=True,grouping_checked=True,coverage_residuals=coverage_residuals,
    minimum_piece_eigenvalue=minimum_piece_eigenvalue,boundary_exclusions={'left':1,'right':1},
    sign_convention='increments are sums of nonpositive interpolation residuals with nonnegative weights minus PSD pieces',
    boundary_constraints=[],boundary_S=[],omitted_constraints=[],
    certificate_path='supplementary/b2-n06-certificate.json',source_path='supplementary/explore_b3_n06.py')
(ROOT/'supplementary/b3-n06-observation.json').write_text(json.dumps(selected,indent=2))
print('Selected coverage',coverage_residuals,'minimum piece eigenvalue',minimum_piece_eigenvalue)

