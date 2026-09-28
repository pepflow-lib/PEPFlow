import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'pgm_example_lyap.ipynb'
nb=json.loads(path.read_text())
for c in nb['cells']:
    source=''.join(c['source'])
    if c['cell_type']=='code':
        assert c['execution_count'] is not None
        assert all(o['output_type']!='error' for o in c['outputs'])
    else:
        assert source.count('$')%2==0
        assert not any(x in source for x in ['\\(','\\)','\\[','\\]','\x0c','\r'])
for i in (15,17,19):
    assert any('text/latex' in o.get('data',{}) for o in nb['cells'][i]['outputs'])
check=root/'supplementary/pgm_example_lyap_checklist.md'
lines=check.read_text().splitlines()
lines=[('Last reviewed block: B2' if line.startswith('Last reviewed block:') else
        'SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest() if line.startswith('SHA-256:') else line) for line in lines]
for i,line in enumerate(lines):
    if line.startswith('| 7 |'):
        lines[i]='| 7 | dense and relaxed proof solves | verified | 11,13 | Both CLARABEL solves optimal; sparse star/consecutive support preserves bound within 2.34e-10; summaries cover f and g. |'
    if line.startswith('| 8 |'):
        lines[i]='| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 13,15,17,19,21,22 | Complete inventory, hash/coordinates, every multiplier, labeled candidate/LDL/residual matrices; identity max 1.62e-8; reconstruction 1.11e-16. Candidate formulas and unresolved analytic obligations explicit. |'
    for number,cell in [(9,23),(10,24),(11,25),(12,26)]:
        if line.startswith(f'| {number} |'):
            parts=lines[i].split('|')
            parts[4]=f' {cell} '
            lines[i]='|'.join(parts)
check.write_text('\n'.join(lines)+'\n')
record=dict(block='B2',access_control='instruction_only',consulted_sources=[
'approved/plugins/pepflow-workflows/skills/pep-full-proof/references/workflow.md',
*[f'approved/pepflow/{name}.py' for name in ['pep_result','lyapunov_utils','constraint','function','expression_manager','ipython_utils']],
'Own generated B1/B2 artifacts and static-check evidence'],
commands='Tool transcript; executed scripts and adapter JSON contain exact operations.',
incidents=[{'kind':'source_diagnostic','reason':'Unused and duplicate imports in generated certificate capture helper','repair':'Removed imports, reran both whole solves and all notebook verification to refresh coherent source hashes.'},
{'kind':'operational','reason':'PowerShell script execution policy blocked convenience wrapper','repair':'Used the existing authorized direct command; did not alter execution policy.'}],
prohibited_content_observed=False,audit_limit='Instruction-only restrictions; no exhaustive filesystem trace.',
notebook_execution='Fresh private pinned kernel; no errors',presentation_policy='evaluation-ancillary-v1',visual_inspection=False,
unresolved=['Arbitrary-horizon analytic certificate and Lyapunov proof remain later-block obligations'])
(root/'supplementary/b2-access-record.json').write_text(json.dumps(record,indent=2))
print('B2 evidence inspected; checklist and access record updated.')
