import json
import hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'dual_feg_example_lyap.ipynb'
nb=json.loads(p.read_text())
for i,c in enumerate(nb['cells']):
    src=''.join(c['source'])
    if c['cell_type']=='markdown':
        assert '\\(' not in src and '\\[' not in src
    for o in c.get('outputs',[]):
        assert o['output_type']!='error'
        if i==12 and 'text' in o:
            print(''.join(o['text']))
check=root/'supplementary/dual_feg_example_lyap_checklist.md'
lines=check.read_text().splitlines()
lines[1]='Last reviewed block: B2 revisit (N=8)'
lines[2]='SHA-256: '+hashlib.sha256(p.read_bytes()).hexdigest()
for i,line in enumerate(lines):
    if line.startswith('| 7.') or line.startswith('| 8.'):
        lines[i]=line.replace('| 8,9,10 |','| 8,9,10,11,12 |')+' N=8 additional certificate replayed with full-coordinate checks.'
    for no,index in [(9,13),(10,14),(11,15),(12,16)]:
        if line.startswith(f'| {no}.'):
            parts=line.split('|')
            parts[3]=f' {index} '
            lines[i]='|'.join(parts)
check.write_text('\n'.join(lines))
record={'current_block':'B2','phase':'N8 acquisition revisit','new_approved_reads':[],'own_generated_scripts':['b2_acquire_n8.py','b2-n8-verification-source.py','update_b2_n8_notebook.py','review_b2_n8.py'],'certificate':'supplementary/n8-dual_feg_b2.json','prohibited_content_observed':False,'incidents':[],'access_control':'instruction_only'}
(root/'supplementary/b2-n8-access-record.json').write_text(json.dumps(record,indent=2))
