import json
import hashlib
from pathlib import Path
root=Path.cwd()
notebook=root/'pgm_example_lyap.ipynb'
book=json.loads(notebook.read_text())
b4=json.loads((root/'state/pgm_b4.json').read_text())
static=json.loads((root/'supplementary/b5-static-001.json').read_text())
assert all(command['returncode']==0 for command in static['commands'] if command['label'] in ('source_ruff','source_ty'))
for c in book['cells']:
    if c['cell_type']=='code':
        assert c['execution_count'] is not None
        assert all(o['output_type']!='error' for o in c['outputs'])
def output(index):
    return ''.join(''.join(o.get('text',[])) for o in book['cells'][index].get('outputs',[]))
markers={'step':(34,'Step, 1<=k<=N-2: exact identity verified'),'base':(37,'Base V_1<=V_0=0, N>=2: exact identity verified'),'boundary':(40,'Terminal increment, N>=2: exact identity verified'),'normalization':(45,'Radius normalization: exact identity verified')}
proof_checks={name: marker in output(index) for name,(index,marker) in markers.items()}
assert all(proof_checks.values())
assert 'N=1 direct base-terminal identity: exact identity verified' in output(43)
assert 'Domain/sign proof:' in output(45)
proof_checks.update(signs=True,domain=True,small_horizon=True)
for relative,expected in b4['certificate_provenance']['source_hashes'].items():
    assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==expected
read=lambda part:(root/f'supplementary/b5_{part}.py').read_text(encoding='utf-8-sig')
coeff_source=read('coeff_formula').split('k_sym,m_sym,U_sym=')[0]+read('formula_comparison').split('formula_residuals=[]')[0]
local_source='import sympy as sp\n'+read('derivation')[read('derivation').index('def local_coefficients'):read('derivation').index('# Exact coefficient-equation')]
final_structure={'quadratic_convention':'sum_{i,j} C_ij <v_i,v_j>, symmetric C; off-diagonal products counted twice','interior':{'index_domain':'1 <= k < N','basis_labels':b4['basis_templates']['interior'],'quadratic_coefficients':{'0,0':'-L/(4*N)','1,1':'L*(N-k)/(2*N-k)^2','1,2':'-1/(2*(2*N-k))','1,3':'-1/(2*(2*N-k))','2,2':'-T_k/(2*L*(2*N-k)^2)','other_independent_entries':'0'},'T_definition':'(u_k,v_k)^T = M_k ... M_(N-2) (N-1,1)^T; T_k=u_k/v_k; empty product at k=N-1. Explicit M_j given in theorem and executable transfer_matrix.'},'initial':{'index_domain':'k=0','basis_labels':[],'value':'V_0=0'},'terminal':{'index_domain':'k=N','basis_labels':['x_0-x_star'],'quadratic_coefficients':{'0,0':'-L/(4*N)'}},'function_terms':[{'index_domain':'1 <= k < N','expression':'f(x_k)-f_star','coefficient':'(k+1)/(2*N-k)'},{'index_domain':'1 <= k < N','expression':'g(x_k)-g_star','coefficient':'k/(2*N-k)'},{'index_domain':'k=N','expression':'h(x_N)-h_star','coefficient':'1'}],'constant_terms':[]}
formula='V_0=0; for 1<=k<N, V_k=-L||d_0||^2/(4N)+L(N-k)||d_k||^2/(2N-k)^2-<d_k,grad f(x_k)>/(2N-k)-T_k||grad f(x_k)-grad f(x_star)||^2/(2L(2N-k)^2)+(k+1)(f_k-f_star)/(2N-k)+k(g_k-g_star)/(2N-k); V_N=h_N-h_star-L||d_0||^2/(4N). T_k is the explicit finite transfer-matrix product in coeff_code.'
state={**b4,'analytic_full_pep_verified':False,'lyapunov_proof_verified':True,'require_analytic_full_pep':False,'proof_checks':proof_checks,'proof_arguments':{'step':'Symbolic PEPFlow one-step identity in notebook cells 33-34; all Gram/function/offset coordinates vanish with generic symbolic k,N,L,U and the exact transfer recurrence.','base':'Separate N>=2 base context in cells 36-37; no g(x_0) is evaluated.','boundary':'Terminal identity in cells 39-40 uses T_(N-1)=N-1; N=1 checked independently in cells 42-43.','signs':'Nonnegative first transfer row and strictly positive second row imply positive denominators and T>=0; H,D,A,B>0; explicit positive interpolation differences and terminal weights. Cells 3,44-45.','domain':'Real finite-dimensional space, L>0, R>=0, integer N>=1; generic steps 1<=k<=N-2, base N>=2, terminal N>=2; N=1 separate; no division by R.','normalization':'Cell45 verifies gap-LR^2/(4N)=V_N+L/(4N)(||d_0||^2-R^2); V_N<=V_0=0.'},'lyapunov_formula':formula,'discovery_expression_structure':b4['expression_structure'],'expression_structure':final_structure,'coeff_code':coeff_source,'local_multiplier_code':local_source,'coefficient_formula_status':'verified','unresolved_coefficients':[],'proof_notebook':'pgm_example_lyap.ipynb','notebook_sha256':hashlib.sha256(notebook.read_bytes()).hexdigest(),'validation':{'static_evidence':'supplementary/b5-static-001.json','clean_kernel_execution':'supplementary/b5-final-notebook-output.txt','method':'python -I -B entry to nbconvert --to notebook --execute --inplace; pinned isolated kernel','presentation_policy':'evaluation-ancillary-v1','rendering_performed':False,'markdown_source_checks':True},'run_status':'completed','unresolved_work':['Separate analytic global full-PEP matrix formula proof not claimed; not required by this attempt.'],'usage':{'tokens':None,'reason':'Provider usage is not exposed to this worker.'}}
(root/'state/pgm_b5.json').write_text(json.dumps(state,indent=2,allow_nan=False))
items=[
('title, problem description, and the algorithm update equations in LaTeX','0','All assumptions, metric, update and proximal optimality condition in source.'),
('proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','1,2,3','Placeholder replaced with theorem, explicit finite-product potential and self-contained local identities, signs and telescope.'),
('imports','4,5','Approved path and pinned fresh kernel executed.'),
('function/operator definitions','6','Smooth convex f, convex g and composite h exposed.'),
('make_ctx_pgm and get_pep_setup','6','Context construction, actual recursion, squared-radius constraint and metric exposed.'),
('numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','7,8,9','Seven printed values and image/png plot output retained; N6/N7 inaccurate statuses disclosed. No image inspection.'),
('dense and relaxed proof solves','10,11','Both N4 solves retained with active groups, sparse support, objective comparison; N6 additional sample disclosed.'),
('lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','10,11','Complete coherent certificate identity, sign/PSD checks, labeled true S and factor D, reconstruction, and initial candidate search. Separate global analytic status remains false.'),
('partial-sum Lyapunov construction and rank profile','12,13','Visible saved-certificate checker, LDL decomposition, grouping and accumulation loops; ranks at both horizons; all components covered.'),
('special-vector identification','14-21','Visible actual sparse-basis search with outputs, consistent adopted template, endpoint and independence checks.'),
('coefficient extraction and closed-form V_k','22-31','All-index full-expression reconstruction; labeled coefficient and formula-comparison matrices; exact finite-product formula, recurrence derivation and arbitrary-horizon product argument.'),
('symbolic step, base, and boundary identities','32-45','Distinct symbolic PEPFlow contexts: generic step, base, terminal, N1; exact Gram/function/offset residuals; signs, nonzero denominators, and radius normalization.')]
lines=['Notebook: pgm_example_lyap.ipynb','Last reviewed block: B5','SHA-256: '+state['notebook_sha256'],'Presentation policy: evaluation-ancillary-v1. No rendering or image inspection. Verified means source/content, stored mathematical outputs and execution checks under that override. Markdown row breaks, braces, delimiters and control characters audited.','', '| Item | Requirement | Status | Cell indices | Evidence |','|---|---|---|---|---|']
lines += [f'| {i} | {name} | verified | {indices} | {evidence} |' for i,(name,indices,evidence) in enumerate(items,1)]
(root/'supplementary/pgm_example_lyap_checklist.md').write_text('\n'.join(lines))
print('B5 state saved; all required mathematical and notebook gates verified.')
