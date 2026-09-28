import json
import hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'bppm_example_lyap.ipynb'
nb=json.loads(p.read_text())
for i,c in enumerate(nb['cells']):
    s=''.join(c['source'])
    assert not any(x in s for x in ('\x0c','\x08','\r'))
    if c['cell_type']=='markdown':
        assert '\\(' not in s and '\\[' not in s
    else:
        assert c['execution_count'] is not None
        assert all(o['output_type']!='error' for o in c['outputs'])
    print(i,c['cell_type'],s.splitlines()[0], [o.get('output_type') for o in c.get('outputs',[])])
q=root/'supplementary/bppm_example_lyap_checklist.md'
lines=q.read_text(encoding='utf-8-sig').splitlines()
for i,line in enumerate(lines):
    if line.startswith('Last reviewed block:'): lines[i]='Last reviewed block: B2'
    if line.startswith('SHA-256:'): lines[i]='SHA-256: '+hashlib.sha256(p.read_bytes()).hexdigest()
    if line.startswith('|7|'): lines[i]='|7|dense and relaxed proof solves|verified|10,11,12|Dense/selected coherent solves, all active groups, and support construction inspected; gap 4.66e-10.|'
    if line.startswith('|8|'): lines[i]='|8|lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)|verified|13,14,15,16|All-coordinate identity, eigendecomposition and signs rechecked; candidates displayed and analytic status false.|'
    if line.startswith('|9|'): lines[i]=line.replace('|12|','|17|')
    if line.startswith('|10|'): lines[i]=line.replace('|13|','|18|')
    if line.startswith('|11|'): lines[i]=line.replace('|13,14|','|18,19|')
    if line.startswith('|12|'): lines[i]=line.replace('|14|','|19|')
q.write_text('\n'.join(lines))
record={'phase':'B2','access_control':'instruction_only','approved_sources':['plugins/pepflow-workflows/skills/pep-full-proof/references/workflow.md','pepflow/pep_result.py','pepflow/ipython_utils.py','pepflow/pep_context.py'],'own_sources':'B1 state/setup/notebook, B2 generated scripts, solver state, and tool evidence. Generic approved package source hashes and actual import route recorded in selected certificate.','incidents':[{'classification':'operational_error','reason':'First shell call had misspelled attempt cwd; process creation rejected, no command executed.'},{'classification':'source_diagnostics','evidence':'b2-static-001.json','repair':'Removed notebook module docstring before imports and duplicate setup import; explicit None branch for multiplier capture. Required checks repeated.'}],'prohibited_content_observed':False,'audit_limit':'Instruction-only isolation, not exhaustive filesystem tracing.'}
(root/'supplementary/b2-consulted-sources.json').write_text(json.dumps(record,indent=2))
