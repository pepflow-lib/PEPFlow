import json,os
from pathlib import Path
root=Path.cwd()
for key in ('TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME'):
 p=root/'runtime'/key.lower();p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
nb=json.loads((root/'dual_feg_example_lyap.ipynb').read_text(encoding='utf-8'))
ns={'__name__':'__main__'}
executed=[]
for cell in nb['cells']:
 if cell['cell_type']!='code':continue
 if cell['id']=='9b7030aa':continue
 source=''.join(cell['source'])
 print('REPLAY CELL',cell['id'],flush=True)
 exec(compile(source,cell['id'],'exec'),ns)
 if 'pf' in ns:ns['pf'].pprint_labeled_matrix=lambda *a,**kw:None
 executed.append(cell['id'])
result={'executed_cells':executed,'skipped_plot_cell':'9b7030aa','proof_checks':ns['proof_checks'],'B2':ns['residuals'],'B2_N8':ns['checks8'],'B3':ns['coverage_residuals'],'B4':ns['component_residuals']}
(root/'replay-results.json').write_text(json.dumps(result,indent=2))
print('ALL REPLAYED CHECKS PASSED')
