import json
import hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[1]
path = root / 'dual_feg_example_lyap.ipynb'
nb = json.loads(path.read_text(encoding='utf-8'))
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell['source'])
    assert not any(ord(c) < 32 and c not in '\n\t\r' for c in src)
    if cell['cell_type'] == 'markdown':
        assert '\\(' not in src and '\\[' not in src
    for out in cell.get('outputs', []):
        assert out['output_type'] != 'error'
        if 'text' in out:
            print(i, ''.join(out['text']))
        if 'data' in out:
            print(i, 'output MIME types:', list(out['data']))
items = ['title, problem description, and the algorithm update equations in LaTeX', 'proof statement placeholder, to be filled with the final theorem and proof outline in Block 5', 'imports', 'function/operator definitions', 'make_ctx_dual_feg and get_pep_setup', 'numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate', 'dense and relaxed proof solves', 'lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)', 'partial-sum Lyapunov construction and rank profile', 'special-vector identification', 'coefficient extraction and closed-form V_k', 'symbolic step, base, and boundary identities']
indices = ['0', '1', '2,3', '4', '5', '6,7', '8', '9', '10', '11', '12', '13']
lines = [f'Notebook: {path.name}', 'Last reviewed block: B1', 'SHA-256: ' + hashlib.sha256(path.read_bytes()).hexdigest(), 'Presentation policy: evaluation-ancillary-v1; source delimiters checked; no rendering or image inspection performed.', '', '| Item | Status | Cells (zero-based) | Evidence |', '|---|---|---|---|']
for i, (item, ids) in enumerate(zip(items, indices), 1):
    done = i in (1, 3, 4, 5, 6)
    evidence = 'Source content inspected; clean-kernel execution passed.' if done else 'Later-block obligation pending.'
    if i == 6:
        evidence = 'Seven printed values and statuses; matplotlib image/png output present; max rate discrepancy for N>=2 printed. Rendering omitted under evaluation override.'
    lines.append(f'| {i}. {item} | {"verified" if done else "pending"} | {ids} | {evidence} |')
(root / 'supplementary/dual_feg_example_lyap_checklist.md').write_text('\n'.join(lines))
record = {'current_block':'B1', 'access_control':'instruction_only', 'prohibited_content_observed':False, 'audit_limit':'No exhaustive filesystem-read tracing. Tool outputs and adapter manifests retained.', 'approved_direct_reads':['dispatch.md','input.md','worker-protocol.md','settings.json','clean-room.md','plugins/pepflow-workflows/optional/with-clean-room/references/tool-recovery.md','plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py','plugins/pepflow-workflows/references/output-layout.md','pepflow/operator.py','pepflow/pep.py','pepflow/solver.py','pepflow/vector.py','pepflow/pep_runner.py','pepflow/__init__.py'] + [f'plugins/pepflow-workflows/skills/{s}/SKILL.md' for s in ['pep-implement','pep-full-proof','lyap-define','lyap-vectors','lyap-closed-form']] + ['plugins/pepflow-workflows/skills/pep-implement/references/workflow.md'], 'generated_sources_and_execution':['dual_feg_setup.py','supplementary/runtime.py','supplementary/helpers/runtime.py','supplementary/run_b1.py','supplementary/build_b1_notebook.py','supplementary/review_b1.py','dual_feg_example_lyap.ipynb'], 'commands':'Actual tool logs plus supplementary run scripts, adapter args and evidence JSON preserve commands.', 'incidents':[{'evidence':'b1-static-001.json','classification':'operational_error','reason':'Windows path failure copying broad supplementary helper root','repair':'Narrow generated helper directory supplementary/helpers; preflight-002 passed'},{'evidence':'tool output for b1-static-002 invocation','classification':'operational_error','reason':'PowerShell JSON array handling produced incorrect argv before adapter ran','repair':'Build argv from frozen settings as in prior successful invocation'},{'evidence':'b1-static-003.json','classification':'source_diagnostics','reason':'Ruff E402 and unused bootstrap import','repair':'Separate bootstrap and imports notebook cells; assert runtime root'}]}
(root / 'supplementary/b1-access-record.json').write_text(json.dumps(record, indent=2))
