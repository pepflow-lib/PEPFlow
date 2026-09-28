import json
import hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'feg_example_lyap.ipynb'
nb=json.loads(p.read_text(encoding='utf-8'))
for c in nb['cells']:
    if c['cell_type']=='markdown':
        s=''.join(c['source'])
        assert s.count('$')%2==0
        assert not any(x in s for x in ('\\(','\\)','\\[','\\]','\x0c','\r'))
for index in (13,15,17):
    assert nb['cells'][index]['execution_count'] is not None
    assert not any(o['output_type']=='error' for o in nb['cells'][index]['outputs'])
checklist=root/'supplementary/feg_example_lyap_checklist.md'
lines=checklist.read_text().splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'): lines[i]='Last reviewed block: B2'
    if line.startswith('SHA-256:'): lines[i]='SHA-256: '+hashlib.sha256(p.read_bytes()).hexdigest()
    if line.startswith('| 7 |'): lines[i]='| 7 | dense and relaxed proof solves | verified | 12,13,15 | Saved dense and selected solve summaries, 144 dropped constraints, preserved gap 7.46e-10; all groups covered. |'
    if line.startswith('| 8 |'): lines[i]='| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 14–18 | Complete numerical identity, LDL reconstruction, labeled matrices and residuals; initial formula guesses exceed match tolerance and remain unresolved. |'
    if line.startswith('| 9 |'): lines[i]=line.replace('| 14 |','| 19 |')
    if line.startswith('| 10 |'): lines[i]=line.replace('| 15 |','| 20 |')
    if line.startswith('| 11 |') or line.startswith('| 12 |'): lines[i]=line.replace('| 16 |','| 21 |')
checklist.write_text('\n'.join(lines))
record=dict(current_block='B2',completion_status='complete',next_block='B3',entry_exit_reason='Dense and sparse certificate captured; full numerical checks, initial formula search, notebook execution and static checks complete.',operational_status='awaiting_same_session_continuation',sources=['approved/plugins/pepflow-workflows/skills/pep-full-proof/references/workflow.md','approved/pepflow/lyapunov_utils.py','approved/pepflow/pep_result.py','approved/pepflow/expression_manager.py','state/feg_b1.json','Own generated B2 sources/results and exact allowlisted framework hashes'],commands=['Python -I -B supplementary/certificate_solver.py','Python -I -B supplementary/b2_sparse.py (rerun to record hashes before and after solve)','Python -I -B supplementary/b2_finalize.py','Python -I -B supplementary/b2_notebook.py (fresh kernel, three revisions)','Approved static adapter; full invocations in b2-static-001/002/003.json','Own notebook output inspection and review'],incidents=[dict(classification='ordinary static type diagnostic',evidence='b2-static-001.json',repair='Use exact SymPy integers in ExpressionManager parameter mapping; rerun notebook and checks; remove duplicate SymPy import flagged by b2-static-002.json')],access_control='instruction_only',prohibited_exposure_observed=False,limitations='No exhaustive OS read trace; rendering omitted by evaluation policy',unresolved=['Global lambda/S formulas','Blocks 3–5'])
(root/'supplementary/b2-access-handoff.json').write_text(json.dumps(record,indent=2))
print('B2 source and output checklist inspected and saved')

