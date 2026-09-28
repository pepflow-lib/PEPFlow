import hashlib
import json
from pathlib import Path

root=Path.cwd().resolve()
review=root.parent
settings=json.loads((review/'settings.json').read_text(encoding='utf-8-sig'))
original=Path(settings['original_submission'])
hash_failures=[]
for relative,expected in settings['submission_hashes'].items():
    path=original/relative
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual!=expected:
        hash_failures.append(relative)
nb=json.loads((original/'feg_example_lyap.ipynb').read_text(encoding='utf-8'))
code=[c for c in nb['cells'] if c['cell_type']=='code']
static=json.loads((original/'supplementary/b5-static-002.json').read_text(encoding='utf-8-sig'))
checklist=(original/'supplementary/feg_example_lyap_checklist.md').read_text(encoding='utf-8')
result={'hash_count':len(settings['submission_hashes']),'hash_failures':hash_failures,
 'notebook_sha256':hashlib.sha256((original/'feg_example_lyap.ipynb').read_bytes()).hexdigest(),
 'code_cells':len(code),'execution_counts':[c['execution_count'] for c in code],
 'error_outputs':sum(o['output_type']=='error' for c in code for o in c.get('outputs',[])),
 'plot_output_present':any('image/png' in o.get('data',{}) for c in code for o in c.get('outputs',[])),
 'static_commands':[{'label':c['label'],'returncode':c['returncode'],'stdout':c['stdout']} for c in static['commands'] if c['label'] in ('source_ruff','source_ty','clean_kernel_import_probe')],
 'checklist_hash_matches':settings['submission_hashes']['feg_example_lyap.ipynb'] in checklist,
 'certificates':{}}
for n,folder in ((6,original/'state'),(4,original/'supplementary/sample-N4')):
    b2=json.loads((folder/'feg_b2.json').read_text())
    dense=json.loads((folder/'feg_dense.json').read_text())
    result['certificates'][str(n)]={'certificate_id':b2['certificate_id'],'objective':b2['opt_value'],'dense_objective':dense['opt_value'],'dense_relaxed_gap':abs(b2['opt_value']-dense['opt_value']),'numerical_checks':b2['numerical_checks']}
rank=json.loads((original/'supplementary/rank_search.json').read_text())
result['rank_summary']=rank['summary']
result['rank_margins']=[]
for sample in rank['samples']:
    singular=sample.get('singular_values')
    result['rank_margins'].append({'N':sample['N'],'keys':list(sample),'singular_values':singular})
assert not hash_failures and result['error_outputs']==0 and result['checklist_hash_matches']
assert result['execution_counts']==list(range(1,len(code)+1))
(root/'review-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
