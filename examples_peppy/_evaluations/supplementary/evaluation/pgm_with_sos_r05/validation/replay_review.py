from pathlib import Path
import os, sys, json, hashlib, contextlib
root=Path.cwd().resolve()
assert root.name=='validation' and root.parent.name=='pgm_with_sos_r05'
for key in ['TEMP','TMP','TMPDIR','XDG_CACHE_HOME','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR']:
    p=root/'review_runtime'/key;p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
os.environ['MPLBACKEND']='Agg'
sys.path[:0]=[str(root/'supplementary'/'approved'),str(root),str(root/'supplementary')]
nb=json.loads((root/'pgm_example_lyap.ipynb').read_text(encoding='utf-8'))
original=root.parents[3]/'pgm_with_sos'/'r05'
ns={'notebook_dir':root,'repo_root':root/'supplementary'/'approved','original':original,'Path':Path,'json':json}
def adapt(src):
    return src.replace('assert source_path.is_relative_to(notebook_dir)','assert source_path.is_relative_to(original)')
def cell(i):
    print('REPLAY CELL',i,nb['cells'][i]['id'],flush=True)
    exec(compile(adapt(''.join(nb['cells'][i]['source'])),f'cell-{i}','exec'),ns)
with (root/'review_replay.txt').open('w',encoding='utf-8') as out,contextlib.redirect_stdout(out):
    for i in [5,6,7,12,14,16,18]:cell(i)
    numerical=ns['residuals'].copy()
    rank_results=[]
    for horizon,rel in [(4,'state/pgm_b2.json'),(6,'supplementary/N6/pgm_b2.json')]:
        ns['certificate']=json.loads((root/rel).read_text())
        cell(24)
        rank_results.append({k:ns[k] for k in ['N_int','ranks','singular_values','rank_credible','certificate_residuals','coverage_residuals','increment_residuals','piece_residuals','polar_reconstruction']})
    ns['certificate']=json.loads((root/'state/pgm_b2.json').read_text());cell(24)
    exec('from pepflow.lyapunov_utils import find_symmetric_coefficient_matrix',ns)
    for i in [35,37,38]:cell(i)
    reconstruction=ns['component_residuals'].copy()
    for i in [42,44,46,50,53,56,59,62]:cell(i)
    result={'numerical':numerical,'ranks':rank_results,'reconstruction':reconstruction,'proof_checks':ns['proof_checks'],'multiplier_identities':ns['multiplier_identities'],'adaptation':'Only provenance scope assertion admits original read-only source hashes; replay uses approved validation package. No solves or rendering; selected notebook cells executed in fresh Python process.'}
    (root/'review_replay.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
print('Replay completed')
