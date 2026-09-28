import os, sys, json, math, hashlib
from pathlib import Path
from datetime import datetime, timezone
here=Path.cwd().resolve()
original=here.parents[3]/'ogm'/'r04'
assert original.name=='r04' and original.exists()
for key in ('TEMP','TMP','TMPDIR','IPYTHONDIR','MPLCONFIGDIR','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','XDG_CACHE_HOME'):
    path=here/'runtime'/key.lower(); path.mkdir(parents=True,exist_ok=True); os.environ[key]=str(path)
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[key]='1'
sys.path.insert(0,str(original/'supplementary'/'approved'))
import pepflow as pf
import numpy as np
import sympy as sp
notebook_dir=original
repo_root=original/'supplementary'/'approved'
nb=json.loads((original/'ogm_example_lyap.ipynb').read_text(encoding='utf-8'))
cells={c['id']:''.join(c['source']) for c in nb['cells']}
# Execute only inspected mathematical cells. No setup/runtime, plotting, state-writing cells.
selected_ids=['aee76fe7','154a7a38','84d342f9','a516061f','9666aaf8','d5c858e9','7fb5e03e','280011a1','a1e5f07a','b1b64787','bc666b38','f7052c78','97c543c6','6810660a','6d6d3347','508d786b','ab172f01','8068628b','80428f73','bf628750','19c974a7','745d6866','c3a8bd83','fb273c1f','896c79b8','ea620753']
for cid in selected_ids:
    print('REPLAY CELL',cid,flush=True)
    exec(compile(cells[cid],f'ogm_example_lyap.ipynb#{cid}','exec'),globals())
report={'method':'Fresh isolated Python process replay of inspected mathematical notebook cells; solver acquisition, plotting, state writes and notebook kernel delivery inspected only','cells':selected_ids,'B2':residuals,'B3_N4':{'ranks':ranks,'coverage':coverage_residuals,'singular_values':singular_values},'B4':{'quadratic_residuals':coefficient_residuals,'component_residuals':component_residuals},'B5':exact_results}
# Replay the identical submitted B3 check/decomposition/grouping against its own N6 certificate.
certificate=json.loads((original/'supplementary/b2-N6-verified.json').read_text())
N_int=certificate['N_verify']
params_sp={k:sp.S(v) for k,v in json.loads(certificate['params_json']).items()}
ctx,pb,obj=get_pep_setup(N_int,params_sp)
pb.set_relaxed_constraints(certificate['relaxed_constraints']);ctx.set_as_current()
for cid in ['280011a1','a1e5f07a','b1b64787']: exec(compile(cells[cid],f'ogm_example_lyap.ipynb#{cid}:N6','exec'),globals())
report['B3_N6']={'ranks':ranks,'coverage':coverage_residuals,'singular_values':singular_values}
report['finished_utc']=datetime.now(timezone.utc).isoformat()
(here/'replay-results.json').write_text(json.dumps(report,indent=2))
print('REPLAY COMPLETE',report['finished_utc'])
