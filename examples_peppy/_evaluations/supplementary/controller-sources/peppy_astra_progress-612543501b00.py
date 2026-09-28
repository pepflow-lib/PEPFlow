"""Show operational progress without inspecting mathematical submissions."""
import datetime as dt
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
C=Path((ROOT/'tmp/current_peppy_astra_medium_6x5_campaign.txt').read_text())
M=json.loads((C/'supplementary/manifest.json').read_text())
now=dt.datetime.now(dt.timezone.utc)
lines=[f'# Campaign progress\n\nUpdated {now.isoformat()}. GPT-6 Astra, medium reasoning; 30 attempts, three parallel workers, five sequential rounds.\n',
       'Generation outcomes are provisional until all generation stops and independent review completes.\n',
       '| Attempt | Operational status | Active block | Elapsed minutes |','| --- | --- | --- | --- |']
active=[]
for a in M['attempts']:
    elapsed=(now-dt.datetime.fromisoformat(a['dispatch_at'])).total_seconds()/60 if a.get('dispatch_at') and not a.get('stopped_at') else (a.get('attempt_wall_seconds') or 0)/60
    state=a['run_status'] if a['started'] else 'preflight' if a.get('preflight_status')=='running' else 'queued'
    lines.append(f'| {a["attempt_id"]} | {state} | {a.get("active_block", "—")} | {elapsed:.1f} |')
    if a['run_status']=='running':
        active.append({'attempt':a['attempt_id'],'block':a.get('active_block'),'elapsed_minutes':round(elapsed,1),'deadline':a['deadline'],
                       'remaining_minutes':round((dt.datetime.fromisoformat(a['deadline'])-now).total_seconds()/60,1)})
(C/'progress.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
started=sum(a['started'] for a in M['attempts'])
stopped=sum(a['run_status'] not in ['running','not_started'] for a in M['attempts'])
review_completed=sum(a.get('review_status')=='completed' for a in M['attempts'])
if review_completed == 30:
    lines[1] = 'All generation and independent reviews are complete. See [final results](results.md) and [timing](timing.md).\n'
review_active=[{'attempt':a['attempt_id'],'deadline':a['review_deadline'],
                'remaining_minutes':round((dt.datetime.fromisoformat(a['review_deadline'])-now).total_seconds()/60,1)}
               for a in M['attempts'] if a.get('review_status')=='running']
lines.extend(['', f'Independent reviews: {review_completed}/30 completed; {len(review_active)} active.', '',
              '| Attempt | Review status |', '| --- | --- |'])
lines.extend(f'| {a["attempt_id"]} | {a.get("review_status", "queued")} |' for a in M['attempts'])
(C/'progress.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
D=json.loads((C/'supplementary/details.json').read_text())
if D.get('status')!='completed':
    (C/'results.md').write_text(f'Campaign in progress: {started}/30 generation attempts started; {stopped}/30 stopped and frozen. Independent reviews: {review_completed}/30 completed, {len(review_active)} active. Final verdicts are pending.\n\nSee [live operational progress](progress.md) and [registered settings](supplementary/manifest.json).\n',encoding='utf-8')
    (C/'timing.md').write_text('Timing collection is active. See [operational elapsed times](progress.md). Final block, generation, review and preparation costs will be reconciled after completion; no unavailable cost is estimated.\n',encoding='utf-8')
    csvpath=C/'supplementary/runs.csv'
    with csvpath.open(encoding='utf-8') as f:columns=next(csv.reader(f))
    with csvpath.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader()
        writer.writerows({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in a.items()} for a in M['attempts'])
print(json.dumps({'time':now.isoformat(),'started':sum(a['started'] for a in M['attempts']),
                  'stopped':stopped,'active':active,'reviews_completed':review_completed,'reviews_active':review_active},indent=2))
