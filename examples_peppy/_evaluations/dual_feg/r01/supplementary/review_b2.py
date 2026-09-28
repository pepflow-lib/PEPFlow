import json
import hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'dual_feg_example_lyap.ipynb'
nb=json.loads(path.read_text())
for i,c in enumerate(nb['cells']):
    src=''.join(c['source'])
    if c['cell_type']=='markdown':
        assert '\\(' not in src and '\\[' not in src
        assert not any(ord(x)<32 and x not in '\n\t\r' for x in src)
    for o in c.get('outputs',[]):
        assert o['output_type']!='error'
    print(i,c['cell_type'],len(c.get('outputs',[])),src[:65].replace('\n',' '))
    if i==9:
        for o in c.get('outputs',[]):
            if 'text' in o:
                text=''.join(o['text'])
                for line in text.splitlines():
                    if any(word in line for word in ['Dense bound','Exact candidate','Numerical certificate checks']):
                        print(line)
checklist=root/'supplementary/dual_feg_example_lyap_checklist.md'
lines=checklist.read_text().splitlines()
lines[1]='Last reviewed block: B2'
lines[2]='SHA-256: '+hashlib.sha256(path.read_bytes()).hexdigest()
for i,line in enumerate(lines):
    if line.startswith('| 7.'):
        lines[i]='| 7. dense and relaxed proof solves | verified | 8,9,10 | Both executed solves preserved; support construction and gap 3.061e-9 checked. |'
    if line.startswith('| 8.'):
        lines[i]='| 8. lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 8,9,10 | All groups, LDL factors, candidate lambda/S matrices and labeled residuals present. Gram residual 1.867e-9; exact fixed-N candidate identity true; arbitrary-horizon status explicitly unresolved. |'
    if line.startswith('| 9.'):
        lines[i]=line.replace('| 10 |','| 11 |')
    if line.startswith('| 10.'):
        lines[i]=line.replace('| 11 |','| 12 |')
    if line.startswith('| 11.'):
        lines[i]=line.replace('| 12 |','| 13 |')
    if line.startswith('| 12.'):
        lines[i]=line.replace('| 13 |','| 14 |')
checklist.write_text('\n'.join(lines))
record={'current_block':'B2','access_control':'instruction_only','approved_direct_reads':['plugins/pepflow-workflows/skills/pep-full-proof/references/workflow.md','pepflow/lyapunov_utils.py','pepflow/expression_manager.py','pepflow/pep_context.py','pepflow/pep_result.py','pepflow/solver.py'],'own_generated_inputs':['state/dual_feg_b1.json','state/dual_feg_dense.json','supplementary/b2_sparse_candidate.json'],'scripts':['supplementary/helpers/certificate.py','supplementary/b2_dense.py','supplementary/b2_sparse.py','supplementary/b2_finalize.py','supplementary/b2_certificate_cells.py','supplementary/update_b2_notebook.py','supplementary/review_b2.py'],'incidents':[{'classification':'operational_error','reason':'One tool invocation rejected before execution due to mistyped own cwd; corrected to authorized attempt path.'},{'classification':'static_diagnostics','evidence':'b2-static-001.json','repair':'Removed redundant/unused notebook imports, used SymPy Integer solve parameters and explicit optional-dual guards. Reacquired complete certificates and reran checks.'}],'prohibited_content_observed':False,'audit_limit':'Instruction-only restrictions, no exhaustive OS read tracing. Commands and outputs preserved by actual tools and evidence files.'}
(root/'supplementary/b2-access-record.json').write_text(json.dumps(record,indent=2))
