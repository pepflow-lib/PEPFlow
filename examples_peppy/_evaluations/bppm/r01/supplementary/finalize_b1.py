import json
import hashlib
from pathlib import Path
root = Path.cwd()
nbpath = root / 'bppm_example_lyap.ipynb'
nb = json.loads(nbpath.read_text())
items = ['title, problem description, and the algorithm update equations in LaTeX','proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','imports','function/operator definitions','make_ctx_bppm and get_pep_setup','numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','dense and relaxed proof solves','lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','partial-sum Lyapunov construction and rank profile','special-vector identification','coefficient extraction and closed-form V_k','symbolic step, base, and boundary identities']
workflow = (root / 'supplementary/approved/plugins/pepflow-workflows/skills/pep-implement/references/workflow.md').read_text(encoding='utf-8')
import re
numbered = re.findall(r'^([1-9]|1[0-2])\. (.+)$',workflow,re.M)
items = [label for number,label in numbered[:12]]
assert len(items)==12
for i,c in enumerate(nb['cells']):
    source=''.join(c['source'])
    assert not any(ord(ch)<32 and ch not in '\n\t' for ch in source)
    if c['cell_type']=='markdown':
        assert '\\(' not in source and '\\[' not in source
    if c['cell_type']=='code':
        assert c['execution_count'] is not None
        assert not any(o['output_type']=='error' for o in c['outputs'])
    print(i,c['cell_type'],source[:95].replace('\n',' '))
    for o in c.get('outputs',[]):
        if o['output_type']=='stream':
            print(''.join(o['text']))
        elif o['output_type']=='display_data':
            print('Output formats:',list(o['data']))
assert any('image/png' in o.get('data',{}) for o in nb['cells'][9]['outputs'])
assert json.loads((root/'supplementary/b1-sweep.json').read_text()) == json.loads((root/'supplementary/b1-sweep-original.json').read_text())
assert json.loads((root/'supplementary/b1-static-003.json').read_text())['preflight_passed']
indices={1:[0],2:[1],3:[2,3],4:[5],5:[7],6:[9,10]}
lines=['# Notebook evidence checklist', 'Notebook: bppm_example_lyap.ipynb', 'Last reviewed block: B1', 'SHA-256: '+hashlib.sha256(nbpath.read_bytes()).hexdigest(), 'Presentation policy: evaluation-ancillary-v1; rendering and image inspection omitted as instructed. Source content, text outputs, stored plot output and fresh-kernel execution checked.', '', '| Item | Status | Cells | Evidence |','|---|---|---|---|']
for n,item in enumerate(items,1):
    status='verified' if n in (1,3,4,5,6) else 'pending'
    ids=', '.join(f'{j} ({nb["cells"][j]["id"]})' for j in indices.get(n,[]))
    reason='Visible source inspected; fresh-kernel execution passed; Ruff and ty passed.' if status=='verified' else 'Later-block obligation.'
    if n==6: reason='Seven optimal CLARABEL values; max error 3.622e-9; printed inverse-rate increments; stored PNG plot compares both curves. No visual inspection under presentation override.'
    lines.append(f'| {n}. {item} | {status} | {ids} | {reason} |')
(root/'supplementary/bppm_example_lyap_checklist.md').write_text('\n'.join(lines))
record={'current_block':'B1','completion_status':'complete','next_block':'B2','entry_exit_reason':'Dispatched after preflight; setup, sweep, notebook execution and static checks complete.','run_status':'awaiting_continuation','dispatch_utc':'2026-09-23T15:01:13.976153+00:00','deadline_utc':'2026-09-23T17:01:13.976153+00:00','access_control':'instruction_only','sources':['approved/dispatch.md','approved/input.md','approved/worker-protocol.md','approved/plugins/pepflow-workflows/skills/pep-implement/SKILL.md','approved/plugins/pepflow-workflows/skills/pep-implement/references/workflow.md','approved/plugins/pepflow-workflows/skills/pep-full-proof/SKILL.md','approved/plugins/pepflow-workflows/skills/lyap-define/SKILL.md','approved/plugins/pepflow-workflows/skills/lyap-vectors/SKILL.md','approved/plugins/pepflow-workflows/skills/lyap-closed-form/SKILL.md','approved/plugins/pepflow-workflows/references/output-layout.md','approved/pepflow/function.py','approved/pepflow/__init__.py','approved/pepflow/pep_runner.py','approved/pepflow/pep.py','approved/plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py'],'commands':['run_b1.py executed before and after annotation-only setup change; preserved both logs','build_b1_notebook.py executed three times; each log preserved','three static adapter check invocations; exact commands in b1-static-001/002/003.json','finalize_b1.py inspected saved notebook text and output metadata without viewing images'],'incidents':[{'classification':'operational','evidence':'b1-static-001.json','issue':'Windows path-length error staging wide supplementary helper root','repair':'Narrow attempt-owned supplementary/helpers root and matching probe layout; generic preflight rerun by adapter passed.'},{'classification':'source diagnostics','evidence':'b1-static-002.json','issue':'Notebook import ordering and symbolic Parameter versus Number annotation','repair':'Separate import cell; Any annotation for supported symbolic parameter; checks passed in b1-static-003.json.'}],'prohibited_content_observed':False,'observability_limit':'No exhaustive OS read trace; declaration limited to tool-visible activity.','unresolved_work':'B2-B5 not started.','usage':None}
(root/'supplementary/b1-access-handoff.json').write_text(json.dumps(record,indent=2))
print('B1 saved-artifact checks passed.')
