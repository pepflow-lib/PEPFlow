import json
import hashlib
from pathlib import Path
root=Path.cwd()
p=root/'pgm_example_lyap.ipynb'
book=json.loads(p.read_text())
for i,c in enumerate(book['cells']):
    if i>=12 and c['cell_type']=='code':
        assert c['execution_count'] is not None
        assert not any(o['output_type']=='error' for o in c['outputs'])
        output=''.join(''.join(o.get('text',[])) for o in c['outputs'])
        print('cell',i,'executed outputs',len(c['outputs']))
        if 'All-index full-expression' in output:
            print(output)
state=json.loads((root/'state/pgm_b4.json').read_text())
check=root/'supplementary/pgm_example_lyap_checklist.md'
s=check.read_text().replace('Last reviewed block: B3','Last reviewed block: B4')
s='\n'.join('SHA-256: '+hashlib.sha256(p.read_bytes()).hexdigest() if line.startswith('SHA-256:') else line for line in s.splitlines())
s=s.replace('| 10 | special-vector identification | pending | 12 | Due B4. |','| 10 | special-vector identification | verified | 12-22 | Candidate scan, actual sparse search and adopted consistent basis executed; independence and all-index reconstruction verified. |')
s=s.replace('| 11 | coefficient extraction and closed-form V_k | pending | 12,13 | Due B4/B5. |','| 11 | coefficient extraction and closed-form V_k | pending | 19-23 | B4 extraction and all component reconstructions passed, including endpoints; closed-form coefficients remain due B5. |')
s=s.replace('| pending | 13 | Due B5.', '| pending | 24 | Due B5.')
check.write_text(s)
record={'current_block':'B4','completion_status':'complete','next_block':'B5','entry_exit_reason':'Interpretable basis and complete expression reconstruction passed for all indices; notebook execution and static checks passed','run_status':'awaiting_same_session_continuation','state':'state/pgm_b4.json','unresolved_work':'Closed-form coefficients and exact step/base/terminal proof in B5','access_control':'instruction_only','prohibited_material_observed':False,'consulted_sources':['approved lyap-vectors/SKILL.md','approved lyap-vectors/references/workflow.md','approved pepflow/lyapunov_utils.py','own generated records'],'recovery':['Converted object coordinate arrays to float before numerical rank; split semicolon statements for Ruff.']}
(root/'supplementary/b4-handoff.json').write_text(json.dumps(record,indent=2))
