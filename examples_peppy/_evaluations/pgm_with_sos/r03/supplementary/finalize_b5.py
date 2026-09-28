from pathlib import Path
import json,hashlib,re,datetime
import nbformat
r=Path(__file__).resolve().parents[1]
p=r/'pgm_example_lyap.ipynb'
nb=nbformat.read(p,as_version=4)
errors=[i for i,c in enumerate(nb.cells) if any(o.output_type=='error' for o in c.get('outputs',[]))]
unexecuted=[i for i,c in enumerate(nb.cells) if c.cell_type=='code' and c.execution_count is None]
math_issues=[]
for i,c in enumerate(nb.cells):
 if c.cell_type=='markdown':
  if any(s in c.source for s in ('\\(','\\)','\\[','\\]')): math_issues.append([i,'non-dollar delimiter'])
  if any(ord(v)<32 and v not in '\n\t\r' for v in c.source): math_issues.append([i,'control character'])
  if c.source.count('$$')%2:math_issues.append([i,'odd display delimiters'])
  if re.sub(r'\$\$', '',c.source).count('$')%2:math_issues.append([i,'odd inline delimiters'])
assert not errors and not unexecuted and not math_issues
assert any('image/png' in o.get('data',{}) for o in nb.cells[10].outputs)
for i,label in [(49,'Interior step'),(52,'Base'),(55,'Boundary'),(58,'N=1')]:
 text=''.join(o.get('text','') for o in nb.cells[i].outputs)
 assert label+' Gram residual:' in text and 'offset: 0' in text
 assert any('text/latex' in o.get('data',{}) for o in nb.cells[i].outputs)
assert 'Exact step/base/boundary/N=1 identities verified' in ''.join(o.get('text','') for o in nb.cells[60].outputs)
sha=hashlib.sha256(p.read_bytes()).hexdigest()
b4=json.loads((r/'state/pgm_b4.json').read_text())
structure={
 'quadratic_convention':b4['expression_structure']['quadratic_convention'],
 'interior':{'index_domain':'1 <= k < N','basis_labels':['d0','dk','ak','astar-ak'],'coefficients':[['-L/(4*N)','0','0','0'],['0','L*(N-k)/(2*N-k)**2','-1/(2*(2*N-k))','0'],['0','-1/(2*(2*N-k))','0','0'],['0','0','0','1/(2*L*(2*N-k))']]},
 'initial':{'index_domain':'k=0','basis_labels':[],'coefficients':[],'value':'0'},
 'terminal':{'index_domain':'k=N','basis_labels':['d0'],'coefficients':[['-L/(4*N)']]},
 'function_terms':[{'term':'f(x_k)-f_star','coefficient':'(k+1)/(2*N-k) for 1<=k<N; 1 at k=N; absent at k=0'},{'term':'g(x_k)-g_star','coefficient':'k/(2*N-k) for 1<=k<N; 1 at k=N; absent at k=0'}],
 'constant_terms':[]}
state=dict(b4)
state.update(block='B5',completion_status='complete',run_status='success',numerical_certificate_verified=True,analytic_full_pep_verified=False,lyapunov_proof_verified=True,
 proof_checks={key:True for key in ['step','base','boundary','signs','domain','normalization']},
 proof_arguments={'step':'Notebook cell 49: exact symbolic k,N,L all scalar coordinates zero, 1<=k<=N-2.','base':'Cell 52: separate first update at N>=2; no g(x0) evaluation. Gauge additions uniquely zero in cell 43.','boundary':'Cell 55: exact symbolic N,L terminal identity; cell 58 verifies N=1 separately.','signs':nb.cells[59].source,'domain':'L>0, R>=0, integer N>=1; 2N-i>=N>=1, 2N+1-i>=N+1>0 for 1<=i<=N. For N=2 the interior-step range is empty.','normalization':'V0=0, VN=hN-hstar-L||d0||^2/(4N); each increment<=0. ||d0||^2<=R^2 yields LR^2/(4N). No division by R; R=0 included.'},
 lyapunov_formula=nb.cells[2].source,discovery_expression_structure=b4['expression_structure'],expression_structure=structure,
 coeff_code=(r/'supplementary/helpers/derive_coefficients.py').read_text(),local_multiplier_code=(r/'supplementary/helpers/exact_proof.py').read_text(),coefficient_formula_status='verified',unresolved_coefficients=[],remaining_unknowns=[],
 final_notebook_sha256=sha,static_evidence='supplementary/b5-static-002.json',execution_evidence='supplementary/b5-nbconvert-001.log',presentation_policy='evaluation-ancillary-v1',rendered_verification_performed=False)
(r/'state/pgm_b5.json').write_text(json.dumps(state,indent=2))
old=(r/'supplementary/pgm_example_lyap_checklist.md').read_text()
wordings=[]
for line in old.splitlines():
 if re.match(r'\| \d+ \|',line):wordings.append(line.split('|')[2].strip())
indices=['0','1-3','4-6','7','8','9-11','12-13','14-19','20-25','26-34','35-46','47-60']
evidence=[
 'Algorithm, assumptions and update equations source-inspected.',
 'Self-contained theorem, piecewise potential, all residual/square terms and telescoping proof appear near the top.',
 'Executed imports use own helpers and frozen approved source.',
 'Executed f,g and parameter definitions.',
 'Actual algorithm context and PEP setup code executed.',
 'Seven optimal solves and rate comparison; saved PNG output present (not viewed).',
 'Dense and sparse solve evidence includes coherent owners and labeled slack matrices.',
 'Initial closed-form search retained; numerical lambda/S coordinate checks and decomposition replayed. Global analytic full-PEP status remains false.',
 'Explicit partial-sum construction and transported decomposition; rank4 interior at N4,N6, fixed exclusions(1,1), all-index coverage.',
 'Actual sparse basis search plus candidate scan; adopted basis and every-index endpoint reconstruction executed.',
 '55 exact scalar equations for 24 unknowns; three constant freedoms fixed by base normalization. Exact matrix and function-gap formulas compared at every selected index with labeled displays; closed-form potential stated.',
 'Separate symbolic step/base/boundary/N1 calculations visibly build LHS,RHS,diff. Executed Gram/function/offset residuals all zero. Sign/domain and radius normalization arguments inspected.'
]
lines=['# Notebook evidence checklist','','Notebook: pgm_example_lyap.ipynb','Last reviewed block: B5','SHA-256: '+sha,'Presentation: evaluation-ancillary-v1; source/output inspection only; no rendered/image inspection.','Static: supplementary/b5-static-002.json (passed). Execution: supplementary/b5-nbconvert-001.log (nbconvert exit 0, fresh attempt kernel).','','| Item | Requirement | Status | Zero-based cells | Evidence |','|---|---|---|---|---|']
for i,(word,idx,ev) in enumerate(zip(wordings,indices,evidence),1):lines.append(f'| {i} | {word} | verified | {idx} | {ev} |')
assert len(wordings)==12
(r/'supplementary/pgm_example_lyap_checklist.md').write_text('\n'.join(lines)+'\n')
audit={'notebook_sha256':sha,'cell_count':len(nb.cells),'code_cells':sum(c.cell_type=='code' for c in nb.cells),'execution_errors':errors,'unexecuted':unexecuted,'math_source_issues':math_issues,'plot_output_present':True,'checks':'source and saved outputs inspected; no rendering or image inspection','static_pass':True,'nbconvert_exit_code':0}
(r/'supplementary/b5-final-audit.json').write_text(json.dumps(audit,indent=2))
handoff={'current_block':'B5','completion_status':'complete','next_block':None,'entry_exit_reason':'Exact symbolic proof, final static checks, clean-kernel nbconvert execution and twelve-item notebook evidence audit complete.','operational_status':'completed','run_status':'success','completed_blocks':['B1','B2','B3','B4','B5'],'unresolved_work':'No required Lyapunov proof obligations remain. A separate arbitrary-horizon global lambda/S formula is not established and is not required.','isolation':'instruction_only','prohibited_content_observed':False,'exhaustive_os_read_trace_available':False,'consulted_sources':'Frozen approved input, dispatch, settings, allowlist, worker protocol, clean-room and recovery policies, five approved skills/workflows, approved framework source, and own generated files; earlier block source-access records retained.','B5_operational_incidents':[{'failure':'b5-static-001: notebook E402 imports after docstring, unused helper imports, SymPy Basic type arithmetic','repair':'Changed notebook docstring to comment, removed unused imports, cast sympify scalar results to Expr. No math or frozen sources changed.','recheck':'b5-static-002 passed; fresh kernel nbconvert passed.'},{'warning':'Windows ZMQ selector fallback and missing dash comm handler','impact':'Nonfatal; notebook execution exited 0 with no cell errors.'}],'notebook':'pgm_example_lyap.ipynb','state':'state/pgm_b5.json','audit':'supplementary/b5-final-audit.json','finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(r/'supplementary/b5-handoff.json').write_text(json.dumps(handoff,indent=2))
print(json.dumps(audit,indent=2))
print(json.dumps(handoff,indent=2))