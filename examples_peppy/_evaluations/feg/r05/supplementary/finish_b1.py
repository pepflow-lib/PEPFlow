import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'feg_example_lyap.ipynb'
nb = json.loads(path.read_text())
for i, cell in enumerate(nb['cells']):
    source = ''.join(cell['source'])
    assert not any(c in source for c in ('\x0c', '\r'))
    if cell['cell_type'] == 'markdown':
        assert '\\(' not in source and '\\[' not in source
    outputs = cell.get('outputs', [])
    assert all(o['output_type'] != 'error' for o in outputs)
    print(i, cell['cell_type'], 'outputs:', [o['output_type'] for o in outputs])
    for output in outputs:
        if output['output_type'] == 'stream':
            print(''.join(output['text']))
assert any('image/png' in output.get('data', {}) for output in nb['cells'][9]['outputs'])
labels = ['title, problem description, and the algorithm update equations in LaTeX',
'proof statement placeholder, to be filled with the final theorem and proof outline in Block 5',
'imports', 'function/operator definitions', 'make_ctx_feg and get_pep_setup',
'numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate',
'dense and relaxed proof solves', 'lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)',
'partial-sum Lyapunov construction and rank profile', 'special-vector identification',
'coefficient extraction and closed-form V_k', 'symbolic step, base, and boundary identities']
verified = {1: '0: inspected assumptions, updates, first-half identity, metric', 3: '2,3: executable imports; pinned approved root', 4: '5: LipschitzMonotoneOperator with L and R', 5: '7: recurrence, alias, R squared initial constraint and metric', 6: '8,9,10: seven optimal values, candidate comparison assertion, saved PNG plot output'}
text = ['Notebook: feg_example_lyap.ipynb', 'Last reviewed block: B1', 'SHA-256: ' + hashlib.sha256(path.read_bytes()).hexdigest(), 'Presentation policy: evaluation-ancillary-v1; source/output inspection only; no visual rendering review.', '', '| Item | Status | Cells and evidence |', '|---|---|---|']
for i, label in enumerate(labels, 1):
    text.append(f'| {i}. {label} | {"verified" if i in verified else "pending"} | {verified.get(i, "Later-block requirement")} |')
(root / 'supplementary/feg_example_lyap_checklist.md').write_text('\n'.join(text))
record_path = root / 'supplementary/preflight-access-record.json'
record = json.loads(record_path.read_text(encoding='utf-8-sig'))
record['B1_reads'] = ['supplementary/approved/dispatch.md', 'supplementary/approved/input.md', 'supplementary/approved/worker-protocol.md', 'supplementary/approved/plugins/pepflow-workflows/references/output-layout.md'] + ['supplementary/approved/plugins/pepflow-workflows/skills/' + name + '/SKILL.md' for name in ['pep-implement','pep-full-proof','lyap-define','lyap-vectors','lyap-closed-form']] + ['supplementary/approved/plugins/pepflow-workflows/skills/pep-implement/references/workflow.md'] + ['supplementary/approved/pepflow/' + name for name in ['operator.py','pep_runner.py','pep.py','solver.py','pep_result.py','vector.py']] + ['supplementary/approved/plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py']
record['own_generated_reads'] = 'Own setup, notebook, B1 state, sweep cache, static evidence and generated scripts.'
record['B1_commands'] = ['sweep.py; CLARABEL defaults N=1..7', 'build_b1.py; fresh private kernel (three executions)', 'adapter check b1-static-001/002/003.json', 'adapter preflight preflight-002.json', 'finish_b1.py inspection']
record['incidents'] = [{'kind': 'operational', 'evidence': 'b1-static-001.json', 'reason': 'Broad helper root stages long approved paths; Windows path length failure', 'repair': 'Moved own runtime helper to supplementary/helpers; preflight-002 passed; frozen sources unchanged'}, {'kind': 'source_diagnostics', 'evidence': 'b1-static-002.json', 'repair': 'Separate bootstrap and import cells; reference runtime root explicitly'}]
record['status'] = 'B1 verified pending final static result'
record_path.write_text(json.dumps(record, indent=2))
