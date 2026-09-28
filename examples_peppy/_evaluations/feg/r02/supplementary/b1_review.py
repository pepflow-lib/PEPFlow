import json
import hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[1]
p = root / 'feg_example_lyap.ipynb'
nb = json.loads(p.read_text(encoding='utf-8'))
for c in nb['cells']:
    s = ''.join(c['source'])
    if c['cell_type'] == 'markdown':
        assert not any(x in s for x in ('\\(', '\\)', '\\[', '\\]', '\x0c', '\r'))
        assert s.count('$') % 2 == 0
items = [
('title, problem description, and the algorithm update equations in LaTeX','verified','0','Source equations and assumptions inspected; presentation override applies.'),
('proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','pending','1','Placeholder present; final theorem due B5.'),
('imports','verified','2,3','Fresh-kernel output confirms approved framework origin.'),
('function/operator definitions','verified','5','LipschitzMonotoneOperator and L,R parameters inspected.'),
('make_ctx_feg and get_pep_setup','verified','7,8','Exact updates, R squared constraint, final metric; shared point assertion passed.'),
('numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','verified','9,10,11','Seven optimal results printed; image/png plot output present; no image inspection under evaluation policy.'),
('dense and relaxed proof solves','pending','12','Due B2.'),
('lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','pending','13','Due B2.'),
('partial-sum Lyapunov construction and rank profile','pending','14','Due B3.'),
('special-vector identification','pending','15','Due B4.'),
('coefficient extraction and closed-form V_k','pending','16','Due B4/B5.'),
('symbolic step, base, and boundary identities','pending','16','Due B5.')]
lines = ['Notebook: feg_example_lyap.ipynb','Last reviewed block: B1','SHA-256: '+hashlib.sha256(p.read_bytes()).hexdigest(),'Presentation policy: evaluation-ancillary-v1; source/delimiter checks and executed outputs only; no rendered or image review.','','| Item | Requirement | Status | Cell indices | Evidence |','|---|---|---|---|---|']
for i,(name,status,cells,ev) in enumerate(items,1):
    lines.append(f'| {i} | {name} | {status} | {cells} | {ev} |')
(root/'supplementary/feg_example_lyap_checklist.md').write_text('\n'.join(lines))

record = dict(current_block='B1', completion_status='complete', next_block='B2', entry_exit_reason='Initial dispatch; setup, rate sweep, notebook and required checks completed.', operational_status='awaiting_same_session_continuation', access_control='instruction_only', prohibited_exposure_observed=False, limitations='No exhaustive OS access trace; no claim of enforced isolation.')
record['sources'] = ['approved/dispatch.md','approved/input.md','approved/worker-protocol.md','approved/plugins/pepflow-workflows/references/output-layout.md','approved/plugins/pepflow-workflows/skills/pep-implement/references/workflow.md']
record['sources'] += ['approved/plugins/pepflow-workflows/skills/'+s+'/SKILL.md' for s in ('pep-implement','pep-full-proof','lyap-define','lyap-vectors','lyap-closed-form')]
record['sources'] += ['approved/pepflow/'+s for s in ('operator.py','pep_runner.py','__init__.py','pep.py','solver.py','pep_result.py')]
record['sources'] += ['approved/plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py']
record['commands'] = ['Python -I -B supplementary/b1_sweep.py','Python -I -B supplementary/b1_notebook.py (two executions, second splits bootstrap/import cells)','Approved adapter commands/configuration captured in b1-static-001/002/003.json','PowerShell exact-file source reads and rg searches; own notebook source/output inspection','Python -I -B supplementary/b1_review.py']
record['incidents'] = [{'evidence':'b1-static-001.json','classification':'operational path-length error','repair':'Narrow helper root to supplementary/helpers and probe-helper-path to supplementary/helpers/runtime.py; repeated full preflight and checks.'},{'evidence':'b1-static-002.json','classification':'Ruff E402 in notebook bootstrap','repair':'Separate bootstrap/import cells; fresh execution and static checks passed in b1-static-003.json.'}]
record['verification'] = {'fresh_kernel':'b1-notebook-002-console.txt','static':'b1-static-003.json','markdown_delimiters':'passed','plot_output':'image/png present; not visually inspected under evaluation override'}
(root/'supplementary/b1-access-handoff.json').write_text(json.dumps(record,indent=2))
print('B1 checklist and access/handoff record saved.')
