"""Close the B3 evidence checklist and hand off the selected sample."""
import hashlib
import json
from pathlib import Path
import re
import nbformat as nbf

root=Path(__file__).resolve().parents[1]
assert json.loads((root/'supplementary/b3-static-001.json').read_text())['status']=='passed'
nbpath=root/'bppm_example_lyap.ipynb'
nb=nbf.read(nbpath,as_version=4)
assert all(c.execution_count is not None for c in nb.cells if c.cell_type=='code')
checkpath=root/'supplementary/bppm_example_lyap_checklist.md'
text=checkpath.read_text()
text=re.sub(r'Last reviewed block: .*','Last reviewed block: B3',text)
text=re.sub(r'SHA-256: [a-f0-9]+','SHA-256: '+hashlib.sha256(nbpath.read_bytes()).hexdigest(),text)
lines=text.splitlines()
for i,line in enumerate(lines):
    if line.startswith('| 9 |'):
        lines[i]='| 9 | partial-sum Lyapunov construction and rank profile | verified | 25-31 | Saved certificate revalidated, visible grouping/coverage code executed; rank 4 at N=4 and N=6 with fixed exclusions (1,1), wide singular-value gap. |'
    elif line.startswith('| 10 |'):
        lines[i]='| 10 | special-vector identification | pending | 32 | B4 |'
    elif line.startswith('| 11 |'):
        lines[i]='| 11 | coefficient extraction and closed-form V_k | pending | 33 | B4/B5 |'
    elif line.startswith('| 12 |'):
        lines[i]='| 12 | symbolic step, base, and boundary identities | pending | 33 | B5 |'
checkpath.write_text('\n'.join(lines)+'\n')
p=root/'state/bppm_b3.json'
state=json.loads(p.read_text())
state.update(completion_status='complete',static_evidence='supplementary/b3-static-001.json',execution_evidence='supplementary/b3-execution.json')
p.write_text(json.dumps(state,indent=2))
audit={'current_block':'B3','access_control':'instruction_only','prior_record':'b3-access-record-001.json',
       'new_approved_reads':[], 'generated_reads':['supplementary/bppm_N6_b2.json','supplementary/b3-trial-N4.json','supplementary/b3-trial-N6.json','supplementary/b3_certificate_check.py','supplementary/b3_decomposition.py','supplementary/b3_grouping.py','state/bppm_b2.json','state/bppm_b3.json','bppm_example_lyap.ipynb','supplementary/b3-static-001.json','supplementary/bppm_example_lyap_checklist.md'],
       'commands':['python -I -B supplementary/run_b3_trial.py supplementary/bppm_N6_b2.json','python -I -B supplementary/complete_b3.py','python -I -B supplementary/execute_notebook.py B3','approved static adapter; b3-static-001.json','python -I -B supplementary/finalize_b3.py'],
       'source_hash_reads':'Only exact certificate provenance source files', 'prohibited_content_observed':False,'incidents':[],
       'audit_limit':'Instruction-only access; no exhaustive OS read trace.'}
(root/'supplementary/b3-access-record-002.json').write_text(json.dumps(audit,indent=2))
handoff={'current_block':'B3','completion_status':'complete','next_block':'B4',
         'entry_exit_reason':'Same-recipe rank confirmed at two independently verified horizons; selected N=4 coverage and notebook checks pass',
         'operational_status':'awaiting_same_session_continuation','next_block_started':False,
         'deadline_utc':'2026-09-24T00:34:49.219272+00:00'}
(root/'supplementary/b3-handoff-002.json').write_text(json.dumps(handoff,indent=2))
print(json.dumps(handoff))
