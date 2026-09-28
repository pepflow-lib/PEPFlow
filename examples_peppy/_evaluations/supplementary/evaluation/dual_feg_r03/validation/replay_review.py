import os, sys, json, hashlib, contextlib, time
from pathlib import Path
root=Path.cwd().resolve()
assert root.name=='validation' and root.parent.name=='dual_feg_r03'
for key in ['TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME']:
    p=root/'review_runtime'/key.lower(); p.mkdir(parents=True,exist_ok=True); os.environ[key]=str(p)
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']: os.environ[key]='1'
sys.path[:0]=[str(root/'supplementary/approved'),str(root),str(root/'supplementary')]
nb=json.loads((root/'dual_feg_example_lyap.ipynb').read_text(encoding='utf-8'))
ns={'__name__':'__review__'}
executed=[]
with (root/'replay-output.txt').open('w',encoding='utf-8') as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
    for i,c in enumerate(nb['cells']):
        if c['cell_type']!='code' or i==12: continue
        src=''.join(c['source'])
        if i==5: src=src.replace('import matplotlib.pyplot as plt','')
        print('CELL',i,c['id'],flush=True)
        exec(compile(src,f"notebook-cell-{c['id']}",'exec'),ns)
        executed.append(c['id'])
    results={'executed_cells':executed,'omitted_plot_cell':'81a35430','certificate_N4':ns['checks'],'certificate_N6':ns['checks6'],'rank_samples':[{'N':s['N'],'rank_profile':s['rank_profile'],'coverage_residuals':s['coverage_residuals'],'singular_values':s['singular_values']} for s in ns['rank_samples']],'reconstruction_N4':ns['reconstruction'],'reconstruction_N6':ns['reconstruction6'],'exact_checks':ns['exact_checks']}
(root/'replay-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print('PASS',len(executed),'code cells; skipped only plot cell and matplotlib import')
