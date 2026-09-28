import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'pgm_example_lyap.ipynb'
nb = json.loads(path.read_text())
for cell in nb['cells']:
    source = ''.join(cell['source'])
    if cell['cell_type'] == 'markdown':
        assert not any(x in source for x in ('\\(', '\\)', '\\[', '\\]', '\x0c', '\r'))
        assert source.count('$') % 2 == 0
    else:
        assert cell['execution_count'] is not None
        assert all(o['output_type'] != 'error' for o in cell['outputs'])
plot = nb['cells'][9]
assert any('image/png' in o.get('data', {}) for o in plot['outputs'])
text = ''.join(''.join(o.get('text', [])) for o in plot['outputs'])
assert '4.31910757159315e-09' in text
items = [
('title, problem description, and the algorithm update equations in LaTeX','verified','0','Assumptions, metric and proximal update inspected; math delimiters checked.'),
('proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','pending','1','Placeholder retained; B5 owns final theorem.'),
('imports','verified','2,3','Pinned approved source bootstrap and helper imported in fresh kernel.'),
('function/operator definitions','verified','5','Smooth convex f, convex g and h=f+g inspected.'),
('make_ctx_pgm and get_pep_setup','verified','7','Visible executable recursion, composite stationarity, squared R initialization and metric inspected.'),
('numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','verified','9,10','Printed N=1..7 values and saved PNG plot output; max discrepancy 4.31910757159315e-09. No visual inspection under evaluation override.'),
('dense and relaxed proof solves','pending','11','B2.'),
('lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','pending','12','B2.'),
('partial-sum Lyapunov construction and rank profile','pending','13','B3.'),
('special-vector identification','pending','14','B4.'),
('coefficient extraction and closed-form V_k','pending','15','B4/B5.'),
('symbolic step, base, and boundary identities','pending','16','B5.')]
header = '# Notebook evidence checklist\n\nNotebook: pgm_example_lyap.ipynb\nLast reviewed block: B1\nSHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()+'\nPresentation policy: evaluation-ancillary-v1; no rendering or image inspection.\n\n| Item | Requirement | Status | Cell indices | Evidence |\n|---|---|---|---|---|\n'
(root/'supplementary/pgm_example_lyap_checklist.md').write_text(header + '\n'.join(f'| {i} | {a} | {b} | {c} | {d} |' for i,(a,b,c,d) in enumerate(items,1)))
record = {'block':'B1','access_control':'instruction_only','consulted_sources':[
'approved/dispatch.md','approved/input.md','approved/worker-protocol.md','approved/settings.json',
'approved/plugins/pepflow-workflows/skills/pep-implement/SKILL.md','approved/plugins/pepflow-workflows/skills/pep-implement/references/workflow.md','approved/plugins/pepflow-workflows/references/output-layout.md',
*[f'approved/plugins/pepflow-workflows/skills/{s}/SKILL.md' for s in ['pep-full-proof','lyap-define','lyap-vectors','lyap-closed-form']],
*[f'approved/pepflow/{s}.py' for s in ['__init__','function','pep','pep_runner','solver']],
'approved/plugins/pepflow-workflows/optional/with-clean-room/scripts/check_static.py'],
'own_generated_files_consulted':['pgm_setup.py','pgm_example_lyap.ipynb','supplementary/helpers/runtime.py','supplementary/run_b1.py','supplementary/build_b1_notebook.py','supplementary/_sweep_tmp.json','state/pgm_b1.json','supplementary/b1-static-001.json','supplementary/b1-static-002.json'],
'commands':'Actual tool transcript plus adapter commands stored in evidence JSON; generation scripts preserve executed Python source.',
'incidents':[{'kind':'operational_error','evidence':'b1-static-001.json','reason':'Windows path length during broad helper staging','repair':'Narrow helper-root to supplementary/helpers; moved own runtime helper; preflight-002 passed'},
{'kind':'source_diagnostic','evidence':'b1-static-002.json','reason':'Notebook E402 and unused runtime import','repair':'Separate bootstrap/import cells and assert helper root; rerun notebook and static checks'}],
'prohibited_content_observed':False,'audit_limit':'No exhaustive filesystem tracing; declarations limited to actual observed tool evidence.',
'notebook_checks':{'fresh_kernel_execution':True,'math_delimiters':True,'plot_output_present':True,'visual_inspection':False,'presentation_policy':'evaluation-ancillary-v1'}}
(root/'supplementary/b1-access-record.json').write_text(json.dumps(record,indent=2))
print('B1 notebook evidence verified; checklist and access record saved.')
