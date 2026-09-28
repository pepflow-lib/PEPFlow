import json,hashlib,datetime
from pathlib import Path
root=Path.cwd(); review=root.parent
settings=json.loads((review/'settings.json').read_text(encoding='utf-8-sig'))
original=Path(settings['original_submission'])
mismatch=[r for r,h in settings['submission_hashes'].items() if hashlib.sha256((original/r).read_bytes()).hexdigest()!=h]
nb=json.loads((root/'bppm_example_lyap.ipynb').read_text())
static=json.loads((root/'supplementary/b5-static-002.json').read_text())
summary={'hashes_checked':len(settings['submission_hashes']),'hash_mismatches':mismatch,'saved_execution_counts':[c['execution_count'] for c in nb['cells'] if c['cell_type']=='code'],'saved_error_outputs':[c['id'] for c in nb['cells'] for o in c.get('outputs',[]) if o['output_type']=='error'],'source_static_checks':[{'label':c['label'],'returncode':c['returncode'],'stdout':c['stdout']} for c in static['commands'] if c['label'] in ('source_ruff','source_ty')],'sweep':json.loads((root/'supplementary/b1-sweep.json').read_text()),'audit_scope':'Frozen artifact hash verification; notebook output metadata; inspected saved static/preflight/clean-kernel logs and source/access declarations; bounded host-call screening. No exhaustive OS access tracing.'}
(root/'review-artifact-audit.json').write_text(json.dumps(summary,indent=2))
print('Hash count',summary['hashes_checked'],'mismatches',mismatch)
