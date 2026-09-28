"""Show operational progress without inspecting mathematical submissions."""
import datetime as dt
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
print(json.dumps({'time':now.isoformat(),'started':sum(a['started'] for a in M['attempts']),
                  'stopped':sum(a['run_status'] not in ['running','not_started'] for a in M['attempts']),'active':active},indent=2))
