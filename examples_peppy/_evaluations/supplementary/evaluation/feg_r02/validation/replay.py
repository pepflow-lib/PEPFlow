import os,json,sys,hashlib,contextlib,traceback
from pathlib import Path
root=Path.cwd()
for key in ('TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME'):
    d=root/'review_runtime'/key.lower();d.mkdir(parents=True,exist_ok=True);os.environ[key]=str(d)
os.environ['MPLBACKEND']='Agg'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
nb=json.loads((root/'feg_example_lyap.ipynb').read_text(encoding='utf-8'))
ns={'__name__':'__main__'}
results=[]
with (root/'replay.txt').open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
    for i,c in enumerate(nb['cells']):
        if c['cell_type']!='code' or i==12:continue
        print('CELL',i,c['id'],flush=True)
        exec(compile(''.join(c['source']),f'notebook_cell_{i}','exec'),ns)
        results.append({'index':i,'id':c['id'],'passed':True})
    summary={'cells':results,'B2':ns['residuals'],'ranks':ns['ranks'],'B4':ns['component_residuals'],'step':ns['step_verified'],'base':ns['base_verified'],'boundary':ns['boundary_verified']}
    (root/'replay.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print('Replayed',len(results),'code cells, excluding plot cell. Exact identities passed.')
