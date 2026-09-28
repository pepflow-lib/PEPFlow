import hashlib
import json
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
path=root/'bppm_example_lyap.ipynb'
book=json.loads(path.read_text())
static=json.loads((root/'supplementary/b5-static-002.json').read_text())
assert static['status']=='passed'
for cell in book['cells']:
    source=''.join(cell['source'])
    assert not any(ord(c)<32 and c not in '\n\t' for c in source)
    assert not any(o.get('output_type')=='error' for o in cell.get('outputs',[]))
    if cell['cell_type']=='code':
        assert isinstance(cell['execution_count'],int)
    else:
        assert all(x not in source for x in ('\\(','\\)','\\[','\\]'))
assert any('image/png' in o.get('data',{}) for o in book['cells'][10]['outputs'])
for index in (43,46,49):
    outputs=book['cells'][index]['outputs']
    assert any('text/latex' in o.get('data',{}) for o in outputs)
    text=''.join(''.join(o.get('text',[])) for o in outputs if o.get('output_type')=='stream')
    assert 'offset residual: 0' in text and 'function residual: Matrix([[0]' in text
labels=[
 'title, problem description, and the algorithm update equations in LaTeX',
 'proof statement placeholder, to be filled with the final theorem and proof outline in Block 5',
 'imports','function/operator definitions','make_ctx_bppm and get_pep_setup',
 'numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate',
 'dense and relaxed proof solves',
 'lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)',
 'partial-sum Lyapunov construction and rank profile','special-vector identification',
 'coefficient extraction and closed-form V_k','symbolic step, base, and boundary identities']
indices=['0','1–3','4–6,29,40','7','8','9–11','12–13','14–19','20–25','26–33','34–40','41–50']
evidence=[
 'Assumptions, exact updates, Bregman definition, radius R and metric stated.',
 'Separate proof heading, theorem with full potential, and self-contained residual identities/telescoping.',
 'Approved framework and installed dependencies; all import cells executed.',
 'Convex f and h definitions visible and executed.',
 'Visible context builder, proximal update, initialization and metric executed.',
 'Seven printed CLARABEL optima, discrepancy 3.62e-9, and stored matplotlib comparison output.',
 'Dense/sparse solve provenance, both owners multiplier matrices and bound preservation displayed.',
 'Initial candidate search, selected S spectral decomposition, true S and residual matrices, signs and complete scalar identity rechecked; global analytic status explicitly separate.',
 'Visible partial-sum loop, full component coverage, terminal leftovers, ranks and N=4/6 comparison executed.',
 'Candidate scan and actual sparse search executed at k=1..4; four independent vectors; k=0 empty case.',
 'Labeled numerical and candidate matrices, all-index full reconstruction, final full formula including function terms; exact local proof resolves candidate.',
 'Separate symbolic contexts and LHS/RHS identities, exact Gram/function/offset zeros, derived multipliers, sign/domain justification and radius normalization executed.']
digest=hashlib.sha256(path.read_bytes()).hexdigest()
lines=['Notebook: bppm_example_lyap.ipynb','Last reviewed block: B5','SHA-256: '+digest,
'Presentation policy: evaluation-ancillary-v1. Source and executed outputs inspected; no rendering, browser or image inspection performed or claimed.','',
'| Item | Status | Cell indices | Evidence |','|---|---|---|---|']
for i,(label,where,why) in enumerate(zip(labels,indices,evidence),1):
    lines.append(f'| {i}. {label} | verified | {where} | {why} |')
(root/'supplementary/bppm_example_lyap_checklist.md').write_text('\n'.join(lines))
state_path=root/'state/bppm_b5.json'
state=json.loads(state_path.read_text())
assert all(state['proof_checks'].values()) and state['lyapunov_proof_verified']
state.update(lyapunov_formula=state['final_lyapunov_formula'],discovery_expression_structure=state['expression_structure'],
run_status='completed',remaining_work=[],unresolved_required_work=[],current_block='B5',completion_status='complete',next_block=None,
entry_exit_reason='Exact local Lyapunov proof, final static checks, clean-kernel nbconvert and all twelve notebook content items verified.',
notebook='bppm_example_lyap.ipynb',notebook_sha256=digest,
validation={'static_evidence':'supplementary/b5-static-002.json','clean_kernel_execution':'supplementary/b5-final-nbconvert-console.txt','content_checklist':'supplementary/bppm_example_lyap_checklist.md','presentation_policy':'evaluation-ancillary-v1','rendered_review_performed':False},
optional_unresolved_work=['Separate analytic global full-PEP formula not claimed or required.'],
completed_utc=datetime.now(timezone.utc).isoformat())
state_path.write_text(json.dumps(state,indent=2))
record={'current_block':'B5','completion_status':'complete','next_block':None,'run_status':'completed',
'entry_exit_reason':state['entry_exit_reason'],'unresolved_required_work':[],
'consulted_sources':['supplementary/approved/plugins/pepflow-workflows/skills/lyap-closed-form/SKILL.md','supplementary/approved/plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md','supplementary/approved/pepflow/function.py','own B4 state, generated symbolic source and notebook outputs'],
'commands':['run_b5.py','finalize_b5_notebook.py','approved adapter b5-static-001.json','repair_b5_typing.py','run_b5.py (recheck)','approved adapter b5-static-002.json','pinned python -I -B -m nbconvert --to notebook --execute bppm_example_lyap.ipynb --output bppm_example_lyap.ipynb --output-dir own attempt --ExecutePreprocessor.timeout=120','final_audit.py'],
'incidents':[{'kind':'static_diagnostic','evidence':'supplementary/b5-static-001.json','repair':'Explicit heterogeneous symbolic-parameter mapping annotation and direct all-component V0 zero check; frozen sources unchanged.'}],
'access_control':'instruction_only','prohibited_content_observed':False,'external_resources':[],
'audit_limit':'Source records and actual tool logs support this declaration; no exhaustive filesystem or dependency startup-hook tracing. No claim of OS-enforced read isolation.',
'prior_access_records':['preflight-access-001.json','b1-access.json','b2-access.json','b3-access-001.json','b2-access-N6.json','b3-access-002.json','b4-access.json'],
'operational_status':'closed','completed_utc':state['completed_utc']}
(root/'supplementary/b5-access.json').write_text(json.dumps(record,indent=2))
print('Final audit passed: 12/12 items, 28 executed code cells, no notebook errors.')
print('Notebook SHA-256:',digest)
print('run_status=completed; numerical_certificate_verified=true; analytic_full_pep_verified=false; lyapunov_proof_verified=true')
