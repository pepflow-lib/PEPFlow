from pathlib import Path
import os, sys, json, hashlib, datetime
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
for key in ['TEMP','TMP','TMPDIR','MPLCONFIGDIR','IPYTHONDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME']:
    p = ROOT/'review_runtime'/key.lower()
    p.mkdir(parents=True,exist_ok=True)
    os.environ[key] = str(p)
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[key]='1'
sys.path[:0]=[str(ROOT/'supplementary/approved'),str(ROOT),str(ROOT/'supplementary/helpers')]
import runtime
notebook_dir=ROOT
nb=json.loads((ROOT/'feg_example_lyap.ipynb').read_text(encoding='utf-8'))
executed=[]
for index,cell in enumerate(nb['cells']):
    if cell['cell_type']!='code' or index==4:
        continue
    source=''.join(cell['source'])
    if index==5:
        source=source.replace('import matplotlib.pyplot as plt','')
    if index==11:
        source='\n'.join(line for line in source.splitlines() if not line.startswith('plt.'))
    print('REPLAY CELL',index,cell['id'],flush=True)
    exec(compile(source,f'notebook-cell-{index}','exec'),globals())
    executed.append(index)
summary={
 'executed_code_cells':executed,
 'changes':'Bootstrap redirected to validation copy; matplotlib import and plotting calls omitted. All mathematical code unchanged.',
 'certificate6':checks,'certificate8':checks8,
 'rank6':observation['rank_profile'],'rank8':observation8['rank_profile'],
 'coverage6':observation['maximum_coverage_residual'],'coverage8':observation8['maximum_coverage_residual'],
 'quadratic_residuals':quadratic_residuals,'full_component_residuals':component_residuals,
 'proof_checks':proof_checks,
 'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()
}
(ROOT/'replay-results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print('REPLAY COMPLETED',flush=True)
