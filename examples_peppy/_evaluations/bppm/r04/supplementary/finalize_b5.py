import ast
import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'bppm_example_lyap.ipynb'
nb=json.loads(path.read_text())
streams=[]
for index,cell in enumerate(nb['cells']):
    source=''.join(cell['source'])
    assert not any(c in source for c in ('\x0c','\x08','\r'))
    if cell['cell_type']=='markdown':
        assert '\\(' not in source and '\\[' not in source
        assert source.count('$$')%2==0
    else:
        assert cell['execution_count'] is not None
        assert all(o['output_type']!='error' for o in cell['outputs'])
        for output in cell['outputs']:
            if output['output_type']=='stream':
                streams.append(''.join(output.get('text',[])))
    print(index,cell['cell_type'],source.splitlines()[0])
text=''.join(streams)
proof_line=next(line for line in text.splitlines() if line.startswith('Exact proof checks:'))
checks=ast.literal_eval(proof_line.split(':',1)[1].strip())
assert all(checks.values()) and set(checks)=={'step','base','boundary','signs','domain','normalization'}
for name in ('Step','Coefficient structure','Initial zero','Base first step','Initial normalization','Boundary','Metric domination'):
    assert name+' constant residual: 0' in text
assert any('image/png' in o.get('data',{}) for c in nb['cells'] for o in c.get('outputs',[]))
static=json.loads((root/'supplementary/b5-static-002.json').read_text())
assert static['status']=='passed'
b4=json.loads((root/'state/bppm_b4.json').read_text())
evidence=json.loads((root/'supplementary/b5_exact_checks.json').read_text())
assert evidence['proof_checks']==checks
structure=json.loads(json.dumps(b4['expression_structure']).replace('candidate ',''))
state={**b4,'analytic_full_pep_verified':False,'lyapunov_proof_verified':True,
 'proof_checks':checks,'proof_arguments':evidence['proof_arguments'],
 'lyapunov_formula':'V_k=(D_h(x_star,x_k)-D_h(x_star,x_0))/(alpha*N)+(k/N)*(f(x_k)-f(x_star)), 0<=k<=N; V_0=0',
 'conventional_lyapunov_formula':'Phi_k=alpha*k*(f(x_k)-f(x_star))+D_h(x_star,x_k)',
 'discovery_expression_structure':b4['expression_structure'],'expression_structure':structure,
 'coefficient_formula_status':'verified','unresolved_coefficients':[],
 'local_multiplier_code':'def local_weights(k,N,alpha):\n    return [1/N,k/N,(k+1)/(alpha*N),k/(alpha*N)]\n',
 'exact_verification':evidence['exact_residuals'],
 'symbolic_source':{name:(root/'supplementary'/name).read_text(encoding='utf-8-sig') for name in ('b5_initialize.py','b5_step.py','b5_base.py','b5_boundary.py','b5_signs.py')},
 'final_validation':{'static_evidence':'supplementary/b5-static-002.json','fresh_kernel_execution':'supplementary/b5_nbconvert.console.txt','execution_method':'python -I -B, nbconvert --to notebook --execute --inplace, private bppm-attempt kernel','presentation_policy':'evaluation-ancillary-v1','rendered_visual_review':'not performed under evaluation override','notebook_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},
 'run_status':'completed','completed_blocks':['B1','B2','B3','B4','B5'],'unresolved_mandatory_work':[],
 'optional_unverified_work':['Separate global analytic full-PEP lambda/S proof not asserted; numerical full-PEP certificate and exact local Lyapunov proof are separate.']}
assert set(structure)=={'quadratic_convention','interior','initial','terminal','function_terms','constant_terms'}
(root/'state/bppm_b5.json').write_text(json.dumps(state,indent=2,allow_nan=False))
items=[
('title, problem description, and the algorithm update equations in LaTeX','0','All assumptions, Bregman definition, exact updates and metric inspected.'),
('proof statement placeholder, to be filled with the final theorem and proof outline in Block 5','1,2,3','Placeholder replaced by separate proof heading, self-contained theorem and detailed outline with full V_k, all residuals and bound.'),
('imports','4,5,13,22,26,38','Pinned approved source paths and private runtime; final fresh kernel execution passed.'),
('function/operator definitions','7','Both convex function families, alpha and R definitions inspected.'),
('make_ctx_bppm and get_pep_setup','8','Actual proximal recurrence, initial radius R, and metric visible and executable.'),
('numerical evidence, including a plot comparing the PEP values against the discovered or conjectured rate','10','Seven optimal CLARABEL values, printed comparison and embedded PNG plot verified as output; no image inspection under policy.'),
('dense and relaxed proof solves','12,13,14,19,20','Complete coherent N4 and N6 solve provenance, active groups, relaxation and preserved-optimum output inspected.'),
('lambda and S verification (closed-form when available, otherwise numerical with explicit analytic status)','15,16,17,18','Initial formula search, labeled candidates/actual S, full eigendecomposition reconstruction and all-coordinate numerical certificate checks present; global analytic status explicitly false.'),
('partial-sum Lyapunov construction and rank profile','21,22,23','Actual construction loops, all certificate/grouping checks, singular-value credibility, and rank4 at N4/N6 with fixed exclusions (1,1) executed.'),
('special-vector identification','24,25,26,27,28,29,30,31','Actual deduplicated candidate scan, column filtering and sparse search outputs for every nonzero index; boundary independence verified.'),
('coefficient extraction and closed-form V_k','32,33,34,35,36,37,41','All-index labeled coefficient matrices, comparisons, full-expression reconstructions and exact coefficient-structure identity; function gaps and zero offset retained.'),
('symbolic step, base, and boundary identities','38,39,40,41,42,43,44,45,46,47,48,49,50','Separate auxiliary PEPFlow contexts and visible LHS/RHS/difference calculations; all Gram/function/offset residuals exactly zero; sign, domain, N1, R0 and normalization arguments inspected.')]
lines=['Notebook: bppm_example_lyap.ipynb','Last reviewed block: B5','SHA-256: '+state['final_validation']['notebook_sha256'],'Presentation policy: evaluation-ancillary-v1. Source, outputs, delimiters and execution inspected. No rendering, browser, or image inspection performed; no rendered-review claim.','','|Item|Requirement|Status|Cell indices|Evidence|','|---|---|---|---|---|']
lines += [f'|{i}|{requirement}|verified|{indices}|{details}|' for i,(requirement,indices,details) in enumerate(items,1)]
(root/'supplementary/bppm_example_lyap_checklist.md').write_text('\n'.join(lines))
record={'phase':'B5','approved_sources':['plugins/pepflow-workflows/skills/lyap-closed-form/references/workflow.md','pepflow/expression_manager.py (definition-name scan)','pepflow/parameter.py (definition-name scan)'],'own_sources':'B4 state and exact reconstruction scripts, B5 symbolic initialization/step/base/boundary/sign scripts, final notebook authoring/repair/execution/audit scripts and their generated output.','commands':'All Python used pinned interpreter -I -B; actual tool transcript and supplementary console/static evidence retained. Final notebook executed with nbconvert --execute.',
 'incidents':[{'classification':'source_diagnostic','evidence':'b5-static-001.json','repair':'Explicit typing cast for symbolic parameter mapping supported by ExpressionManager sympy_mode; no runtime expression change, gate suppression, or frozen source edit. b5-static-002 passed.'}],
 'access_control':'instruction_only','prohibited_sources_used_or_encountered':False,'integrity_exceptions':[],
 'audit_limit':'Instruction-only access restrictions; no exhaustive OS filesystem read tracing, and no claim about training exposure. Available tool transcript and source records support only observed accesses.'}
(root/'supplementary/b5-consulted-sources.json').write_text(json.dumps(record,indent=2))
closure={'current_block':'B5','completion_status':'complete','next_block':None,'entry_exit_reason':'Exact proof, required static checks, fresh-kernel nbconvert execution, and final notebook audit completed.','operational_status':'stopped_completed','run_status':'completed','completed_blocks':['B1','B2','B3','B4','B5'],'unresolved_mandatory_work':[],'optional_unverified_work':state['optional_unverified_work'],'deadline_utc':'2026-09-23T22:42:59.899868+00:00','access_control':'instruction_only','access_status':'no_prohibited_content_observed','notebook':'bppm_example_lyap.ipynb','state':'state/bppm_b5.json'}
(root/'supplementary/final-handoff.json').write_text(json.dumps(closure,indent=2))
print('B5 complete: state, notebook audit and operational closure saved.')

