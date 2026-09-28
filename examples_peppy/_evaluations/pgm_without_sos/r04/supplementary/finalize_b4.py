from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import nbformat as nbf
source=(runtime.ATTEMPT/'supplementary/run_b4.py').read_text(encoding='utf-8-sig')
exec(compile(source,'run_b4.py','exec'))
parts=source if False else (notebook_dir/'supplementary/b4_cells.py').read_text(encoding='utf-8-sig').split('# CELL')
basis_code='from pgm_setup import f as setup_f, g as setup_g\n'+parts[4][parts[4].index('def V_k_basis'):parts[4].index('\nfor k in range')]
structure_code='function_sample_coefficients = '+repr(function_sample_coefficients)+'\n'+parts[6][parts[6].index('def V_k_structure'):parts[6].index('\ncomponent_residuals')]
exec(compile(structure_code,'saved_structure_replay','exec'))
for k in range(N_int+1):
    diff=pm.eval_scalar(V_k_structure(k)-lyap[k])
    assert max(float(np.max(np.abs(np.asarray(v,float)),initial=0)) for v in (diff.inner_prod_coords,diff.func_coords,np.asarray(diff.offset)))<=1e-4
unknowns=[dict(name=f'c_{i}{j}',arguments=['k','N','L'],role=f'interior.C[{i},{j}] symmetric',index_domain='1 <= k <= N-1') for i in range(4) for j in range(i,4)]
unknowns += [dict(name=name,arguments=['k','N','L'],role=role,index_domain='1 <= k <= N-1') for name,role in [('a','coefficient of f_k-f_star'),('b','coefficient of g_k-g_star')]]
unknowns += [dict(name=name,arguments=['N','L'],role=role,index_domain='k=N') for name,role in [('t00','terminal.C[0,0]'),('tF','terminal f gap'),('tG','terminal g gap')]]
expression_structure=dict(quadratic_convention='sum_ij C_ij <v_i,v_j>, symmetric C, off-diagonals counted twice',
 interior=dict(index_domain='1 <= k <= N-1',basis_labels=['e_0','e_k','p_k','s_star'],
               definitions='e_k=x_k-x_star; p_k=grad f(x_k)-grad f(x_star); s_star=grad f(x_star)',
               quadratic_coefficients={f'{i},{j}':f'c_{i}{j}(k,N,L)' for i in range(4) for j in range(i,4)}),
 initial=dict(index_domain='k=0',basis_labels=[],quadratic_coefficients={},expression='V_0=0 by construction'),
 terminal=dict(index_domain='k=N',basis_labels=['e_0'],quadratic_coefficients={'0,0':'t00(N,L)'}),
 function_terms=[dict(index_domain='1 <= k <= N-1',expression='f(x_k)-f(x_star)',coefficient='a(k,N,L)'),
                 dict(index_domain='1 <= k <= N-1',expression='g(x_k)-g(x_star)',coefficient='b(k,N,L)'),
                 dict(index_domain='k=N',expression='f(x_N)-f(x_star)',coefficient='tF(N,L)'),
                 dict(index_domain='k=N',expression='g(x_N)-g(x_star)',coefficient='tG(N,L)')],constant_terms=[])
state={**b3,'basis_templates':{'interior':['e_0','e_k','p_k','s_star'],'initial':[],'terminal':['e_0']},
 'basis_code':basis_code,'structure_code':structure_code,'coeff_by_k':{str(k):C.tolist() for k,C in coeff_by_k.items()},
 'coeff_code':None,'coefficient_formula_status':'unresolved','expression_structure':expression_structure,
 'unresolved_coefficients':unknowns,'function_sample_coefficients':function_sample_coefficients,
 'numerical_reconstruction':dict(certificate_id=b3['certificate_id'],required_indices=list(range(N_int+1)),
     quadratic_residuals=coefficient_residuals,component_residuals=component_residuals,
     tolerances=dict(indep_tol=1e-7,span_tol=1e-5,component_atol=1e-4,component_rtol=1e-5),passed=True),
 'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
(notebook_dir/'state/pgm_b4.json').write_text(json.dumps(state,indent=2,allow_nan=False))
print('Coefficient samples:',{k:C.tolist() for k,C in coeff_by_k.items()})
nb_path=notebook_dir/'pgm_example_lyap.ipynb'
nb=nbf.read(nb_path,as_version=4)
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Identify the vectors'))
end=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Symbolic step'))
nb.cells[start:end]=[
 nbf.v4.new_markdown_cell('## Identify the vectors composing the Lyapunov function\nReconstruct the selected Block 3 partial sums and seek interpretable spanning vectors. All endpoint cases remain included.'),
 nbf.v4.new_code_cell(parts[0]),
 nbf.v4.new_markdown_cell('### Candidate-vector scan\nCandidates include initial/current point gaps, gradient differences, the optimizer gradient, all basis vectors and tagged iterates, and pairwise differences. Duplicate coordinates and zero vectors are removed.'),
 nbf.v4.new_code_cell(parts[1]),nbf.v4.new_code_cell(parts[2]),
 nbf.v4.new_markdown_cell('### Selected basis pattern\nRun the sparsity search on the actual column-space candidates at each nonzero-rank index. Then adopt a uniform order using the optimizer gradient explicitly, because it makes the expression consistent across indices.'),
 nbf.v4.new_code_cell(parts[3]),
 nbf.v4.new_markdown_cell(r'''Define $e_k=x_k-x_\star$, $p_k=\nabla f(x_k)-\nabla f(x_\star)$, and $s_\star=\nabla f(x_\star)$. The adopted ordered basis is
$$\mathcal B_k=[e_0,e_k,p_k,s_\star]\quad(1\leq k<N),\qquad \mathcal B_0=[],\quad\mathcal B_N=[e_0].$$
This choice is independently checked below, including the initial and terminal ranks.'''),
 nbf.v4.new_code_cell(parts[4]),
 nbf.v4.new_markdown_cell('### Coefficient matrices\nThe symmetric matrix uses the basis order above; off-diagonal terms occur twice. Function gaps and offsets are checked separately. Coefficient fitting is deferred: c_ij(k,N,L), a(k,N,L), b(k,N,L), and terminal t00(N,L), tF(N,L), tG(N,L) are analytic unknowns.'),
 nbf.v4.new_code_cell(parts[5]),nbf.v4.new_code_cell(parts[6]),
 nbf.v4.new_markdown_cell(r'''### Block 4 conclusion
The full interior structure is
$$V_k=\sum_{i,j=0}^3c_{ij}(k,N,L)\langle (\mathcal B_k)_i,(\mathcal B_k)_j\rangle+a(k,N,L)(f(x_k)-f(x_\star))+b(k,N,L)(g(x_k)-g(x_\star)).$$
At $k=0$, $V_0=0$. At $k=N$, the observed structure is $t_{00}\|e_0\|^2+t_F(f_N-f_\star)+t_G(g_N-g_\star)$. No scalar offset is present. Every component is numerically reconstructed at every selected index. These sample coefficients are not an analytic formula; Block 5 must derive them and prove the exact step, base, boundary and sign conditions.''')]
nbf.write(nb,nb_path)
print('B4 state and notebook saved.')
