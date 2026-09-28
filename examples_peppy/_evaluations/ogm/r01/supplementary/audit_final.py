import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
path=root/'ogm_example_lyap.ipynb'
nb=json.loads(path.read_text(encoding='utf-8'))
state=json.loads((root/'state/ogm_b5.json').read_text())
digest=hashlib.sha256(path.read_bytes()).hexdigest()
assert digest==state['notebook_sha256']
assert all((root/'state'/f'ogm_b{j}.json').is_file() for j in range(1,6))
assert any('image/png' in o.get('data',{}) for o in nb['cells'][11]['outputs'])
assert sum(o['output_type']=='display_data' for o in nb['cells'][17]['outputs'])>=4
assert 'find_basis_with_sparsest_coefficients' in ''.join(nb['cells'][30]['source'])
assert all(cell['execution_count'] is not None for cell in nb['cells'] if cell['cell_type']=='code')
rows=[
('title, problem description, and the algorithm update equations in LaTeX','0','Assumptions, exact algorithm, initial condition, metric and special terminal theta recurrence inspected.'),
('proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','1-3','Placeholder replaced by separate heading, theorem with full V formula and terminal case, and self-contained proof with every local residual and sign implication.'),
('imports','4-5','Pinned runtime and approved framework origin printed; private cache and numerical thread configuration retained.'),
('function/operator definitions','6-7','Convex L-smooth function and L,R parameters visibly defined.'),
('make_ctx_ogm and get_pep_setup','8-9','Visible context builder, every update/tag, stationary point, R-squared constraint, and objective-gap metric.'),
('numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','10-12','Seven actual optimal CLARABEL sweep rows and candidate comparison printed; PNG plot embedded. Plot data inspected without viewing an image.'),
('dense and relaxed proof solves','13-14','Actual dense/sparse acquisition evidence preserved, active pairs summarized, matching bound checked; one coherent sparse certificate used.'),
('lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','15-17','All-coordinate certificate replay, scalar signs/PSD, sparse-lambda candidate matrix, true S and reconstruction displays; original formula search and separate global analytic status retained. Independent N=6 replay included.'),
('partial-sum Lyapunov construction and rank profile','18-23','Visible extraction, S pieces, lyap/partial_sum loop, rank printouts and coverage checks. Independent N=4,6 samples confirm rank 3 under fixed (1,1) exclusions and threshold 1e-4.'),
('special-vector identification','24-32','Rich deduplicated candidate scan and actual sparse-basis search executed for each nonzero-rank index; selected pattern and endpoint exception stated.'),
('coefficient extraction and closed-form V_k','33-42','Labeled numeric and candidate matrices, every-index independence/quadratic/function/offset reconstruction, coefficient derivation and complete general-L formula inspected; exact verification below establishes it.'),
('symbolic step, base, and boundary identities','43-57','Separate native PEPFlow contexts and LHS/RHS/diff calculations; all Gram/function/offset components exactly zero for ordinary/base/terminal/metric/N=1/normalization. Equation cells immediately follow verification headings; signs/domain/telescoping complete.')]
lines=['Notebook: ogm_example_lyap.ipynb','Last reviewed block: B5','SHA-256: '+digest,'Presentation policy: evaluation-ancillary-v1. No browser, rendered visual review, screenshot, or image inspection performed. Markdown delimiters/escapes, actual source, printed output and embedded output types inspected. This override does not waive mathematical, static, or execution gates.','Static evidence: supplementary/b5-static-001.json','Clean-kernel execution: supplementary/b5-nbconvert-evidence.json; actual nbconvert --execute exit 0.','Final Markdown-only cleanup preserved executable source hash: supplementary/b5-final-markdown-evidence.json.','','| Item | Status | Zero-based cell indices | Evidence |','|---|---|---|---|']
for i,(item,cells,evidence) in enumerate(rows,1):
    lines.append(f'| {i}. {item} | verified | {cells} | {evidence} |')
(root/'supplementary/ogm_example_lyap_checklist.md').write_text('\n'.join(lines),encoding='utf-8')
record=dict(attempt_id='ogm_r01',current_block='B5',completion_status='complete',next_block=None,entry_exit_reason='All analytic identities, signs, domain, endpoint and normalization obligations completed; required final static and nbconvert execution passed; all twelve notebook requirements inspected.',run_status='success',operational_status='closed',completed_blocks=['B1','B2','B3','B4','B5'],unresolved_required_work=[],numerical_certificate_verified=True,analytic_full_pep_verified=False,lyapunov_proof_verified=True,analytic_full_pep_note='Separate global table proof was not required and is not claimed.',notebook='ogm_example_lyap.ipynb',notebook_sha256=digest,state='state/ogm_b5.json',checks=['supplementary/b5-symbolic-output.txt','supplementary/b5-static-001.json','supplementary/b5-nbconvert-evidence.json','supplementary/b5-final-markdown-evidence.json'],access_control='instruction_only',prohibited_sources_used_or_encountered=False,access_declaration='No prohibited source use or exposure observed in this attempt; exact approved files and own generated artifacts only.',observability_limits='No exhaustive OS read tracing; declaration and tool logs are not OS enforcement or proof about model training.',new_consulted_sources=['supplementary/approved/plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md','Own B4 state, native symbolic scripts, theorem/proof text, final notebook and validation records'],consulted_source_record_chain=['supplementary/preflight-access.json','supplementary/b1-handoff.json','supplementary/b2-handoff.json','supplementary/b3-handoff-to-b2.json','supplementary/b2-N6-handoff.json','supplementary/b3-handoff.json','supplementary/b4-handoff.json'],command_records='Actual tool transcript and per-command stdout/evidence files preserve read/execute history; adapter manifests enumerate staged approved sources and pinned tools. No external resources consulted.',integrity_exceptions=[],operational_repairs='Earlier encoding, path-length, notebook writer, import and static typing failures were repaired only in attempt-owned files; preserved in earlier handoff/evidence records.',presentation_policy='evaluation-ancillary-v1',token_usage=None,finished_utc=state['finished_utc'],original_deadline_utc='2026-09-23T16:12:13.416403+00:00')
(root/'supplementary/b5-handoff.json').write_text(json.dumps(record,indent=2))
print('Final checklist: all twelve items verified under frozen presentation policy.')
print('Final operational status: success; required unresolved work: none.')
