import os,json,sys,contextlib,hashlib
from pathlib import Path
root=Path.cwd()
for key in ('TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME'):
 d=root/'review_runtime'/key.lower();d.mkdir(parents=True,exist_ok=True);os.environ[key]=str(d)
os.environ['MPLBACKEND']='Agg'
nb=json.loads((root/'feg_example_lyap.ipynb').read_text(encoding='utf-8'));ns={'__name__':'__main__'}
with (root/'n8-replay.txt').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log):
 for i in (4,5,7,9):exec(''.join(nb['cells'][i]['source']),ns)
 exec("certificate=json.loads((notebook_dir/'supplementary/N8/feg_b2.json').read_text()); REPO_ROOT=repo_root; N_int=8; params_sp={'L':sp.Integer(1),'R':sp.Integer(1)}; ctx,pb,obj=get_pep_setup(N_int,params_sp);pb.set_relaxed_constraints(certificate['relaxed_constraints']);ctx.set_as_current()",ns)
 for i in (25,26,27):exec(''.join(nb['cells'][i]['source']),ns)
 spectra=ns['singular_values'][1:-1]
 summary={'N':8,'certificate_checked':ns['certificate_checked'],'coverage':ns['coverage_residuals'],'ranks':ns['ranks'],'smallest_retained_singular_value':min(s[1] for s in spectra),'largest_discarded_singular_value':max(s[2] for s in spectra)}
 (root/'n8-replay.json').write_text(json.dumps(summary,indent=2))
settings=json.loads((root.parent/'settings.json').read_text());original=Path(settings['original_submission']);mismatch=[]
for rel,sha in settings['submission_hashes'].items():
 if hashlib.sha256((original/rel).read_bytes()).hexdigest()!=sha:mismatch.append(rel)
(root/'hash-check.json').write_text(json.dumps({'checked_files':len(settings['submission_hashes']),'mismatches':mismatch},indent=2))
print(json.dumps(summary));print('Hash mismatches:',mismatch)
