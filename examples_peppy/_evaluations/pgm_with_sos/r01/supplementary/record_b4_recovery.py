import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'helpers'))
import runtime
import json
import hashlib
import re
import nbformat as nb
root=runtime.ATTEMPT
path=root/'pgm_example_lyap.ipynb'
book=nb.read(path,as_version=4)
book.cells[15].source='''## Identify the vectors composing the Lyapunov function
Block 4 candidate scan is incomplete. Tagged vectors, gradient values, point-to-optimum gaps, composite gradients, and pairwise differences were scanned using the existing framework utilities. A four-vector family was found at early indices, but no candidate subset passed the fixed span tolerance at indices 5 and 6. The complete failed scan is preserved in `supplementary/b4-scan-001.json` with executed source in `supplementary/scan_b4.py`. No Block 4 state is issued. Return to Block 3 to test a better numerical decomposition of the same certificate before retrying all-index reconstruction.'''
nb.write(book,path)
p=root/'supplementary/pgm_example_lyap_checklist.md'
s=p.read_text()
s=re.sub(r'Last reviewed block:.*','Last reviewed block: B4 incomplete; return to B3',s)
s=re.sub(r'SHA-256: [a-f0-9]+','SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest(),s)
s=s.replace('| pending | 15 | Due B4. |','| failed | 15 | Candidate scan failed required span tolerance at k=5 and k=6; recovery returns to B3. |')
p.write_text(s)
record=dict(current_block='B4',completion_status='incomplete',next_block='B3',entry_exit_reason='All-index basis reconstruction failed at fixed span tolerance; numerical decomposition recovery required',operational_status='awaiting_same_session_continuation',sources=['supplementary/approved/plugins/pepflow-workflows/skills/lyap-vectors/references/workflow.md','supplementary/approved/pepflow/lyapunov_utils.py','state/pgm_b3.json','supplementary/scan_b4.py'],commands=['Pinned Python -I -B supplementary/scan_b4.py'],evidence=['supplementary/b4-scan-001.json','supplementary/b4-scan-001-output.txt'],access_control='instruction_only',prohibited_sources_observed=False,audit_limit='No exhaustive filesystem audit',unresolved_work='Reconstructing basis at k=5,N; B4-B5',deadline_utc='2026-09-23T16:12:00.406449+00:00')
(root/'supplementary/b4-handoff-001.json').write_text(json.dumps(record,indent=2))
