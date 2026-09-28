import os, sys, json, hashlib, contextlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
SETTINGS=json.loads((HERE.parent/'settings.json').read_text())
NOTEBOOK_DIR=Path(SETTINGS['original_submission'])
REPO_ROOT=NOTEBOOK_DIR/'supplementary/approved'
for key in ('TEMP','TMP','TMPDIR','XDG_CACHE_HOME','MPLCONFIGDIR','IPYTHONDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','PYTHONPYCACHEPREFIX','JUPYTER_PATH'):
    loc=HERE/'runtime'/key
    loc.mkdir(parents=True,exist_ok=True)
    os.environ[key]=str(loc)
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
sys.path.insert(0,str(REPO_ROOT))
import numpy as np
import pepflow as pf
nb=json.loads((NOTEBOOK_DIR/'pgm_example_lyap.ipynb').read_text())
hash_results={p:hashlib.sha256((NOTEBOOK_DIR/p).read_bytes()).hexdigest()==h for p,h in SETTINGS['submission_hashes'].items()}
assert all(hash_results.values())
(HERE/'hash-audit.json').write_text(json.dumps(hash_results,indent=2))
cells={c['id']:''.join(c['source']) for c in nb['cells']}
selected=['d13b250e','3f7d5d27','689d6a15','555014d6','8a709058','566026a9','6fb2ff99','ccc7c313']
# These reviewed cells read only own frozen certificate/source files; all runtime state is private.
with (HERE/'numeric-replay.txt').open('w') as out,contextlib.redirect_stdout(out):
    for cell_id in selected:
        print('REPLAY CELL',cell_id,flush=True)
        exec(compile(cells[cell_id],str(HERE/('cell_'+cell_id+'.py')),'exec'),globals())
        print('PASS',cell_id,flush=True)
summary={'cells_passed':selected,'ranks':{str(v['N_int']):v['ranks'] for v in samples},'component_residuals':component_residuals,'quadratic_residuals':coefficient_residuals,'frozen_hashes_matched':len(hash_results)}
(HERE/'numeric-replay.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
