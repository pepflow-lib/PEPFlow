"""Audit required final notebook evidence and save the analytic proof state."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import nbformat as nbf

root=Path(__file__).resolve().parents[1]
nbpath=root/'bppm_example_lyap.ipynb'
nb=nbf.read(nbpath,as_version=4)
static=json.loads((root/'supplementary/b5-static-002.json').read_text())
execution=json.loads((root/'supplementary/b5-nbconvert-execution.json').read_text())
assert static['status']=='passed' and execution['returncode']==0 and execution['clean_kernel']
digest=hashlib.sha256(nbpath.read_bytes()).hexdigest()
assert digest==execution['notebook_sha256']
for cell in nb.cells:
    if cell.cell_type=='code':
        assert cell.execution_count is not None
        assert not any(o.output_type=='error' for o in cell.outputs)
    else:
        assert not any(c in cell.source for c in ('\\(','\\)','\\[','\\]','\x0c','\r'))
stream='\n'.join(o.text for c in nb.cells if c.cell_type=='code' for o in c.outputs if o.output_type=='stream')
exact_names=('Step','Closed-form coefficient structure','Initial step','Initial value V_0','Initial radius normalization','Terminal bound')
assert all(name+': exact Gram, function, and offset residuals are zero.' in stream for name in exact_names)
assert 'All local weights are nonnegative' in stream
assert 'N=1 uses the separate initial-step identity' in stream
assert nb.cells[1].source=='## Proof Statement'
assert nb.cells[2].source.startswith('### Theorem') and 'V_{k}' in nb.cells[2].source
assert nb.cells[3].source.startswith('### Proof outline') and 'r^h' in nb.cells[3].source
for heading in ('## Symbolic Step Recursion Verification','## Base Case and Boundary Symbolic Verification','### Boundary Identity Symbolic Verification'):
    index=next(i for i,c in enumerate(nb.cells) if c.source==heading)
    assert nb.cells[index+1].cell_type=='markdown' and 'LHS' in nb.cells[index+1].source
    assert nb.cells[index+2].cell_type=='code'
    assert sum(o.output_type in ('display_data','execute_result') for o in nb.cells[index+2].outputs)>=2
assert any('image/png' in o.get('data',{}) for c in nb.cells if c.cell_type=='code' for o in c.outputs)
assert 'sparse basis:' in stream and 'zero coefficients:' in stream
assert 'Selected numerical S (retained, not rounded to zero):' in stream
assert 'Closed-form coefficient candidate at k =' in stream
b4=json.loads((root/'state/bppm_b4.json').read_text())
checks={name:True for name in ('step','base','boundary','signs','domain','normalization')}
formula='V_k = (alpha*k*(f(x_k)-f(x_star)) + D_h(x_star,x_k) - D_h(x_star,x_0))/(alpha*N), 0<=k<=N'
arguments={
    'step':'Exact symbolic PEPFlow identity in notebook cell 55; four nonpositive convex interpolation residuals with weights 1/N, k/N, (k+1)/(alpha*N), k/(alpha*N).',
    'base':'Separate actual initial proximal-step context in cell 58 verifies V_1-V_0=r_f(star,1)/N+r_h(1,0)/(alpha*N), V_0=0 and E_0-R=D_0-R.',
    'boundary':'Cell 61 verifies gap_N-R/(alpha*N)-V_N=(D_0-R+r_h(star,N))/(alpha*N); both numerator terms are nonpositive.',
    'signs':'Convexity gives all interpolation residuals <=0, including r_h(star,N)=-D_h(star,x_N); initial assumption gives D_0-R<=0. All local multipliers are nonnegative.',
    'domain':'Real finite-dimensional Euclidean space; closed proper convex differentiable f,h; exact well-defined proximal updates; alpha>0; R>=0; integer N>=1; 0<=k<N. No strong-convexity or Euclidean-radius assumption.',
    'normalization':'V_N <= V_0=0 and gap_N-R/(alpha*N) <= V_N. Radius is R, not R squared. N=1 is covered by the separate base and terminal identities.'}
local_code='''def local_multipliers(k, N, alpha):
    return {"f_star_next": 1/N, "f_current_next": k/N,
            "h_next_current": (k+1)/(alpha*N), "h_current_next": k/(alpha*N)}
'''
incident=json.loads((root/'supplementary/b5-write-incident.json').read_text())
state={**b4,'proof_checks':checks,'proof_arguments':arguments,'lyapunov_formula':formula,
       'discovery_expression_structure':b4['expression_structure'],'expression_structure':b4['expression_structure'],
       'coefficient_formula_status':'verified','local_multiplier_code':local_code,'unresolved_coefficients':[],
       'remaining_unknowns':[],'numerical_certificate_verified':True,'analytic_full_pep_verified':False,
       'lyapunov_proof_verified':True,'require_analytic_full_pep':False,
       'analytic_full_pep_status':'Not independently established; global candidate formulas retained as discovery evidence. This is not required for the completed local Lyapunov proof.',
       'proof_source_files':[f'supplementary/b5_{name}.py' for name in ('symbolic_common','step','base','boundary')],
       'exact_identity_evidence':{name:'Exact Gram, function, offset zeros in final executed notebook' for name in exact_names},
       'completion_status':'complete','run_status':'completed','unresolved_required_work':[],
       'static_evidence':'supplementary/b5-static-002.json','execution_evidence':'supplementary/b5-nbconvert-execution.json',
       'notebook_sha256':digest,'presentation_policy':'evaluation-ancillary-v1','rendered_review':'omitted_by_evaluation_policy',
       'integrity_exceptions':[incident]}
(root/'state/bppm_b5.json').write_text(json.dumps(state,indent=2))

items=[
('title, problem description, and the algorithm update equations in LaTeX','0','Assumptions, Bregman orientation, update, metric, and unsquared radius inspected.'),
('proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','1-3','Separate Proof Statement, Theorem, and self-contained Proof outline with explicit potential, full decrease equation, signs and terminal normalization.'),
('imports','4,5','Approved source and own helper origin checked; fresh kernel execution.'),
('function/operator definitions','6,7','Convex f and h and parameters visible; no extra curvature assumption.'),
('make_ctx_{ALGO_NAME} and get_pep_setup','8-10','Actual proximal update, tags, initial Bregman condition and terminal metric visible and executed.'),
('numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','11-13','Seven values, inverse-difference pattern, error check and comparison PNG output present. Rendering not inspected under evaluation policy.'),
('dense and relaxed proof solves','14-16,25-26','Complete same-solve provenance, active groups, dense/sparse bound comparison; independent N=6 certificate checks.'),
('lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','17-24','Initial search record, candidate matrices, true S, retained factor reconstruction and all-coordinate numerical residual checks. Independent global analytic status explicitly unverified.'),
('partial-sum Lyapunov construction and rank profile','27-33','Exact executed grouping shown; all terms assigned; PSD boundary piece retained; full-coordinate coverage checked; rank 4 at N=4,6 with fixed exclusions.'),
('special-vector identification','34-42','Actual column-space filter and sparse search, executed at every nonzero index; independent four-vector basis and empty k=0 basis.'),
('coefficient extraction and closed-form V_k','43-50,55','Labeled numerical and candidate coefficient matrices, function coordinates, full-expression reconstruction at every index, and exact symbolic coefficient-structure verification.'),
('symbolic step, base, and boundary identities','51-62','Separate symbolic contexts and visible LHS/RHS/diff; exact Gram/function/offset checks; local signs, domain, N=1, and radius normalization proved.')]
header=f'# Notebook evidence checklist\n\nNotebook: {nbpath.name}\nLast reviewed block: B5\nSHA-256: {digest}\n\nPresentation policy: evaluation-ancillary-v1. Source delimiters, control characters, executable content and saved outputs inspected. No browser, rendering or image inspection performed or claimed.\n\n| Item | Requirement | Status | Cell indices | Evidence |\n|---|---|---|---|---|\n'
(root/'supplementary/bppm_example_lyap_checklist.md').write_text(header+'\n'.join(f'| {i} | {a} | verified | {b} | {c} |' for i,(a,b,c) in enumerate(items,1))+'\n')
audit={'current_block':'B5','access_control':'instruction_only','new_approved_reads':['plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md','pepflow/expression_manager.py'],
       'generated_reads':['state/bppm_b4.json','bppm_example_lyap.ipynb','supplementary/b5_symbolic_common.py','supplementary/b5_step.py','supplementary/b5_base.py','supplementary/b5_boundary.py','supplementary/b5-static-001.json','supplementary/b5-static-002.json','supplementary/b5-nbconvert-execution.json','supplementary/b5-write-incident.json'],
       'commands':['python -I -B supplementary/run_b5.py','python -I -B supplementary/author_b5.py','python -I -B supplementary/update_b5_symbolic.py','approved static adapter twice','python -I -B supplementary/execute_final_nbconvert.py (actual nbconvert argv preserved)','python -I -B supplementary/finalize_b5.py'],
       'incidents':[incident,{'classification':'source typing diagnostic','evidence':'b5-static-001.json','repair':'Generic symbolic substitution wrapper around numeric-only annotated framework API; no framework change or diagnostic suppression.'}],
       'prohibited_content_observed':False,'audit_limit':'Instruction-only restriction; no exhaustive OS read trace; cleaned accidental write outside attempt recorded separately.'}
(root/'supplementary/b5-access-record.json').write_text(json.dumps(audit,indent=2))
closure={'current_block':'B5','completion_status':'complete','next_block':None,'run_status':'completed',
         'entry_exit_reason':'Exact local theorem proof, all required block artifacts, final static checks and fresh-kernel nbconvert execution completed',
         'operational_status':'closed','completed_blocks':['B1','B2','B3','B4','B5'],'unresolved_required_work':[],
         'analytic_full_pep_verified':False,'lyapunov_proof_verified':True,'numerical_certificate_verified':True,
         'closed_utc':datetime.now(timezone.utc).isoformat(),'deadline_utc':'2026-09-24T00:34:49.219272+00:00',
         'integrity_exceptions':['Cleaned accidental empty-file write outside attempt; see b5-write-incident.json.'],
         'access_control':'instruction_only','prohibited_content_observed':False,'token_usage':None,
         'consulted_source_records':['preflight-access-record.json','b1-access-record.json','b2-access-record.json','b3-access-record-001.json','b2-n6-access-record.json','b3-access-record-002.json','b4-access-record.json','b5-access-record.json']}
(root/'supplementary/closure.json').write_text(json.dumps(closure,indent=2))
print(json.dumps(closure))
