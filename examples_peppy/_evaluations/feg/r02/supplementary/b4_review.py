import json
import hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'feg_example_lyap.ipynb'
nb=json.loads(p.read_text(encoding='utf-8'))
for c in nb['cells']:
    s=''.join(c['source'])
    if c['cell_type']=='markdown':
        assert s.count('$')%2==0 and not any(x in s for x in ('\\(','\\)','\\[','\\]','\x0c','\r'))
for i in (29,31,32,34,36,38,39):
    assert nb['cells'][i]['execution_count'] is not None
    assert not any(o['output_type']=='error' for o in nb['cells'][i]['outputs'])
checklist=root/'supplementary/feg_example_lyap_checklist.md'
lines=checklist.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'): lines[i]='Last reviewed block: B4'
    if line.startswith('SHA-256:'): lines[i]='SHA-256: '+hashlib.sha256(p.read_bytes()).hexdigest()
    if line.startswith('| 10 |'): lines[i]='| 10 | special-vector identification | verified | 28–36 | 360 candidates, actual filter and sparse-basis searches, adopted common residual/anchor-gap basis, independence at all indices. |'
    if line.startswith('| 11 |'): lines[i]='| 11 | coefficient extraction and closed-form V_k | pending | 37–40 | Numerical extraction and all-component reconstruction verified at every index; exact coefficient functions remain named unknowns for B5. |'
    if line.startswith('| 12 |'): lines[i]=line.replace('| 29 |','| 41 |')
checklist.write_text('\n'.join(lines))
record=dict(current_block='B4',completion_status='complete',next_block='B5',entry_exit_reason='Consistent basis found and every index reconstructed, including endpoints; notebook and source checks complete.',operational_status='awaiting_same_session_continuation',sources=['approved/plugins/pepflow-workflows/skills/lyap-vectors/references/workflow.md','approved/pepflow/lyapunov_utils.py','Own B3 state and generated replay/search/coefficient files'],commands=['Python -I -B supplementary/b4_trial.py','Python -I -B supplementary/b4_finalize.py','Python -I -B supplementary/b4_notebook.py','Python -I -B supplementary/execute_notebook.py','Approved adapter b4-static-001/002.json','Notebook source/output inspection'],incidents=[dict(classification='Static keyword-unpacking inference error',repair='Use explicit unchanged tolerance keyword arguments; execute and recheck')],access_control='instruction_only',prohibited_exposure_observed=False,unresolved=['Exact coefficient functions and step/base/terminal proof in B5'])
(root/'supplementary/b4-access-handoff.json').write_text(json.dumps(record,indent=2))
print('B4 checklist updated')
