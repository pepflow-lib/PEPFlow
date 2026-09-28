import json,hashlib,datetime
from pathlib import Path
root=Path.cwd()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
nbpath=root/'pgm_example_lyap.ipynb'
nb=json.loads(nbpath.read_text(encoding='utf-8'))
digest=hashlib.sha256(nbpath.read_bytes()).hexdigest()
record={
 'attempt_id':'pgm_without_sos_r02','current_block':'B5','completion_status':'incomplete','next_block':None,
 'run_status':'error','operational_status':'stopped','recorded_utc':now,
 'entry_exit_reason':'Final nbconvert dispatcher used unapproved Python313 installed dependencies. Frozen allowlist restricts installed dependencies to pinned .venv and provides no source-equivalence exception; continuation prohibited by generic tool-recovery policy.',
 'access_control':'instruction_only','access_status':'confirmed_unapproved_generic_dependency_read','eligible':False,
 'prohibited_mathematical_content_observed':False,
 'incident':{'command':['pinned python.exe','-I','-B','-m','jupyter','nbconvert','--to','notebook','--execute','pgm_example_lyap.ipynb','--ExecutePreprocessor.kernel_name=pgm-private'],
  'owned_launcher':'supplementary/execute_b5.py','evidence':'supplementary/b5-nbconvert.log',
  'observed_dependency_path':'C:/Users/Jack/AppData/Local/Programs/Python/Python313/Lib/site-packages/zmq/_future.py',
  'observed_result':'nbconvert exit 0; all notebook code completed. Parent conversion process used Python313 dependency; private notebook kernel argv remained pinned.',
  'distinction':'Confirmed generic dependency route deviation; no target-specific prohibited source or answer observed. Not classified as mathematical contamination.',
  'triage':['Stopped suspect route; no active owned jobs','Read own log, approved recovery policy, allowlist and settings only','Allowlist installed_dependencies=.venv/Lib/site-packages; source_equivalence_exceptions=[]','No permitted evidence can establish predeclared exception; no further execution or mathematical work'],
  'repair_not_executed':'Would call pinned python -I -B -m nbconvert directly; cannot retroactively cure eligibility or continue absent predeclared equivalence rule'},
 'completed_blocks':['B1','B2','B3','B4'],
 'B5_evidence':{'standalone_symbolic_checks':'Step, base, boundary, normalization, N=1 all exact zero; generic Gram square completion exact zero.',
  'notebook_execution':'78-cell notebook executed successfully through nbconvert before final small source edit; execution route is ineligible.',
  'postexecution_edit':'One symbolic recurrence-link assertion and printed elimination formula added to cell 75; this edit has not undergone required static check and final execution.',
  'last_static':'supplementary/b5-static-002.json passed before final cell75 edit',
  'current_notebook_sha256':digest},
 'unresolved_work':['Eligible pinned final notebook execution','Static check after latest cell75 edit','Final twelve-item delivery audit'],
 'consulted_sources':['Own generated B1-B5 notebook, scripts, state, and logs','Approved lyap-closed-form SKILL.md and references/workflow.md','Approved dispatch.md, worker-protocol.md, clean-room.md, settings.json, preflight-only.md, allowlist.json','Approved optional/with-clean-room/references/tool-recovery.md','Previously recorded approved framework and skills'],
 'ordinary_incidents':['Nested rational symbolic expansion was slow; owned sessions interrupted, modular exact square completion succeeded','Initial B5 lint failed on lambda, semicolons, import placement; fixed and B5 static002 passed','Attempted reads of nonexistent own b4-access.json and approved/tool-recovery.md yielded no content; exact existing paths then used'],
 'audit_limit':'Instruction-only isolation; no exhaustive filesystem tracing. Dependency read is evidenced by the actual conversion warning path.',
 'original_deadline_utc':'2026-09-23T18:18:03.767479+00:00'}
(root/'supplementary/b5-access-record.json').write_text(json.dumps(record,indent=2))
b4=json.loads((root/'state/pgm_b4.json').read_text())
b5={**b4,'block_status':'incomplete','run_status':'error','lyapunov_proof_verified':False,
 'proof_checks':{'step':True,'base':True,'boundary':True,'signs':True,'domain':True,'normalization':True},
 'proof_check_scope':'Executed exact standalone and notebook identities before final recurrence-link assertion edit; these mathematical results do not satisfy remaining delivery/access gates.',
 'proof_valid':False,'coefficient_formula_status':'derived_and_exact_local_identities_checked_delivery_incomplete',
 'lyapunov_formula':nb['cells'][2]['source'],'proof_outline':nb['cells'][3]['source'],
 'symbolic_check_source':'supplementary/b5_symbolic_cells.py',
 'access_record':'supplementary/b5-access-record.json','access_eligible':False,
 'delivery_unresolved':record['unresolved_work'],'notebook_sha256':digest}
(root/'state/pgm_b5.json').write_text(json.dumps(b5,indent=2))
check=root/'supplementary/pgm_example_lyap_checklist.md'
prior=check.read_text(encoding='utf-8-sig')
(root/'supplementary/b4-checklist-archived.md').write_text(prior)
rows=[
(1,'title, problem description, and algorithm update equations in LaTeX','verified','0','Assumptions and update retained.'),
(2,'proof statement and final theorem with proof outline','content present; final audit incomplete','1-3','Explicit potential, finite-product coefficient, all residuals and squares stated.'),
(3,'imports','verified in prior execution','4-5','Kernel bootstrap uses pinned approved source. Parent converter route deviation recorded separately.'),
(4,'function/operator definitions','verified','7','Approved native smooth-convex and convex definitions.'),
(5,'make_ctx_pgm and get_pep_setup','verified','9','Algorithm setup retained and certificate replays executed.'),
(6,'numerical evidence and comparison plot','verified in prior execution','11-12','Sweep data and PNG output retained; no image inspection.'),
(7,'dense and relaxed proof solves','verified in prior execution','13-15,25-27','Both horizon certificate owners and statuses retained.'),
(8,'lambda and S verification','verified in prior execution','15-35,60','Coherent certificates, exact source replay, numerical decompositions; global analytic full-PEP remains unverified.'),
(9,'partial-sum Lyapunov construction and rank profile','verified in prior execution','36-39','Full numerical reconstruction at two horizons.'),
(10,'special-vector identification','verified in prior execution','40-49','Visible actual candidate and sparse-basis searches.'),
(11,'coefficient extraction and closed-form V_k','content and numerical comparison verified; final audit incomplete','50-63','Resolved potential and every-index comparison retained; maximum full-component comparison 3.15e-6.'),
(12,'symbolic step, base, and boundary identities','exact identities checked; delivery pending','64-77','Exact all-coordinate checks executed; N=1 and normalization included; cell75 modified afterward and not rerun.')]
text='# Notebook evidence checklist\n\nNotebook: pgm_example_lyap.ipynb\nReviewed block: B5 incomplete\nSHA-256: '+digest+'\nPresentation policy: evaluation-ancillary-v1; no rendering or image inspection.\nOperational stop: confirmed unapproved generic conversion dependency route; see b5-access-record.json.\n\n| Item | Requirement | Status | Cell indices | Evidence |\n|---|---|---|---|---|\n'
for row in rows:text+='| '+' | '.join(map(str,row))+' |\n'
check.write_text(text)
print(json.dumps({'run_status':'error','current_block':'B5','completed_blocks':record['completed_blocks'],'notebook_sha256':digest,'access_status':record['access_status']},indent=2))
