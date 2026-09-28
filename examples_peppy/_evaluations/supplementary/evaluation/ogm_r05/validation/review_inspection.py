import json,hashlib
from pathlib import Path
r=Path.cwd(); settings=json.loads((r.parent/'settings.json').read_text()); original=Path(settings['original_submission'])
mismatches=[name for name,h in settings['submission_hashes'].items() if hashlib.sha256((original/name).read_bytes()).hexdigest()!=h]
assert not mismatches,mismatches
nb=json.loads((original/'ogm_example_lyap.ipynb').read_text())
code=[c for c in nb['cells'] if c['cell_type']=='code']
plots=sum('image/png' in o.get('data',{}) for c in code for o in c.get('outputs',[]))
static=json.loads((original/'supplementary/b5-static-004.json').read_text())
checks=[{'tool':Path(c['command'][0]).name,'returncode':c['returncode'],'stdout':c['stdout']} for c in static['commands'] if 'check' in c['command'] and any('source' in a for a in c['command'])]
sweep=json.loads((original/'supplementary/b1_sweep.json').read_text())
report={'hash_count':len(settings['submission_hashes']),'hash_mismatches':mismatches,'code_cells':len(code),'execution_counts':[c['execution_count'] for c in code],'error_outputs':sum(o['output_type']=='error' for c in code for o in c.get('outputs',[])),'embedded_plot_count':plots,'static_source_checks':checks,'sweep_max_rate_error':max(abs(x['opt_value']-1/(2*x['theta_N']**2)) for x in sweep)}
(r/'review-inspection.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
