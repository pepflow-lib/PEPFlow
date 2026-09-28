import json
import hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'bppm_example_lyap.ipynb'
nb=json.loads(p.read_text())
for c in nb['cells']:
    source=''.join(c['source'])
    assert not any(x in source for x in ('\x0c','\x08','\r'))
    if c['cell_type']=='code':
        assert c['execution_count'] is not None
        assert all(o['output_type']!='error' for o in c['outputs'])
q=root/'supplementary/bppm_example_lyap_checklist.md'
s=q.read_text().splitlines()
for i,line in enumerate(s):
    if line.startswith('SHA-256:'): s[i]='SHA-256: '+hashlib.sha256(p.read_bytes()).hexdigest()
    if line.startswith('|7|'): s[i]=line.replace('|10,11,12|','|10,11,12,17,18|')
    if line.startswith('|8|'): s[i]=line.replace('|13,14,15,16|','|13,14,15,16,18|')
    if line.startswith('|9|'): s[i]=line.replace('|17|','|19|')
    if line.startswith('|10|'): s[i]=line.replace('|18|','|20|')
    if line.startswith('|11|'): s[i]=line.replace('|18,19|','|20,21|')
    if line.startswith('|12|'): s[i]=line.replace('|19|','|21|')
q.write_text('\n'.join(s))
record={'phase':'B2_revisit_N6','new_external_sources':[],'own_generated_sources':['supplementary/prepare_b2_N6.py','supplementary/run_b2_N6.py','supplementary/b2_core.py','supplementary/update_b2_confirmation.py','supplementary/inspect_b2_confirmation.py'],'evidence':['supplementary/b2_N6.console.txt','supplementary/b2_N6_notebook.console.txt','supplementary/b2-static-003.json'],'notes':'Duplicate context-name warning expected from creating a fresh builder for each solve; no older builder reused. Numerical checks passed.','access_control':'instruction_only','prohibited_content_observed':False,'audit_limit':'No exhaustive OS read tracing.'}
(root/'supplementary/b2_N6-consulted-sources.json').write_text(json.dumps(record,indent=2))
