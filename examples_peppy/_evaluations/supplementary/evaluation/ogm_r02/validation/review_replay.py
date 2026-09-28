import os
import sys
import json
import hashlib
import contextlib
from pathlib import Path

root = Path(__file__).resolve().parent
assert Path.cwd().resolve() == root
runtime = root / 'review-runtime'
runtime.mkdir(exist_ok=True)
for key in ['TMP','TEMP','TMPDIR','MPLCONFIGDIR','IPYTHONDIR','JUPYTER_RUNTIME_DIR','XDG_CACHE_HOME']:
    os.environ[key] = str(runtime)
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[key] = '1'
os.environ['MPLBACKEND'] = 'Agg'
sys.path[:0] = [str(root/'supplementary/approved'),str(root),str(root/'supplementary')]
settings = json.loads((root.parent/'settings.json').read_text())
hashes = {name: hashlib.sha256(Path('\\\\?\\'+str(root/name)).read_bytes()).hexdigest() == value
          for name,value in settings['submission_hashes'].items()}
assert all(hashes.values()), [k for k,v in hashes.items() if not v]
nb = json.loads((root/'ogm_example_lyap.ipynb').read_text())
saved_errors = [(c['id'],o) for c in nb['cells'] for o in c.get('outputs',[]) if o.get('output_type')=='error']
assert not saved_errors
ns = {}
done = []
with (root/'review-replay-output.txt').open('w',encoding='utf-8') as out, contextlib.redirect_stdout(out):
    for c in nb['cells']:
        if c['cell_type'] != 'code':
            continue
        source = ''.join(c['source'])
        if c['id']=='b1-evidence':
            source = source.split('fig, ax =')[0]
        print('\nCELL',c['id'])
        exec(compile(source,c['id'],'exec'),ns)
        if c['id']=='b1-evidence':
            b1_max_error = ns['error']
        done.append(c['id'])
result = dict(hashes_verified=len(hashes),replayed_cells=done,
    plotting_omitted=True, saved_notebook_errors=saved_errors,
    b1_max_error=b1_max_error,b4_component_residuals=ns['component_residuals'],
    b4_quadratic_residuals=ns['coefficient_residuals'],exact_proof=ns['proof_results'])
import numpy as np
import pepflow as pf
from ogm_setup import L, get_pep_setup, theta_sequence
from b2_notebook_cells import LOAD,CANDIDATES,VERIFY
from b3_notebook_cells import DECOMPOSITION,GROUPING
result['certificates'] = []
for n in [6,8]:
    env = dict(notebook_dir=root, json=json,np=np,pf=pf,L=L,get_pep_setup=get_pep_setup,theta_sequence=theta_sequence,
        certificate_dir=root/'state' if n==6 else root/'supplementary/horizon_N8')
    with (root/f'review-N{n}-output.txt').open('w',encoding='utf-8') as out,contextlib.redirect_stdout(out):
        exec(LOAD+'\n'+CANDIDATES+'\n'+VERIFY+'\n'+DECOMPOSITION+'\n'+GROUPING,env)
    result['certificates'].append(dict(N=n,certificate_id=env['b2']['certificate_id'],
       dense_relaxed_gap=abs(env['b2']['opt_value']-env['dense']['opt_value']),
       gram_max=float(np.max(np.abs(env['gram_residual']))),function_max=float(np.max(np.abs(env['func_residual']))),
       offset_abs=abs(env['offset_residual']),min_dual=min(env['inequality_values']),
       min_eigenvalue=float(np.linalg.eigvalsh(env['S_array']).min()),
       S_reconstruction_max=float(np.max(np.abs(env['S_reconstructed']-env['S_array']))),
       rank_profile=env['ranks'],singular_values=env['singular_values'],
       coverage=env['coverage_checks'],increments=env['step_errors']))
(root/'review-replay.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
