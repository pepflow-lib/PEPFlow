import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'dual_feg_example_lyap.ipynb'
nb=json.loads(path.read_text(encoding='utf-8'))
source=lambda c: ''.join(c['source'])
texts=lambda c: ''.join(''.join(o.get('text',[])) for o in c.get('outputs',[]) if o['output_type']=='stream')
assert all(c.get('execution_count') is not None for c in nb['cells'] if c['cell_type']=='code')
assert not any(o['output_type']=='error' for c in nb['cells'] for o in c.get('outputs',[]))
assert any('image/png' in o.get('data',{}) for o in nb['cells'][9]['outputs'])
for c in nb['cells']:
    if c['cell_type']=='markdown':
        assert '\\(' not in source(c) and '\\[' not in source(c)
        assert not any(ord(x)<32 and x not in '\n\t' for x in source(c))
expected={38:['Interior step (t>=2)','General-L coefficient representation'],41:['Initial V0=0','Base first step (N>=2)'],44:['Last-step identity (N>=2)'],47:['Rate and initial-radius normalization'],50:['N=1 direct terminal potential']}
for index,names in expected.items():
    output=texts(nb['cells'][index])
    for name in names:
        assert name+' function residual: Matrix(0, 0, []) offset residual: 0 exact zero: True' in output
    assert any('text/latex' in o.get('data',{}) for o in nb['cells'][index]['outputs'])
final_text=texts(nb['cells'][50])
checks=ast.literal_eval(final_text.split('Exact proof obligations: ',1)[1].strip())
assert all(checks.values())
assert 'sparse basis:' in texts(nb['cells'][26]) and 'zero coefficients:' in texts(nb['cells'][26])
assert 'Full-expression reconstruction passed at all indices' in texts(nb['cells'][32])
assert 'Dense objective:' in texts(nb['cells'][11])
assert 'Selected numerical S:' in texts(nb['cells'][14])
assert 'rank V_6: 2' in texts(nb['cells'][19])
assert 'Horizon 4' in texts(nb['cells'][20]) and 'Horizon 6' in texts(nb['cells'][20])
static=json.loads((root/'supplementary/b5-static-003.json').read_text())
assert static['status']=='passed'
b4=json.loads((root/'state/dual_feg_b4.json').read_text())
formula='V_0=0; for 1<=k<N and t=N-k, V_k=-4<G,z_k>-2||z_k||^2+(4L/t)<G+z_k,x_k-x_N>+(4L/N)<G,x_N-x_0>; V_N=2||G||^2+(4L/N)<G,x_N-x_0>, G=A(x_N).'
structure={**b4['expression_structure']}
structure['interior']={**structure['interior'],'coefficients':{'C00':'0','C01':'-2','C02':'2*L/(N-k)','C03':'-2*L*k/(N*(N-k))','C11':'-2','C12':'2*L/(N-k)','C13':'-2*L/(N-k)','C22':'0','C23':'0','C33':'0'},'status':'verified exactly for L>0, integers N>=2, 1<=k<N'}
structure['terminal']={**structure['terminal'],'coefficients':{'C00':'2','C01':'2*L/N','C11':'0'},'status':'verified exactly for L>0, integers N>=1; N=1 direct identity checked'}
coefficient_code='''def analytic_coefficients(k,N,L):
    if k == 0:
        return sp.zeros(0,0)
    if k == N:
        return sp.Matrix([[2,2*L/N],[2*L/N,0]])
    t=N-k
    return sp.Matrix([[0,-2,2*L/t,-2*L*k/(N*t)],[-2,-2,2*L/t,-2*L/t],[2*L/t,2*L/t,0,0],[-2*L*k/(N*t),-2*L/t,0,0]])
'''
proof_arguments={'step':'Substitution of the exact recurrence gives 2/t^2 Lip(x_k,y_k)+4L/[t(t-1)] Mon(x_N,y_k), for t=N-k>=2; local multipliers solved from every symbolic coefficient.',
'base':'V0=Phi(N,x0,0)=0. Separate N>=2 first-step identity and N=1 direct VN=2 Lip(x0,x1) identity verified exactly.',
'boundary':'VN-V_(N-1)=2 Lip(x_(N-1),xN). Rate residual equals VN+(4L/N) Mon(xN,xstar)-||(2L/N)(x0-xstar)-G||^2+(4L^2/N^2)(||x0-xstar||^2-R^2).',
'signs':'All residuals Lip and Mon are nonpositive. For t>=2, L>0, N>=1 every displayed multiplier is positive; the squared norm is nonnegative and subtracted. Hence VN<=V0=0 and the rate residual is <=0.',
'domain':'All finite-dimensional real Euclidean spaces; L>0, R>=0, integer N>=1. No division by R. Interior t>=2; final and N=1 identities use no t-1 denominator.',
'normalization':'The exact boundary identity contains 4*L^2*R^2/N^2 and the initial residual ||x0-xstar||^2-R^2, including all offset components.'}
state={**b4,'coefficient_formula_status':'verified','proof_checks':checks,'proof_arguments':proof_arguments,'lyapunov_formula':formula,
'discovery_expression_structure':b4['expression_structure'],'expression_structure':structure,'coeff_code':coefficient_code,
'local_multiplier_code':'def local_multipliers(t,L):\n    return {"Lipschitz": 2/t**2, "monotone": 4*L/(t*(t-1))}\n',
'remaining_unknowns':[],'unresolved_coefficients':[],'lyapunov_proof_verified':True,'analytic_full_pep_verified':False,
'analytic_full_pep_status':'Separate global lambda/S proof not claimed; the complete local Lyapunov theorem is verified.',
'final_theorem':'||A(x_N)||^2 <= 4*L^2*R^2/N^2',
'symbolic_verification_code':{name:(root/'supplementary'/name).read_text(encoding='utf-8') for name in ('b5_definitions.py','b5_step.py','b5_base.py','b5_terminal.py','b5_boundary.py','b5_small_domain.py')},
'notebook_path':path.name,'notebook_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
'presentation_policy':'evaluation-ancillary-v1','rendered_review':'not performed under evaluation override',
'run_status':'completed','required_unresolved_work':[],'completed_utc':datetime.now(timezone.utc).isoformat()}
(root/'state/dual_feg_b5.json').write_text(json.dumps(state,indent=2,allow_nan=False),encoding='utf-8')
items=['title, problem description, and the algorithm update equations in LaTeX','proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','imports','function/operator definitions','make_ctx_dual_feg and get_pep_setup','numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','dense and relaxed proof solves','lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','partial-sum Lyapunov construction and rank profile','special-vector identification','coefficient extraction and closed-form V_k','symbolic step, base, and boundary identities']
indices=['0','1–3','4–5','6','7','8–9','10–11','12–14','15–20','21–28','29–35, 38','36–50']
evidence=['Assumptions, all three updates, metric and horizon explicitly present.','Separate theorem/outline; full closed form and all residual identities with signs and radius normalization.','Approved source origin asserted; fresh kernel passed.','LipschitzMonotoneOperator and symbolic parameters visible.','Actual recursion, tags, initial radius squared and terminal residual visible.','Seven printed values, statuses and PNG comparison plot; N=1 status retained.','Dense, threshold and structural sparse summaries; preserved optimum.','Complete numerical Gram/function/offset check; true S, factors and candidates labeled; global analytic status distinct.','Visible accumulation and step assignments; rank 4 confirmed at N=4,6; coverage and sign checks.','Visible candidate filtering and actual sparse search per k; clear adopted pattern and independence.','All-index numerical matrices and components; final general-L expression and exact representation check.','Executed symbolic step/base/final/boundary/N=1; zero Gram/function/offset residuals; signs and domains established.']
lines=[f'Notebook: {path.name}', 'Last reviewed block: B5', 'SHA-256: '+state['notebook_sha256'], 'Presentation: evaluation-ancillary-v1. No browser, rendering, or image inspection. Required code execution and source-math checks passed; PNG presence verified only.', '', '| Item | Status | Cells (zero-based) | Evidence |','|---|---|---|---|']
for i,(item,ix,ev) in enumerate(zip(items,indices,evidence),1):
    lines.append(f'| {i}. {item} | verified | {ix} | {ev} |')
(root/'supplementary/dual_feg_example_lyap_checklist.md').write_text('\n'.join(lines),encoding='utf-8')
audit={'run_status':'completed','current_block':'B5','completion_status':'complete','next_block':None,'entry_exit_reason':'Exact proof and final delivery gates passed','notebook_sha256':state['notebook_sha256'],'static_evidence':'supplementary/b5-static-003.json','clean_execution':'supplementary/b5-final-nbconvert-output-002.txt','exact_checks':checks,'all_twelve_items_verified':True,'presentation_policy':'evaluation-ancillary-v1','rendered_review_performed':False,'required_unresolved_work':[],'separate_global_analytic_full_pep':'not claimed; not required for completed local proof','access_control':'instruction_only','access_status':'no_prohibited_exposure_observed','audit_limit':'No exhaustive OS read tracing. Declaration and per-command/adapter evidence do not certify all process reads or training knowledge.','prohibited_sources_used_or_encountered':False,'source_records':['preflight-access-001.json','b1-handoff-access.json','b2-handoff-access.json','b3-revisit-b2-handoff.json','b2-N4-handoff-access.json','b3-handoff-access.json','b4-handoff-access.json'],'B5_consulted_sources':['approved/plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md','approved/pepflow/expression_manager.py','own B4 state, prior notebook and B5 generated scripts'],'B5_commands':['Pinned Python -I -B supplementary/b5_run.py','Pinned Python -I -B supplementary/b5_notebook_prepare.py','approved check_static.py B5 attempts 001,002,003','Pinned Python -I -B supplementary/b5_type_repair.py','Pinned Python -I -B supplementary/b5_display_repair.py','Pinned Python -I -B supplementary/b5_execute_nbconvert.py (two attempts)','Pinned Python -I -B supplementary/b5_inspect_saved.py','Pinned Python -I -B supplementary/b5_close.py'],'incidents':['Type annotations on frozen ExpressionManager accept numbers but the approved symbolic workflow maps SymPy Symbols. Narrow typing.cast at each symbolic mapping corrects generated caller annotations without changing runtime or frozen code.','First final notebook execution stopped only on symbolic coefficient display float conversion; precision=0 repaired the generated display, static and final execution rerun passed.','Prior B2 additional/B3 trial numerical imports preceded thread environment setup; actual BLAS thread counts unavailable for those processes. Preserved in B3 record. Subsequent final verification configured thread environment before numerical imports.'],'provider_usage':'unavailable','completed_utc':state['completed_utc']}
(root/'supplementary/closure.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print('B5 complete; all required proof and notebook gates passed.')
print('Notebook SHA-256:',state['notebook_sha256'])
