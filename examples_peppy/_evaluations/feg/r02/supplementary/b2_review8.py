import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'feg_example_lyap.ipynb'
nb=json.loads(p.read_text(encoding='utf-8'))
for c in nb['cells']:
    s=''.join(c['source'])
    if c['cell_type']=='markdown':
        assert s.count('$')%2==0 and not any(x in s for x in ('\\(','\\)','\\[','\\]','\x0c','\r'))
print(''.join(o.get('text',[]) for o in []))
for o in nb['cells'][20]['outputs']:
    if o['output_type']=='stream': print(''.join(o['text']))
checklist=root/'supplementary/feg_example_lyap_checklist.md'
lines=checklist.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('SHA-256:'): lines[i]='SHA-256: '+hashlib.sha256(p.read_bytes()).hexdigest()
    if line.startswith('| 7 |'): lines[i]=line.replace('| 12,13,15 |','| 12,13,15,19,20 |').replace('all groups covered.','all groups covered; N8 confirmation acquired with the same recipe and verified.')
    if line.startswith('| 9 |'): lines[i]=line.replace('| 19 |','| 21 |')
    if line.startswith('| 10 |'): lines[i]=line.replace('| 20 |','| 22 |')
    if line.startswith('| 11 |') or line.startswith('| 12 |'): lines[i]=line.replace('| 21 |','| 23 |')
checklist.write_text('\n'.join(lines))
record=dict(current_block='B2',completion_status='complete_confirmation_certificate',next_block='B3',entry_exit_reason='Acquired coherent N8 dense/relaxed certificate with preserved optimum, full checks and decomposition; selected N6 remains unchanged.',operational_status='awaiting_same_session_continuation',confirmation_certificate='supplementary/N8/feg_b2.json',sources=['Own prior B2 scripts and states','Exact approved framework paths hashed in certificate'],commands=['Python -I -B supplementary/b2_acquire8.py','Python -I -B supplementary/b2_finalize8.py','Python -I -B supplementary/b2_notebook8.py','Python -I -B supplementary/execute_notebook.py','Approved static adapter b2-N8-static-001.json'],incidents=[dict(classification='PowerShell script execution disabled',action='Returned to original inline argv invocation; no policy change')],access_control='instruction_only',prohibited_exposure_observed=False,unresolved=['B3 cross-horizon rank confirmation','Blocks 4–5'])
(root/'supplementary/b2-N8-handoff.json').write_text(json.dumps(record,indent=2))
