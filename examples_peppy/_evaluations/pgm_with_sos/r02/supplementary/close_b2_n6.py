import hashlib
import json
from pathlib import Path
import nbformat
root=Path(__file__).resolve().parents[1]
path=root/'pgm_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
for c in nb.cells:
    if c.cell_type=='markdown':
        c.source=c.source.replace('\times',r'\times')
        assert not any(s in c.source for s in ('\x0c','\r','\t','\\(','\\[','\\)','\\]'))
nbformat.write(nb,path)
checkpath=root/'supplementary/pgm_example_lyap_checklist.md'
lines=checkpath.read_text().splitlines()
lines=[('SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()) if l.startswith('SHA-256:') else l for l in lines]
lines=[l.replace('11-16:','11-18:') for l in lines]
checkpath.write_text('\n'.join(lines))
e=json.loads((root/'supplementary/b2-n6-static-001.json').read_text())
assert e['status']=='passed'
record=dict(current_block='B2',completion_status='complete',next_block='B3',entry_exit_reason='Second-horizon coherent sparse certificate acquired and checked',operational_status='awaiting_same_session_continuation',additional_certificate='supplementary/b2-n6-certificate.json',selected_certificate_unchanged='state/pgm_b2.json',static_evidence='supplementary/b2-n6-static-001.json',notebook_execution='supplementary/b2-n6-notebook-console.txt',solver_note='Dense N=6 optimal_inaccurate recorded; sparse N=6 optimal and independently verified',sources='Own generated scripts and approved framework already recorded; no new external sources',commands=['acquire_b2_n6.py','update_b2_n6_notebook.py','execute_notebook.py','approved check_static.py check'],access_control='instruction_only',access_status='no_observed_prohibited_exposure',original_deadline_utc='2026-09-23T18:17:47.370960+00:00')
(root/'supplementary/b2-n6-handoff.json').write_text(json.dumps(record,indent=2))
print('Additional certificate B2 handoff ready')
