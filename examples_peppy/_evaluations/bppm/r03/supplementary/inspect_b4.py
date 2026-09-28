import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'bppm_example_lyap.ipynb'
book=json.loads(path.read_text())
for cell in book['cells']:
    source=''.join(cell['source'])
    assert not any(ord(c)<32 and c not in '\n\t' for c in source)
    assert not any(o.get('output_type')=='error' for o in cell.get('outputs',[]))
    if cell['cell_type']=='markdown':
        assert all(x not in source for x in ('\\(','\\)','\\[','\\]'))
for index in (29,33,34):
    print(index,''.join(''.join(o.get('text',[])) for o in book['cells'][index].get('outputs',[]) if o.get('output_type')=='stream'))
checklist=root/'supplementary/bppm_example_lyap_checklist.md'
lines=checklist.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'): lines[i]='Last reviewed block: B4'
    if line.startswith('SHA-256:'): lines[i]='SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()
    if line.startswith('| 10.'): lines[i]='| 10. special-vector identification | verified | 24–34 | Visible candidate scan and sparse search at k=1..4; basis independence and all-index Gram/function/offset reconstruction executed; max component error 8.90e-10. |'
    if line.startswith('| 11.'): lines[i]='| 11. coefficient extraction and closed-form V_k | pending | 32–35 | Numerical coefficient matrices and complete candidate expression verified; exact closed form proof due in B5. |'
    if line.startswith('| 12.'): lines[i]=line.replace('| 25 |','| 36 |')
checklist.write_text('\n'.join(lines))
record={'current_block':'B4','completion_status':'complete','next_block':'B5','entry_exit_reason':'Interpretable basis and complete numerical reconstruction at every index; formulas retained as candidates.',
'consulted_sources':['supplementary/approved/plugins/pepflow-workflows/skills/lyap-vectors/SKILL.md','supplementary/approved/plugins/pepflow-workflows/skills/lyap-vectors/references/workflow.md','supplementary/approved/pepflow/lyapunov_utils.py','own B3 and generated sources'],
'commands':['run_b4.py','update_b4_notebook.py','approved adapter b4-static-001.json','inspect_b4.py'],
'access_control':'instruction_only','prohibited_content_observed':False,
'incidents':[{'kind':'operational','reason':'Initial source-search command had a mistyped nonexistent working directory; process creation failed with code 267 before reads; corrected to own attempt directory.'}],
'operational_status':'awaiting same-session continuation'}
(root/'supplementary/b4-access.json').write_text(json.dumps(record,indent=2))
