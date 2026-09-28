from pathlib import Path
import json,hashlib,datetime
root=Path(__file__).resolve().parent
settings=json.loads((root.parent/'settings.json').read_text(encoding='utf-8-sig'))
original=Path(settings['original_submission'])
checks={}
for rel,expected in settings['submission_hashes'].items():
    p=Path('\\\\?\\'+str(original/rel))
    checks[rel]=hashlib.sha256(p.read_bytes()).hexdigest()==expected
nb=json.loads((original/'feg_example_lyap.ipynb').read_text(encoding='utf-8-sig'))
cells=[c for c in nb['cells'] if c['cell_type']=='code']
static={}
for name in ['preflight-002','b1-static-003','b2-static-002','b2-N8-static','b3-static-002','b4-static-002','b5-static-001']:
    s=json.loads((original/f'supplementary/{name}.json').read_text(encoding='utf-8-sig'))
    static[name]=[{'label':c['label'],'returncode':c['returncode'],'stdout':c.get('stdout','')} for c in s['commands'] if c['label'] in ['source_ruff','source_ty','clean_kernel_import_probe']]
result={'frozen_hashes_count':len(checks),'all_hashes_match':all(checks.values()),'hash_failures':[k for k,v in checks.items() if not v], 'code_cell_count':len(cells),'execution_counts':[c['execution_count'] for c in cells], 'error_outputs':[c['id'] for c in cells if any(o['output_type']=='error' for o in c.get('outputs',[]))], 'plot_output_present':any('image/png' in o.get('data',{}) for c in cells for o in c.get('outputs',[])), 'saved_static_checks':static,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(root/'artifact-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
p=Path('\\\\?\\'+str(original/'supplementary/approved/plugins/pepflow-workflows/optional/with-clean-room/references/tool-recovery.md'))
print(p.read_text(encoding='utf-8-sig'))
