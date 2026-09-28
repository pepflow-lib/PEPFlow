import json,hashlib,re
from pathlib import Path
here=Path.cwd(); settings=json.loads((here.parent/'settings.json').read_text(encoding='utf-8-sig')); original=Path(settings['original_submission'])
checks=[]
for relative,expected in settings['submission_hashes'].items():
    p=original/relative
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    checks.append({'path':relative.replace('\\','/'),'match':actual==expected})
assert all(c['match'] for c in checks)
nb=json.loads((original/'ogm_example_lyap.ipynb').read_text())
code=[c for c in nb['cells'] if c['cell_type']=='code']
summary={'frozen_hash_count':len(checks),'frozen_hashes_unchanged':True,'notebook_cells':len(nb['cells']),'code_cells':len(code),'execution_counts':[c['execution_count'] for c in code],'error_outputs':[o for c in code for o in c['outputs'] if o['output_type']=='error'],'embedded_png_count':sum('image/png' in o.get('data',{}) for c in code for o in c['outputs']),'checks':checks}
(here/'integrity-delivery.json').write_text(json.dumps(summary,indent=2))
print({k:v for k,v in summary.items() if k!='checks'})
# Summarize explicit external/sibling path indicators in own host tool-call evidence, without opening any paths.
calls=json.loads((here.parent/'own-generation-host-access-calls.json').read_text())
indicators=[]
for item in calls:
    s=item['arguments'].replace('\\\\','/').replace('\\','/')
    paths=re.findall(r'(?:ogm|pgm_with_sos|pgm_without_sos|bppm|fgm|gd)/r\d+',s)
    other=[p for p in paths if p!='ogm/r04']
    if other: indicators.append({'line':item['line'],'paths':other})
print('HOST_CALL_COUNT',len(calls),'SIBLING_PATH_INDICATORS',indicators)
