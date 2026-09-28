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
for i in (22,23):
    print(i,''.join(''.join(o.get('text',[])) for o in book['cells'][i].get('outputs',[]) if o.get('output_type')=='stream'))
checklist=root/'supplementary/bppm_example_lyap_checklist.md'
lines=checklist.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'): lines[i]='Last reviewed block: B3'
    if line.startswith('SHA-256:'): lines[i]='SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()
    if line.startswith('| 9.'):
        lines[i]='| 9. partial-sum Lyapunov construction and rank profile | verified | 18–23 | Certificate replay, complete PSD boundary block, explicit signed grouping, ranks [0,4,4,4,4], N=4/6 confirmation and full-coordinate coverage executed. |'
    if line.startswith('| 10.') or line.startswith('| 11.'): lines[i]=line.replace('| 19 |','| 24 |')
    if line.startswith('| 12.'): lines[i]=line.replace('| 20 |','| 25 |')
checklist.write_text('\n'.join(lines))
record={'current_block':'B3','completion_status':'complete','next_block':'B4','entry_exit_reason':'Rank and coverage confirmed at N=4 and N=6 with fixed recipe and exclusions; selected N=4 state and notebook updated.',
'consulted_sources':['own B2 states, generated B3 source and samples','previously read approved lyap-define workflow'],
'commands':['run_b3_N6.py','finalize_b3.py','update_b3_notebook.py','approved adapter b3-static-001.json','inspect_b3.py'],
'access_control':'instruction_only','prohibited_content_observed':False,'incidents':[],'operational_status':'awaiting same-session continuation'}
(root/'supplementary/b3-access-002.json').write_text(json.dumps(record,indent=2))
