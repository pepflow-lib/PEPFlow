import collections
import csv
import datetime as dt
import json
import os
import re
from pathlib import Path
from urllib.parse import quote, unquote
from peppy_astra_prepare_review import read, digest, fs_path, parse, require

ROOT = Path(__file__).resolve().parents[1]
P = Path((ROOT / 'tmp/current_peppy_posthoc.txt').read_text())
S = read(P / 'settings.json')
C = Path(S['campaign'])
original = read(C / 'supplementary/details.json')
inventory = read(P / 'original-inventory.json')
def write(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')
def link(path, label, base=P):
    return f'[{label}]({quote(Path(os.path.relpath(path, base)).as_posix())})'
def check_ref(ref, directory, own):
    path = Path(ref.split('#')[0])
    if not path.is_absolute(): path = directory / path
    path = path.resolve()
    require(any(path.is_relative_to(root.resolve()) for root in [directory, own]), f'Out-of-scope evidence: {ref}')
    require(fs_path(path).is_file(), f'Missing evidence: {ref}')

rows = []
blocks = []
costs = []
for a in original['attempts']:
    aid = a['attempt_id']
    old_path = C / 'supplementary/evaluation' / aid / 'review.json'
    old = read(old_path)
    row = dict(attempt_id=aid, condition_id=a['condition_id'], repetition=a['repetition'],
               historical_mathematical_verdict=old['mathematical_verdict'], historical_eligible=old['eligible'],
               original_generation_status=a['run_status'], original_delivery_status='COMPLETE' if old['workflow_complete'] else 'INCOMPLETE',
               historical_review=str(old_path.relative_to(C)), historical_review_sha256=digest(old_path),
               original_generation_seconds=a['attempt_wall_seconds'], original_generation_tokens=a['generation_tokens_total'],
               original_review_seconds=a['evaluation_wall_seconds'], original_review_tokens=a['evaluation_tokens_total'],
               mathematical_criteria='Frozen exact-target and B1-B5 mathematical criteria; no threshold or target changes',
               access_findings={'status': old['access_status'], 'prohibited_mathematical_exposure': 'not_established',
                                'independence_eligible': True, 'historical_evidence': old['access_reason'],
                                'limitation': 'Instruction-only controls and available logs do not certify absence of every possible exposure.'})
    if aid in S['fresh_reviews']:
        R = P / aid
        r = read(R / 'review.json')
        require(r['attempt_id'] == aid and r['mathematical_verdict'] in ['PASS','FAIL','REVIEW','NOT_EVALUATED'], 'Invalid review')
        require(len(r['blocks']) == 5 and {b['block_id'] for b in r['blocks']} == {f'B{i}' for i in range(1,6)}, 'Block mismatch')
        require(r['mathematical_verdict'] != 'PASS' or r['mathematical_evidence_refs'], 'Missing PASS evidence')
        refs = list(r['mathematical_evidence_refs'])
        for check in r['checks']:
            if check.get('evidence_ref'): refs.append(check['evidence_ref'])
        for b in r['blocks']: refs.extend(b.get('evidence_refs', []))
        for ref in refs: check_ref(ref, R, Path(a['output']))
        row.update(mathematical_verdict=r['mathematical_verdict'], mathematical_reason=r['mathematical_reason'],
                   basis='Fresh missing mathematical verification; original generation not resumed',
                   assessment=str((R/'review.json').relative_to(C)), access_findings=r['access_findings'],
                   original_delivery_status=r['original_delivery_status'],
                   posthoc_validation_execution_status=r['posthoc_validation_execution_status'],
                   execution_adjustments=r['execution_adjustments'])
        for b in r['blocks']: blocks.append(dict(attempt_id=aid, **b))
        h = read(P / 'host' / ('ph_'+aid+'.json'))
        require(h['session_id'] == S['reviews'][aid]['session_id'], 'Wrong review session')
        require(h['turns'] and all(t['model']=='gpt-6-astra' and t['effort']=='medium' for t in h['turns']), 'Wrong model/effort')
        usage = [e for e in h['events'] if e['type']=='usage']
        boundaries = [e for e in h['events'] if e['type']!='usage']
        complete = bool(usage and boundaries and usage[0]['total']==usage[0]['last_usage'] and not h['anomalies'] and boundaries[-1]['type']=='task_complete' and parse(boundaries[-1]['timestamp'])>=parse(r['review_stopped_at']))
        require(parse(S['reviews'][aid]['dispatched_at'])<=parse(r['review_started_at'])<=parse(r['review_stopped_at']), 'Invalid timestamps')
        require(parse(r['review_stopped_at'])<=parse(S['reviews'][aid]['deadline']), 'Review overrun')
        costs.append(dict(attempt_id=aid, session_id=h['session_id'], model='gpt-6-astra', reasoning_effort='medium',
                          dispatch_at=S['reviews'][aid]['dispatched_at'], stopped_at=r['review_stopped_at'],
                          wall_seconds=(parse(r['review_stopped_at'])-parse(S['reviews'][aid]['dispatched_at'])).total_seconds(),
                          token_components_observed=h['last_total'], tokens_total=h['last_total']['total_tokens'] if complete else None,
                          usage_status='complete' if complete else 'partial', host_evidence=str((P/'host'/('ph_'+aid+'.json')).relative_to(C))))
        S['reviews'][aid].update(status='completed', review_sha256=digest(R/'review.json'), stopped_at=r['review_stopped_at'])
    else:
        require(old['mathematical_verdict']=='PASS' or aid=='bppm_r02', 'Unexpected missing mathematical review')
        if aid=='bppm_r02':
            require(all(b['mathematical_checks_passed'] is True for b in old['blocks']), 'BPPM verification missing')
            audit = C/'supplementary/evaluation/bppm_r02/validation/symbolic-audit.json'
            require(audit.is_file(), 'Missing BPPM exact audit')
            row.update(mathematical_verdict='PASS', mathematical_reason='The preserved independent review established the exact R/(alpha*N) target using the supplied potential, general step, base, terminal and sign/domain arguments. Its saved fresh symbolic audit has exact zero residuals. The historical NOT_EVALUATED label coupled this completed verification to generic-runtime eligibility; that operational issue is separated here.', historical_review_reason=old['final_reason'],
                       basis='Preserved completed mathematical review; post hoc removal of generic-runtime eligibility coupling',
                       assessment=str(old_path.relative_to(C)), posthoc_validation_execution_status='NOT_RERUN')
            row['access_findings'].update(status='operational_deviation', posthoc_reason='Generic launcher provenance concern is operational; historical evidence establishes no prohibited mathematical exposure.')
            adjudication = P / 'bppm_r02-adjudication.md'
            adjudication.write_text('# BPPM r02 — dated post hoc adjudication\n\nAssessed '+dt.datetime.now(dt.timezone.utc).isoformat()+' under the explicit user-requested separation of mathematical, delivery and access findings.\n\nMathematical validity: **PASS**, preserving completed verification. Original delivery: **INCOMPLETE**. Actual prohibited mathematical exposure: **not established** by available evidence; generic launcher provenance remains an operational finding.\n\n'+row['mathematical_reason']+'\n\nNo fresh proof verification or generation was performed for this adjudication. All five historical blocks explicitly record mathematical_checks_passed=true; the final delivery checklist remains incomplete.\n\n'+link(old_path,'Unmodified historical review')+' · '+link(audit,'Previously completed exact symbolic audit')+'\n',encoding='utf-8')
            row['assessment']=str(adjudication.relative_to(C))
        else:
            require(old['eligible'], 'Unexpected historical access exclusion')
            row.update(mathematical_verdict=old['mathematical_verdict'], mathematical_reason=old['final_reason'],
                       basis='Preserved completed independent mathematical review', assessment=str(old_path.relative_to(C)),
                       posthoc_validation_execution_status='NOT_RERUN')
        for b in old['blocks']:
            blocks.append(dict(attempt_id=aid, block_id=b['block_id'], historical_gate_verdict=b['gate_verdict'],
                               mathematical_status='PASS' if b.get('mathematical_checks_passed') is True or b['gate_verdict']=='PASS' else 'NOT_EVALUATED',
                               delivery_status='COMPLETE' if b.get('delivery_checks_passed') is True else 'INCOMPLETE' if b.get('delivery_checks_passed') is False else 'NOT_EVALUATED',
                               reason=b['reason'], evidence_refs=b.get('evidence_refs',[])))
    rows.append(row)

require(len(rows)==30 and len(blocks)==150 and len(costs)==2, 'Count mismatch')
# All historical files except the explicitly updated summary must remain byte-identical.
changed = [name for name, expected in inventory.items() if name!='results.md' and (not fs_path(C/name).is_file() or digest(C/name)!=expected)]
require(not changed, f'Historical records changed: {changed}')
require(digest(P/'original-summary/results.md')==inventory['results.md'], 'Original summary backup mismatch')
host = read(P/'host/controller.json')
turn = host['turns'][-1]
require(turn['model']=='gpt-6-astra' and turn['effort']=='medium', 'Controller setting mismatch')
starts=[e for e in host['events'] if e['type']=='task_started' and parse(e['timestamp'])<=parse(turn['timestamp'])]
start=starts[-1]['timestamp']
before=[e for e in host['events'] if e['type']=='usage' and parse(e['timestamp'])<parse(start)]
baseline=before[-1]['total'] if before else None
delta={k:v-baseline[k] for k,v in host['last_total'].items()} if baseline else None
controller_cost=dict(started_at=start, observed_at=host['observed_at'], token_components_observed_delta=delta,
                     usage_status='partial', scope='Current post hoc controller turn through latest collection; includes preparation, orchestration and reporting; final response is outside snapshot.')
counts=dict(collections.Counter(r['mathematical_verdict'] for r in rows))
count_text=', '.join(f'{counts.get(k,0)} {k}' for k in ['PASS','FAIL','REVIEW','NOT_EVALUATED'])
report=dict(assessed_at=dt.datetime.now(dt.timezone.utc).isoformat(), user_authorized_posthoc=True,
            original_protocol=S['original_protocol'], assessment_policy=S['policy'], model='gpt-6-astra', reasoning_effort='medium',
            preserved_completed_mathematical_reviews=28, fresh_mathematical_reviews=2, attempts=rows, blocks=blocks,
            mathematical_counts=counts, additional_verification_costs=costs, additional_controller_cost=controller_cost,
            original_records_unchanged=True, original_delivery_not_backfilled=True)
write(P/'assessment.json',report); write(P/'costs.json',{'verification':costs,'controller':controller_cost})
write(P/'settings.json',S)
for name,data in [('attempts.csv',rows),('blocks.csv',blocks)]:
    fields=list(dict.fromkeys(k for row in data for k in row))
    with (P/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in data)
lines=[f'# Post hoc mathematical assessment — {report["assessed_at"]}', '',
       'This is a user-requested retrospective assessment of the frozen 30-attempt campaign. The original protocol, submissions, reviews and time/token records remain unchanged. This assessment separates mathematical validity from delivery and access; it is not a rerun of generation or a replacement preregistered result.', '',
       'The same frozen exact-target, all-horizon, sign/domain, normalization, endpoint and B1–B5 mathematical criteria apply to all attempts. No mathematical criterion or numerical threshold was relaxed. Twenty-seven existing PASS reviews are preserved. BPPM r02 uses its already-completed positive mathematical checks and exact symbolic audit; only the prior generic-runtime exclusion is separated from that result. FEG r03 and PGM without SOS r02 receive fresh verification. No missing proof arguments may be supplied.', '',
       f'Mathematical results: {count_text}. Original delivery: {sum(r["original_delivery_status"].upper()=="COMPLETE" for r in rows)}/30 complete. A successful validation replay does not retroactively complete original delivery.', '',
       '| Attempt | Mathematical validity | Original delivery | Review basis | Access |', '| --- | --- | --- | --- | --- |']
for row in rows:
    access=row['access_findings']; exposure=access.get('prohibited_mathematical_exposure','not_established')
    if isinstance(exposure, dict): exposure=exposure['status']
    label='Fresh verification' if row['attempt_id'] in S['fresh_reviews'] else 'Preserved verification'
    lines.append(f'| {row["attempt_id"]} | {link(C/row["assessment"],row["mathematical_verdict"])} | {row["original_delivery_status"]} | {label} | {str(exposure).replace("|","/")} |')
lines += ['', '## Access and operational findings', '',
          'The three historical exclusions concerned generic Python/Jupyter dependency routes. They are retained in the original records and treated as operational findings in this post hoc assessment. Available evidence does not establish prohibited mathematical exposure. Instruction-only isolation and nonexhaustive logs do not certify absence of every possible read. The BPPM r05 recovered empty-file write incident remains in its original review.', '',
          'Original incomplete deliveries remain FEG r03, PGM without SOS r02 and BPPM r02. Fresh environment and display adjustments, including their scope and unchanged proof semantics, are documented in the two new reviews and validation evidence. No new verification was charged to the 28 preserved reviews.', '',
          '## Additional costs', '', '| New verification | Minutes | Tokens | Coverage |','| --- | ---: | ---: | --- |']
for cost in costs: lines.append(f'| {cost["attempt_id"]} | {cost["wall_seconds"]/60:.2f} | {cost["tokens_total"]} | {cost["usage_status"]} |')
lines += ['', 'The two reviews ran in parallel. Durations include validation setup, repair and waiting after dispatch; their sum is not elapsed campaign time. Token totals count input plus output, including repeated context; cached input and reasoning are subsets. Controller/preparation/reporting usage is separate and partial through the recorded observation. No original generation or review costs were changed.', '',
          link(P/'costs.json','Additional cost records')+' · '+link(P/'assessment.json','All 30 assessments and 150 block records')+' · '+link(C/'timing.md','Unchanged original timing')+' · '+link(P/'original-summary/results.md','Preserved original summary'), '',
          'Post hoc interpretation must be distinguished from the original 27-PASS/3-operational-exclusion result. Historical run-status and paired cost records remain historical; this assessment changes interpretation and completes missing verification, not the generation timeline.']
(P/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
summary=['# Campaign results — post hoc mathematical assessment', '',
         f'Updated {report["assessed_at"]} at the user’s request. This dated post hoc assessment preserves completed mathematical reviews and completes missing verification for `feg_r03` and `pgm_without_sos_r02`, using GPT-6 Astra with medium reasoning. No proof generation was rerun and no submitted proof was altered.', '',
         f'Mathematical verdicts: **{count_text}**. Original delivery remains **27 complete / 3 incomplete**. Generic dependency-path and notebook-display issues are operational; available evidence establishes no prohibited mathematical exposure. Access observability remains limited by instruction-only isolation.', '',
         'The original result was 27 eligible PASS reviews and three operational exclusions. BPPM r02 already had completed positive mathematical verification; its post hoc mathematical PASS preserves that work. The dated report distinguishes the two fresh verdicts, original delivery, access evidence and additional costs. Original reviews, raw records and timing are unchanged.', '',
         link(P/'report.md','Dated re-evaluation report',C)+' · '+link(P/'assessment.json','Detailed post hoc records',C)+' · '+link(P/'costs.json','Additional verification costs',C)+' · '+link(P/'original-summary/results.md','Original summary (preserved)',C)+' · '+link(C/'timing.md','Original timing (unchanged)',C), '',
         '| Condition | Mathematical PASS | FAIL | REVIEW | NOT_EVALUATED |', '| --- | ---: | ---: | ---: | ---: |']
for cond in dict.fromkeys(r['condition_id'] for r in rows):
    counter=collections.Counter(r['mathematical_verdict'] for r in rows if r['condition_id']==cond)
    summary.append('| '+cond+' | '+' | '.join(str(counter[k]) for k in ['PASS','FAIL','REVIEW','NOT_EVALUATED'])+' |')
(C/'results.md').write_text('\n'.join(summary)+'\n',encoding='utf-8')
write(P/'integrity.json', {'checked_at':dt.datetime.now(dt.timezone.utc).isoformat(), 'original_files_verified':len(inventory)-1,
                          'changed_original_files':['results.md'], 'original_summary_backup_hash':digest(P/'original-summary/results.md'),
                          'original_submissions_reviews_cost_records_unchanged':True})
print(json.dumps({'mathematical_counts':counts,'report':str(P/'report.md'),'new_review_costs':costs}))
