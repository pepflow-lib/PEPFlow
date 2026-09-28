import os,json,sys,contextlib,datetime
from pathlib import Path
root=Path.cwd().resolve()
cache=root/'review_runtime'
for name in ('TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME'):
 p=cache/name.lower(); p.mkdir(parents=True,exist_ok=True); os.environ[name]=str(p)
os.environ['MPLBACKEND']='Agg'
nb=json.loads((root/'bppm_example_lyap.ipynb').read_text(encoding='utf-8'))
scope={'__name__':'__main__'}
executed=[]
with (root/'review-replay.log').open('w',encoding='utf-8') as out,contextlib.redirect_stdout(out):
 for i,c in enumerate(nb['cells']):
  if c['cell_type']!='code' or i==11: continue
  print('REPLAY CELL',i,c['id'],flush=True)
  exec(compile(''.join(c['source']),c['id'],'exec'),scope)
  executed.append(c['id'])
 summary={'executed_cell_ids':executed,'N4_certificate_residuals':scope['residuals'],'N4_coverage_residuals':scope['coverage_residuals'],'N4_ranks':scope['ranks'],'B4_component_residuals':scope['component_residuals'],'exact_identity_evidence':scope['exact_identity_evidence'],'proof_checks':scope['proof_checks']}
 # Reuse the inspected same notebook certificate and grouping checks on the second submitted certificate.
 scope['certificate']=json.loads((root/'supplementary/N6/certificate.json').read_text())
 scope['N_int']=6
 scope['params_sp']={'alpha':scope['sp'].S(1),'R':scope['sp'].S(1)}
 scope['ctx'],scope['pb'],scope['obj']=scope['get_pep_setup'](6,scope['params_sp'])
 scope['pb'].set_relaxed_constraints(scope['certificate']['relaxed_constraints'])
 scope['ctx'].set_as_current()
 for i in (18,19,20): exec(compile(''.join(nb['cells'][i]['source']),nb['cells'][i]['id'],'exec'),scope)
 summary['N6_ranks']=scope['ranks'];summary['N6_coverage_residuals']=scope['coverage_residuals']
 summary['N6_certificate_verified']=scope['certificate_checked']
 summary['stopped_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(root/'review-replay.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
