"""Operational bookkeeping only; no mathematical guidance or assessment."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
C = Path((ROOT/'tmp/current_peppy_astra_medium_6x5_campaign.txt').read_text(encoding='utf-8'))
S = C/'supplementary'
M = json.loads((S/'manifest.json').read_text(encoding='utf-8'))
D = json.loads((S/'details.json').read_text(encoding='utf-8'))
now = lambda: dt.datetime.now(dt.timezone.utc)
def write(p,v):
    p.write_text(json.dumps(v,indent=2),encoding='utf-8')
def event(kind,attempt=None,**kw):
    row=dict(timestamp=now().isoformat(),monotonic=time.monotonic(),event=kind,attempt_id=attempt,**kw)
    with (S/'controller-events.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(row)+'\n')
    return row
def save():
    for a in M['attempts']:
        dest=next(x for x in D['attempts'] if x['attempt_id']==a['attempt_id'])
        dest.update(a)
    write(S/'manifest.json',M);write(S/'details.json',D)
cmd=sys.argv[1]
if cmd=='status':
    print(json.dumps([dict(attempt_id=a['attempt_id'],status=a['run_status'],preflight=a['preflight_status'],deadline=a.get('deadline'),block=a.get('active_block')) for a in M['attempts']],indent=2))
    raise SystemExit()
a=next(x for x in M['attempts'] if x['attempt_id']==sys.argv[2])
aid=a['attempt_id'];out=Path(a['output']);approved=Path(a['approved'])
if cmd=='register':
    a['agent_name']=sys.argv[3]
    h=json.loads((S/'host'/f'{a["agent_name"]}.json').read_text(encoding='utf-8'))
    assert h['turns'] and all(x['model']=='gpt-6-astra' and x['effort']=='medium' for x in h['turns'])
    a['session_id']=h['session_id'];a['preflight_status']='running'
    event('worker_registered',aid,agent=a['agent_name'],session_id=a['session_id'])
elif cmd=='release':
    assert not a['started']
    evidences=list((out/'supplementary').glob('preflight-*.json'))
    passed=[p for p in evidences if json.loads(p.read_text(encoding='utf-8-sig')).get('status')=='passed' and json.loads(p.read_text(encoding='utf-8-sig')).get('preflight_passed') is True]
    assert passed, 'Actual worker preflight must pass'
    a['preflight_status']='passed';a['preflight_evidence']=str(passed[-1])
    h=json.loads((S/'host'/f'{a["agent_name"]}.json').read_text(encoding='utf-8'))
    assert h['session_id']==a['session_id']
    a['preflight_usage_baseline']=h.get('last_total')
    assert hashlib.sha256(Path(a['packet']).read_bytes()).hexdigest()==a['packet_sha256']
    shutil.copyfile(a['packet'],approved/'input.md')
    stamp=now();deadline=stamp+dt.timedelta(seconds=M['wall_limit_seconds'])
    a.update(started=True,dispatch_at=stamp.isoformat(),deadline=deadline.isoformat(),run_status='running',active_block='B1',visits=[dict(block_id='B1',start=stamp.isoformat(),visit_id=1,usage_start=h.get('last_total'))])
    a['queue_wait_seconds']=(stamp-dt.datetime.fromisoformat(a['queued_at'])).total_seconds()
    dispatch=(S/'inputs'/f'{aid}-dispatch.txt').read_text(encoding='utf-8')
    dispatch+=f'\nDispatch UTC: {a["dispatch_at"]}. Original deadline UTC: {a["deadline"]}. Stop at this deadline; do not extend it.\n'
    (approved/'dispatch.md').write_text(dispatch,encoding='utf-8')
    event('dispatch',aid,session_id=a['session_id'],deadline=a['deadline'],baseline=a['preflight_usage_baseline'])
    D['status']='generation_in_progress'
    print(str(approved/'dispatch.md'))
elif cmd=='handoff':
    assert a['run_status']=='running' and now()<dt.datetime.fromisoformat(a['deadline'])
    block=sys.argv[3];stamp=now().isoformat()
    h=json.loads((S/'host'/f'{a["agent_name"]}.json').read_text(encoding='utf-8'))
    a['visits'][-1]['end']=stamp
    a['visits'][-1]['usage_end']=h.get('last_total')
    a['visits'].append(dict(block_id=block,start=stamp,visit_id=len(a['visits'])+1,usage_start=h.get('last_total')))
    a['active_block']=block
    event('block_transition',aid,next_block=block,session_id=a['session_id'],message='Proceed with the next step under the existing case instructions.')
elif cmd=='stop':
    stamp=now().isoformat()
    hostpath=S/'host'/f'{a.get("agent_name")}.json'
    h=json.loads(hostpath.read_text(encoding='utf-8')) if hostpath.exists() else {}
    boundaries=[e for e in h.get('events',[]) if e['type']!='usage']
    if boundaries and boundaries[-1]['type']=='task_complete' and boundaries[-1]['timestamp'] >= a.get('dispatch_at',''):
        stamp=boundaries[-1]['timestamp'];a['stop_time_source']='host_task_complete'
    else:a['stop_time_source']='controller_observed_stop'
    a['stopped_at']=stamp;a['run_status']=sys.argv[3]
    a['stop_reason']=' '.join(sys.argv[4:])
    if a.get('visits'):
        a['visits'][-1]['end']=stamp;a['visits'][-1]['usage_end']=h.get('last_total')
    a['host_usage_final']=h.get('last_total')
    if h.get('last_total') and a.get('preflight_usage_baseline') and not h.get('anomalies'):
        deltas={k:v-a['preflight_usage_baseline'].get(k,0) for k,v in h['last_total'].items()}
        a['generation_tokens_observed']=deltas
        a['generation_tokens_total']=deltas.get('total_tokens') if all(v>=0 for v in deltas.values()) else None
        a['usage_status']='complete' if a['generation_tokens_total'] is not None else 'partial'
    if a.get('dispatch_at'):a['attempt_wall_seconds']=(dt.datetime.fromisoformat(stamp)-dt.datetime.fromisoformat(a['dispatch_at'])).total_seconds()
    hashes={}
    for p in out.rglob('*'):
        if p.is_file() and not any(x in p.parts for x in ['.runtime','__pycache__']):
            hashes[str(p.relative_to(out))]=hashlib.sha256(p.read_bytes()).hexdigest()
    frozen=S/'submissions';frozen.mkdir(exist_ok=True)
    write(frozen/f'{aid}-hashes.json',hashes)
    a['submission_hashes']=str(frozen/f'{aid}-hashes.json')
    event('stop',aid,status=a['run_status'],reason=a['stop_reason'])
else: raise ValueError(cmd)
save()
