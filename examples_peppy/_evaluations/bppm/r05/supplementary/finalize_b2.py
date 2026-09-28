"""Record completed B2 evidence and its operational handoff."""
import hashlib
import json
from pathlib import Path
import re
import nbformat as nbf

root=Path(__file__).resolve().parents[1]
static=json.loads((root/'supplementary/b2-static-002.json').read_text())
assert static['status']=='passed'
nbpath=root/'bppm_example_lyap.ipynb'
nb=nbf.read(nbpath,as_version=4)
for cell in nb.cells:
    if cell.cell_type=='code':
        assert cell.execution_count is not None
        assert not any(o.output_type=='error' for o in cell.outputs)
for index in (16,18,21):
    outputs=nb.cells[index].outputs
    assert any(o.output_type in ('display_data','execute_result') for o in outputs)
checkpath=root/'supplementary/bppm_example_lyap_checklist.md'
check=checkpath.read_text()
check=check.replace('Last reviewed block: B1','Last reviewed block: B2')
check=re.sub(r'SHA-256: [0-9a-f]+','SHA-256: '+hashlib.sha256(nbpath.read_bytes()).hexdigest(),check)
lines=check.splitlines()
for i,line in enumerate(lines):
    if line.startswith('| 7 |'):
        lines[i]='| 7 | dense and relaxed proof solves | verified | 12,13,14 | Complete saved solve provenance, active groups and basis inspected; sparse bound preserved within 3.2e-10. |'
    elif line.startswith('| 8 |'):
        lines[i]='| 8 | lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status) | verified | 15–22 | Candidate matrices and residual matrices emitted; complete numerical identity and factor reconstruction pass; fixed-N exact candidate identity passes. Global analytic status explicitly unresolved. |'
    elif line.startswith('| 9 |'):
        lines[i]='| 9 | partial-sum Lyapunov construction and rank profile | pending | 23 | B3 |'
    elif line.startswith('| 10 |'):
        lines[i]='| 10 | special-vector identification | pending | 24 | B4 |'
    elif line.startswith('| 11 |'):
        lines[i]='| 11 | coefficient extraction and closed-form V_k | pending | 25 | B4/B5 |'
    elif line.startswith('| 12 |'):
        lines[i]='| 12 | symbolic step, base, and boundary identities | pending | 25 | B5 |'
checkpath.write_text('\n'.join(lines)+'\n')
statepath=root/'state/bppm_b2.json'
state=json.loads(statepath.read_text())
state.update(completion_status='complete', static_evidence='supplementary/b2-static-002.json',
             execution_evidence='supplementary/b2-execution.json',fixed_horizon_candidate_exact_identity=True)
statepath.write_text(json.dumps(state,indent=2))
audit={'current_block':'B2','access_control':'instruction_only','prior_records':['preflight-access-record.json','b1-access-record.json'],
       'new_approved_reads':['plugins/pepflow-workflows/skills/pep-full-proof/references/workflow.md','pepflow/pep_result.py','pepflow/solver.py'],
       'framework_source_reads':'Exact allowlisted pepflow files were hashed; paths/hashes in certificate_provenance.source_hashes.',
       'generated_reads':['state/bppm_b1.json','state/bppm_dense.json','state/bppm_b2.json','bppm_example_lyap.ipynb','supplementary/helpers/certificate_tools.py','supplementary/b2-static-001.json','supplementary/b2-static-002.json','supplementary/bppm_example_lyap_checklist.md'],
       'commands':['python -I -B supplementary/run_b2.py','python -I -B supplementary/relax_b2.py (twice: replacement after helper type repair)','python -I -B supplementary/author_b2.py (twice)','python -I -B supplementary/execute_notebook.py B2 (twice)','approved check_static adapter twice; exact commands recorded in evidence/tool transcript','python -I -B supplementary/finalize_b2.py'],
       'incidents':[{'classification':'source_type_diagnostic','evidence':'b2-static-001.json','repair':'Explicit non-null branch before float conversion; no suppression or source substitution. Replaced and rechecked full certificate after helper source changed.'}],
       'prohibited_content_observed':False,'audit_limit':'Instruction-only access; no exhaustive OS read trace.',
       'certificate_id':state['certificate_id'],'numerical_certificate_verified':True,'analytic_full_pep_verified':False,'lyapunov_proof_verified':False}
(root/'supplementary/b2-access-record.json').write_text(json.dumps(audit,indent=2))
handoff={'current_block':'B2','completion_status':'complete','next_block':'B3',
         'entry_exit_reason':'B1 handoff; dense and sparse solves, complete certificate checks, initial formula search, notebook/static verification completed',
         'operational_status':'awaiting_same_session_continuation','next_block_started':False,
         'deadline_utc':'2026-09-24T00:34:49.219272+00:00'}
(root/'supplementary/b2-handoff.json').write_text(json.dumps(handoff,indent=2))
print(json.dumps(handoff))
