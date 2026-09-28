import hashlib
import json
from pathlib import Path
import nbformat
root=Path(__file__).resolve().parents[1]
path=root/'pgm_example_lyap.ipynb'
nb=nbformat.read(path,as_version=4)
for c in nb.cells:
    if c.cell_type=='markdown':
        assert not any(s in c.source for s in ('\x0c','\r','\t','\\(','\\[','\\)','\\]'))
    assert all(o.output_type!='error' for o in c.get('outputs',[]))
start=next(i for i,c in enumerate(nb.cells) if c.cell_type=='markdown' and c.source.startswith('## Identify the vectors'))
for i in range(start,len(nb.cells)-1):
    print(i,nb.cells[i].cell_type,[o.output_type for o in nb.cells[i].get('outputs',[])])
checkpath=root/'supplementary/pgm_example_lyap_checklist.md'
lines=checkpath.read_text().replace('Last reviewed block: B3','Last reviewed block: B4').splitlines()
lines=[('SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()) if l.startswith('SHA-256:') else l for l in lines]
lines=[l.replace('| pending | Later-block requirement |',f'| verified | {start}-{start+9}: candidate deduplication/filtering, actual sparse searches, consistent template and all-index independent/full-component reconstruction |') if l.startswith('| 10.') else l for l in lines]
lines=[l.replace('Later-block requirement','Numerical coefficients and candidate formulas checked in B4; exact closed form remains pending B5') if l.startswith('| 11.') else l for l in lines]
checkpath.write_text('\n'.join(lines))
e=json.loads((root/'supplementary/b4-static-002.json').read_text())
assert e['status']=='passed'
record=dict(current_block='B4',completion_status='complete',next_block='B5',entry_exit_reason='All-index basis and full scalar reconstruction verified; candidate formulas recorded; notebook/static checks passed',operational_status='awaiting_same_session_continuation',state='state/pgm_b4.json',static_evidence='supplementary/b4-static-002.json',notebook_execution='supplementary/b4-notebook-console-003.txt',new_sources='Own basis_structure.py, finalize/check/update/refresh/close B4 scripts, state and scan outputs; no external sources',commands=['check_b4_blend.py','finalize_b4.py','update_b4_notebook.py','refresh_b4_source.py','execute_notebook.py','approved check_static.py check (two invocations)'],operational_repairs=['Notebook-builder variable typo repaired before successful update','Ruff semicolon formatting and ty SymPy expression assertions corrected; mathematical formulas unchanged'],access_control='instruction_only',access_status='no_observed_prohibited_exposure',original_deadline_utc='2026-09-23T18:17:47.370960+00:00',unresolved_work='B5 exact arbitrary-horizon proof and final notebook verification')
(root/'supplementary/b4-handoff.json').write_text(json.dumps(record,indent=2))
