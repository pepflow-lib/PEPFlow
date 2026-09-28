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
    assert all(o['output_type'] != 'error' for o in cell.get('outputs', []))
    if 11 <= i <= 17:
        print('Cell', i, source.splitlines()[0], 'outputs', [o['output_type'] for o in cell.get('outputs', [])])
        for output in cell.get('outputs', []):
            if output['output_type'] == 'stream':
                print(''.join(output['text']))
checklist = root / 'supplementary/feg_example_lyap_checklist.md'
text = checklist.read_text().replace('Last reviewed block: B1', 'Last reviewed block: B2')
lines = text.splitlines()
for i, line in enumerate(lines):
    if line.startswith('SHA-256:'):
        lines[i] = 'SHA-256: ' + hashlib.sha256(path.read_bytes()).hexdigest()
    elif line.startswith('| 7.'):
        lines[i] = line.replace('| pending | Later-block requirement |', '| verified | 11,12: actual dense/selected solver evidence, support construction and preserved objective |')
    elif line.startswith('| 8.'):
        lines[i] = line.replace('| pending | Later-block requirement |', '| verified | 13-17: complete identity replay, labeled LDL factors/residual matrices, sign/PSD checks, failed candidate comparisons explicitly unresolved |')
checklist.write_text('\n'.join(lines))
p = root / 'supplementary/preflight-access-record.json'
r = json.loads(p.read_text(encoding='utf-8-sig'))
r['B2_reads'] = ['Own B1 state, setup, B2 generated sources, dense/selected states, notebook outputs', 'approved pep-full-proof/references/workflow.md', 'approved pepflow/pep_result.py', 'approved pepflow/lyapunov_utils.py', 'approved pepflow/utils.py', 'approved pepflow/expression_manager.py', 'approved pepflow/ipython_utils.py', 'Approved framework files hashed from exact allowlist; no target reference retrieval']
r['B2_commands'] = ['b2_dense.py', 'b2_selected.py and recorded retries', 'update_b2_notebook.py fresh kernel and retry', 'adapter b2-static-001.json and b2-static-002.json', 'finish_b2.py']
r['incidents'] += [{'kind':'source_diagnostics','evidence':'b2-static-001.json','repair':'Explicit SymPy parameter values, checked nonmissing dual values, and named max_abs function; fresh coherent solve and replay'}, {'kind':'operational','evidence':'b2-selected-003-console.txt','repair':'Avoided shadowing objective by loop variable; fresh complete solve retained in b2-selected-004-console.txt'}]
r['status'] = 'B2 numerical certificate and notebook complete; final static check pending'
p.write_text(json.dumps(r, indent=2))
